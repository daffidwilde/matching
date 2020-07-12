""" The SA solver and algorithm. """
import copy
import warnings

from matching import Matching
from matching import Player as Student
from matching.exceptions import (
    CapacityChangedWarning,
    MatchingError,
    PlayerExcludedWarning,
    PreferencesChangedWarning,
)
from matching.games import HospitalResident
from matching.players import Project, Supervisor

from .util import delete_pair, match_pair


class StudentAllocation(HospitalResident):
    """ A class for solving instances of the student-allocation problem (SA)
    using an adapted Gale-Shapley algorithm.

    In this case, a blocking pair is defined as any student-project pair that
    satisfies **all** of the following:
    
    1. The student has a preference of the project.
    2. Either the student is unmatched, or they prefer the project to their
       current project.
    3. At least one of the following: 
    
       - The project or its supervisor is under-subscribed.
       - The project is under-subscribed and the supervisor is at capacity, and
         the student is matched to a project offered by the supervisor or the
         supervisor prefers the student to its worst currently matched student.
       - The project is at capacity and its supervisor prefers the student to
         its worst currently matched student.

    Parameters
    ----------
    students : list of Player
        The students in the game. Each student must rank a subset of the
        projects.
    projects : list of Project
        The projects in the game. Each project has a supervisor associated
        with it that governs its preferences.
    supervisors : list of Supervisor
        The supervisors in the game. Each supervisor oversees a unique subset
        of ``projects`` and ranks all of those students that have ranked at
        least one of its projects.

    Attributes
    ----------
    matching : Matching or None
        Once the game is solved, a matching is available. This ``Matching``
        object behaves much like a dictionary that uses the elements of
        ``projects`` as keys and their student matches as values. Initialises as
        ``None``.
    blocking_pairs : list of (Player, Project)
        Initialises as None. Otherwise, a list of the student-project blocking
        pairs.
    """

    def __init__(self, students, projects, supervisors):

        students, projects, supervisors = copy.deepcopy(
            [students, projects, supervisors]
        )
        self.students = students
        self.projects = projects
        self.supervisors = supervisors

        self._all_students = students
        self._all_projects = projects
        self._all_supervisors = supervisors

        super().__init__(students, projects)
        self._check_inputs()

    def _remove_player(self, player, player_party, other_party=None):
        """ Remove players from the game normally unless the player is a
        supervisor. """

        if player_party == "supervisors":
            self.supervisors.remove(player)
            for project in player.projects:
                try:
                    super()._remove_player(project, "projects", "students")
                except ValueError:
                    pass

        else:
            super()._remove_player(player, player_party, other_party)

    @classmethod
    def create_from_dictionaries(
        cls,
        student_prefs,
        supervisor_prefs,
        project_supervisors,
        project_capacities,
        supervisor_capacities,
    ):
        """ Create an instance of SA from two preference dictionaries,
        affiliations and capacities. """

        students, projects, supervisors = _make_players(
            student_prefs,
            supervisor_prefs,
            project_supervisors,
            project_capacities,
            supervisor_capacities,
        )
        game = cls(students, projects, supervisors)

        return game

    def solve(self, optimal="student"):
        """ Solve the instance of SA using either the student- or
        supervisor-optimal algorithm. """

        self.matching = Matching(
            student_allocation(
                self.students, self.projects, self.supervisors, optimal
            )
        )
        return self.matching

    def check_validity(self):
        """ Check whether the current matching is valid. Raise a `MatchingError`
        detailing the issues if not. """

        unacceptable_issues = (
            self._check_for_unacceptable_matches("students")
            + self._check_for_unacceptable_matches("projects")
            + self._check_for_unacceptable_matches("supervisors")
        )

        oversubscribed_issues = self._check_for_oversubscribed_players(
            "projects"
        ) + self._check_for_oversubscribed_players("supervisors")

        if unacceptable_issues or oversubscribed_issues:
            raise MatchingError(
                unacceptable_matches=unacceptable_issues,
                oversubscribed_players=oversubscribed_issues,
            )

        return True

    def check_stability(self):
        """ Check for the existence of any blocking pairs in the current
        matching, thus determining the stability of the matching. """

        blocking_pairs = []
        for student in self.students:
            for project in self.projects:
                if (
                    project in student.prefs
                    and _check_student_unhappy(student, project)
                    and _check_project_unhappy(project, student)
                ):
                    blocking_pairs.append((student, project))

        self.blocking_pairs = blocking_pairs
        return not any(blocking_pairs)

    def _check_inputs(self):
        """ Check that the players in the game have valid preferences, and in
        the case of projects and supervisor: capacities. """

        self._check_student_prefs_all_projects()
        self._check_student_prefs_all_nonempty()

        self._check_project_prefs_all_reciprocated()
        self._check_project_reciprocates_all_prefs()
        self._check_project_prefs_all_nonempty()

        self._check_supervisor_prefs_all_reciprocated()
        self._check_supervisor_reciprocates_all_prefs()
        self._check_supervisor_prefs_all_nonempty()

        self._check_init_project_capacities_positive()
        self._check_init_supervisor_capacities_positive()
        self._check_init_supervisor_capacities_sufficient()
        self._check_init_supervisor_capacities_necessary()

    def _check_student_prefs_all_projects(self):
        """ Make sure that each student has ranked only projects. """

        for student in self.students:

            for project in student.prefs:
                if project not in self.projects:
                    warnings.warn(
                        PreferencesChangedWarning(
                            f"{student} has ranked a non-project: {project}."
                        )
                    )

                    student.forget(project)

    def _check_student_prefs_all_nonempty(self):
        """ Make sure that each student has a nonempty preference list. """

        for student in self.students:

            if not student.prefs:
                warnings.warn(
                    PlayerExcludedWarning(
                        f"{student} has an empty preference list."
                    )
                )

                self._remove_player(student, "students", "supervisors")

    def _check_project_prefs_all_reciprocated(self):
        """ Make sure that each project has ranked only those students that
        have ranked it. """

        for project in self.projects:

            for student in project.prefs:
                if project not in student.prefs:
                    warnings.warn(
                        PreferencesChangedWarning(
                            f"{project} ranked {student} but they did not. "
                            f"Removing {student} from {project} preferences."
                        )
                    )

                    project.forget(student)

    def _check_project_reciprocates_all_prefs(self):
        """ Make sure that each project has ranked all those students that
        have ranked it. """

        for project in self.projects:

            students_that_ranked = [
                res for res in self.students if project in res.prefs
            ]
            for student in students_that_ranked:
                if student not in project.prefs:
                    warnings.warn(
                        PreferencesChangedWarning(
                            f"{student} ranked {project} but they did not. "
                            f"Removing {project} from {student} preferences."
                        )
                    )

                    student.forget(project)

    def _check_project_prefs_all_nonempty(self):
        """ Make sure that each project has a non-empty preference list. """

        for project in self.projects:
            if not project.prefs:
                warnings.warn(
                    PlayerExcludedWarning(
                        f"{project} has an empty preference list."
                    )
                )

                self._remove_player(project, "projects", "students")

    def _check_supervisor_prefs_all_reciprocated(self):
        """ Make sure that each supervisor has ranked only those students that
        have ranked at least one of their projects. """

        for supervisor in self.supervisors:

            for student in supervisor.prefs:
                student_prefs_supervisors = {
                    p.supervisor for p in student.prefs
                }
                if supervisor not in student_prefs_supervisors:
                    warnings.warn(
                        PreferencesChangedWarning(
                            f"{supervisor} ranked {student} but they have not "
                            "ranked one of their projects."
                        )
                    )

                    supervisor.forget(student)

    def _check_supervisor_reciprocates_all_prefs(self):
        """ Make sure that each supervisor has ranked all those students that
        have ranked at least one of its projects. """

        for supervisor in self.supervisors:

            students_that_ranked = [
                student
                for student in self.students
                if any(
                    [
                        project in student.prefs
                        for project in supervisor.projects
                    ]
                )
            ]
            for student in students_that_ranked:
                if student not in supervisor.prefs:
                    warnings.warn(
                        PreferencesChangedWarning(
                            f"{student} ranked a project provided by "
                            f"{supervisor} but they did not."
                        )
                    )

                    for project in student.prefs:
                        if project.supervisor == supervisor:
                            warnings.warn(
                                PreferencesChangedWarning(
                                    f"{student} ranked {project} but its "
                                    "supervisor did not."
                                )
                            )

                            student.forget(project)

    def _check_supervisor_prefs_all_nonempty(self):
        """ Make sure that every supervisor has a non-empty preference list. """

        for supervisor in self.supervisors:
            if not supervisor.prefs:
                warnings.warn(
                    PlayerExcludedWarning(
                        f"{supervisor} has an empty preference list."
                    )
                )

                for project in supervisor.projects:
                    warnings.warn(
                        PlayerExcludedWarning(
                            f"{project} supervisor no longer in game."
                        )
                    )

                self._remove_player(supervisor, "supervisors")

    def _check_init_project_capacities_positive(self):
        """ Check that each project has at least one space. """

        for project in self.projects:

            supervisor = project.supervisor
            if project.capacity < 1:
                warnings.warn(
                    PlayerExcludedWarning(
                        f"{project} does not have a positive capacity."
                    )
                )

                self._remove_player(project, "projects", "students")

    def _check_init_supervisor_capacities_positive(self):
        """ Check that each supervisor has at least one space. """

        for supervisor in self.supervisors:

            if supervisor.capacity < 1:
                warnings.warn(
                    PlayerExcludedWarning(
                        f"{supervisor} does not have a positive capacity."
                    )
                )

                for project in supervisor.projects:
                    warnings.warn(
                        PlayerExcludedWarning(
                            f"{project} supervisor no longer in game."
                        )
                    )

                self._remove_player(supervisor, "supervisors")

    def _check_init_supervisor_capacities_sufficient(self):
        """ Check that each supervisor has the capacity to support its largest
        project(s). """

        for supervisor in self.supervisors:

            for project in supervisor.projects:
                if project.capacity > supervisor.capacity:
                    warnings.warn(
                        CapacityChangedWarning(
                            f"{project} has a capacity of {project.capacity} "
                            "but its supervisor has a capacity of "
                            f"{supervisor.capacity}."
                        )
                    )

                    project.capacity = supervisor.capacity

    def _check_init_supervisor_capacities_necessary(self):
        """ Check that each supervisor has at most the necessary capacity for
        all of their projects. """

        for supervisor in self.supervisors:

            total_project_capacity = sum(
                p.capacity for p in supervisor.projects
            )

            if supervisor.capacity > total_project_capacity:
                warnings.warn(
                    CapacityChangedWarning(
                        f"{supervisor} has a capacity of {supervisor.capacity} "
                        "but their projects have a capacity of "
                        f"{total_project_capacity}"
                    )
                )

                supervisor.capacity = total_project_capacity


def _check_student_unhappy(student, project):
    """ Determine whether ``student`` is unhappy either because they are
    unmatched or because they prefer ``project`` to their current matching. """

    return student.matching is None or student.prefers(
        project, student.matching
    )


def _check_project_unhappy(project, student):
    """ Determine whether ``project`` is unhappy because either:
        - they and their supervisor are under-subscribed;
        - they are under-subscribed, their supervisor is full, and either
          ``student`` is in the supervisor's matching or the supervisor prefers
          ``student`` to their worst current matching;
        - ``project`` is full and their supervisor prefers ``student`` to the
          worst student in the matching of ``project``.
    """

    supervisor = project.supervisor

    project_undersubscribed = len(project.matching) < project.capacity
    both_undersubscribed = (
        project_undersubscribed
        and len(supervisor.matching) < supervisor.capacity
    )

    supervisor_full = len(supervisor.matching) == supervisor.capacity

    swap_available = (
        student in supervisor.matching and student.matching != project
    ) or supervisor.prefers(student, supervisor.get_worst_match())

    project_upsetting_supervisor = len(
        project.matching
    ) == project.capacity and supervisor.prefers(
        student, project.get_worst_match()
    )

    return (
        both_undersubscribed
        or (project_undersubscribed and supervisor_full and swap_available)
        or project_upsetting_supervisor
    )


def unmatch_pair(student, project):
    """ Unmatch a student-project pair. """

    student.unmatch()
    project.unmatch(student)


def student_allocation(students, projects, supervisors, optimal="student"):
    """ Solve an instance of SA by treating it as a bi-level HR. A unique,
    stable and optimal matching is found for the given set of students, projects
    and supervisors. The optimality of the matching is found with respect to one
    party and is subsequently the worst stable matching for the other.

    Parameters
    ----------
    students : list of Player
        The students in the game. Each student must rank a subset of the
        elements of ``projects``.
    projects : list of Project
        The projects in the game. Each project is offered by a supervisor that
        governs its preferences.
    supervisor : list of Supervisor
        The supervisors in the game. Each supervisor offers a unique subset of
        ``projects`` and ranks all the students that have ranked at least one of
        these projects.
    optimal : str, optional
        Which party the matching should be optimised for. Must be one of
        ``"student"`` and ``"supervisor"``. Defaults to the former.

    Returns
    =======
    matching : Matching
        A dictionary-like object where the keys are the members of ``projects``
        and their student matches are the values.
    """

    if optimal == "student":
        return student_optimal(students, projects)
    if optimal == "supervisor":
        return supervisor_optimal(projects, supervisors)


def student_optimal(students, projects):
    """ Solve the instance of SA to be student-optimal. The algorithm is as
    follows:

        0. Set all students to be unassigned, and every project (and supervisor)
        to be totally unsubscribed.

        1. Take any student, :math:`s`, that is unassigned and has a non-empty
        preference list, and consider their most preferred project, :math:`p`.
        Let :math:`f` denote the supervisor that offers :math:`p`. Assign
        :math:`s` to be matched to :math:`p` (and thus :math:`f`).

        2. If :math:`p` is now over-subscribed, find its worst current match,
        :math:`s'`. Unmatch :math:`p` and :math:`s'`. Else if :math:`f` is
        over-subscribed, find their worst current match, :math:`s''`, and the
        project they are currently subscribed to, :math:`p'`. Unmatch :math:`p'`
        and :math:`s''`.

        3. If :math:`p` is now at capacity, find their worst current match,
        :math:`s'`. For each successor, :math:`t`, to :math:`s'` in the
        preference list of :math:`p`, delete the pair :math:`(p, t)` from the
        game.

        4. If :math:`f` is at capacity, find their worst current match,
        :math:`s'`. For each successor, :math:`t`, to :math:`s'` in the
        preference list of :math:`f`, for each project, :math:`p'`, offered by
        :math:`f` that :math:`t` finds acceptable, delete the pair
        :math:`(p', t)` from the game.

        5. Go to 1 until there are no such students left, then end.
    """

    free_students = students[:]
    while free_students:

        student = free_students.pop()
        project = student.get_favourite()
        supervisor = project.supervisor

        match_pair(student, project)

        if len(project.matching) > project.capacity:
            worst = project.get_worst_match()
            unmatch_pair(worst, project)
            free_students.append(worst)

        elif len(supervisor.matching) > supervisor.capacity:
            worst = supervisor.get_worst_match()
            worst_project = worst.matching
            unmatch_pair(worst, worst_project)
            free_students.append(worst)

        if len(project.matching) == project.capacity:
            successors = project.get_successors()
            for successor in successors:
                delete_pair(project, successor)
                if not successor.prefs:
                    free_students.remove(successor)

        if len(supervisor.matching) == supervisor.capacity:
            successors = supervisor.get_successors()
            for successor in successors:

                supervisor_projects = [
                    project
                    for project in supervisor.projects
                    if project in successor.prefs
                ]

                for project in supervisor_projects:
                    delete_pair(project, successor)
                if not successor.prefs:
                    free_students.remove(successor)

    return {p: p.matching for p in projects}


def supervisor_optimal(projects, supervisors):
    """ Solve the instance of SA to be supervisor-optimal. The algorithm is as
    follows:

        0. Set all students to be unassigned, and every project (and supervisor)
        to be totally unsubscribed.

        1. Take any supervisor member, :math:`f`, that is under-subscribed and
        whose preference list contains at least one student that is not
        currently matched to at least one acceptable (though currently
        under-subscribed) project offered by :math:`f`. Consider the
        supervisor's most preferred such student, :math:`s`, and that student's
        most preferred such project, :math:`p`.

        2. If :math:`s` is matched to some other project, :math:`p'`, then
        unmatch them. In any case, match :math:`s` and :math:`p` (and thus
        :math:`f`).

        3. For each successor, :math:`p'`, to :math:`p` in the preference list
        of :math:`s`, delete the pair :math:`(p', s)` from the game.

        4. Go to 1 until there are no such supervisors, then end.
    """

    free_supervisors = supervisors[:]
    while free_supervisors:

        supervisor = free_supervisors.pop()
        student, project = supervisor.get_favourite()

        if student.matching:
            curr_match = student.matching
            unmatch_pair(student, curr_match)

        match_pair(student, project)

        successors = student.get_successors()
        for successor in successors:
            delete_pair(student, successor)

        free_supervisors = [
            supervisor
            for supervisor in supervisors
            if supervisor.get_favourite() is not None
        ]

    return {p: p.matching for p in projects}


def _make_players(
    student_prefs,
    supervisor_prefs,
    project_supervisors,
    project_capacities,
    supervisor_capacities,
):
    """ Make a set of ``Player``, ``Project`` and ``Supervisor`` instances,
    respectively for the students, projects and supervisors from the
    dictionaries given, and add their preferences. """

    student_dict, project_dict, supervisor_dict = _make_instances(
        student_prefs,
        project_supervisors,
        project_capacities,
        supervisor_capacities,
    )

    for name, student in student_dict.items():
        prefs = [project_dict[project] for project in student_prefs[name]]
        student.set_prefs(prefs)

    for name, supervisor in supervisor_dict.items():
        prefs = [student_dict[student] for student in supervisor_prefs[name]]
        supervisor.set_prefs(prefs)

    students = list(student_dict.values())
    projects = list(project_dict.values())
    supervisors = list(supervisor_dict.values())

    return students, projects, supervisors


def _make_instances(
    student_prefs,
    project_supervisors,
    project_capacities,
    supervisor_capacities,
):
    """ Create ``Player``, ``Project`` and ``Supervisor`` instances for the
    names in each dictionary. """

    student_dict, project_dict, supervisor_dict = {}, {}, {}

    for student_name in student_prefs:
        student = Student(name=student_name)
        student_dict[student_name] = student

    for project_name, supervisor_name in project_supervisors.items():
        capacity = project_capacities[project_name]
        project = Project(name=project_name, capacity=capacity)
        project_dict[project_name] = project

    for supervisor_name, capacity in supervisor_capacities.items():
        supervisor = Supervisor(name=supervisor_name, capacity=capacity)
        supervisor_dict[supervisor_name] = supervisor

    for project_name, supervisor_name in project_supervisors.items():
        project = project_dict[project_name]
        supervisor = supervisor_dict[supervisor_name]
        project.set_supervisor(supervisor)

    return student_dict, project_dict, supervisor_dict
