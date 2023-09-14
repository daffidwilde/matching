"""The SA game class and supporting functions."""

import copy
import warnings

from matching import MultipleMatching
from matching import Player as Student
from matching.algorithms import student_allocation
from matching.exceptions import (
    CapacityChangedWarning,
    MatchingError,
    PreferencesChangedWarning,
)
from matching.games import HospitalResident
from matching.players import Project, Supervisor


class StudentAllocation(HospitalResident):
    """Solver for the student-allocation problem (SA).

    In SA, a blocking pair is defined as any student-project pair that
    satisfies **all** of the following:

    1. The student has a preference of the project.
    2. Either the student is unmatched, or they prefer the project to
       their current project.
    3. At least one of the following:

       - The project or its supervisor is under-subscribed.
       - The project is under-subscribed and the supervisor is at
         capacity, and the student is matched to a project offered by
         the supervisor or the supervisor prefers the student to its
         worst currently matched student.
       - The project is at capacity and its supervisor prefers the
         student to its worst currently matched student.

    Parameters
    ----------
    students : list of Player
        The students in the game. Each student must rank a subset of the
        projects.
    projects : list of Project
        The projects in the game. Each project has a supervisor
        associated with it that governs its preferences.
    supervisors : list of Supervisor
        The supervisors in the game. Each supervisor oversees a unique
        subset of ``projects`` and ranks all of those students that have
        ranked at least one of its projects.
    clean : bool
        An indicator as to whether the players passed to the game should
        be cleaned in a reductive fashion. Defaults to ``False``.

    Attributes
    ----------
    matching : MultipleMatching or None
        Once the game is solved, a matching is available. This
        ``MultipleMatching`` object behaves much like a dictionary that
        uses the elements of ``projects`` as keys and their student
        matches as values. Initialises as ``None``.
    blocking_pairs : list of (Player, Project)
        Initialises as ``None``. Otherwise, a list of the
        student-project blocking pairs.
    """

    def __init__(self, students, projects, supervisors, clean=False):
        students, projects, supervisors = copy.deepcopy(
            [students, projects, supervisors]
        )
        self.students = students
        self.projects = projects
        self.supervisors = supervisors

        self._all_students = students
        self._all_projects = projects
        self._all_supervisors = supervisors

        self.clean = clean

        super().__init__(students, projects, clean)
        self.check_inputs()

    def _remove_player(self, player, player_party, other_party=None):
        """Remove a player from the game.

        If the player is a supervisor, we must also remove all their
        projects.
        """

        if player_party == "supervisors":
            self.supervisors.remove(player)
            for project in player.projects:
                super()._remove_player(project, "projects", "students")

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
        clean=False,
    ):
        """Create an instance of SA from a set of dictionaries.

        SA requires preference dictionaries for students and
        supervisors, a project-supervisor affiliation dictionary, and
        a capacity dictionary for both the projects and supervisors.
        """

        students, projects, supervisors = _make_players(
            student_prefs,
            supervisor_prefs,
            project_supervisors,
            project_capacities,
            supervisor_capacities,
        )
        game = cls(students, projects, supervisors, clean)

        return game

    def solve(self, optimal="student"):
        """Solve the instance of SA.

        Party optimality can be controlled using the ``optimal``
        parameter. Solutions can either be student-optimal or
        supervisor-optimal.
        """

        self.matching = MultipleMatching(
            student_allocation(
                self.students, self.projects, self.supervisors, optimal
            )
        )
        return self.matching

    def check_validity(self):
        """Check whether the current matching is valid."""

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
        """Check for the existence of any blocking pairs."""

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

    def check_inputs(self):
        """Check if any rules of the game have been broken.

        Any violations will be flagged as warnings. If the ``clean``
        attribute is in use, then any violations will be removed.
        """

        self._check_inputs_player_prefs_unique("students")
        self._check_inputs_player_prefs_unique("projects")
        self._check_inputs_player_prefs_unique("supervisors")

        self._check_inputs_player_prefs_all_in_party("students", "projects")
        self._check_inputs_player_prefs_nonempty("students", "projects")

        self._check_inputs_player_prefs_all_in_party("supervisors", "students")
        self._check_inputs_player_prefs_nonempty("supervisors", "students")

        self._check_inputs_player_prefs_all_reciprocated("projects")
        self._check_inputs_player_reciprocated_all_prefs(
            "projects", "students"
        )
        self._check_inputs_player_prefs_nonempty("projects", "students")

        self._check_inputs_player_prefs_all_reciprocated("supervisors")
        self._check_inputs_player_reciprocated_all_prefs(
            "supervisors", "students"
        )
        self._check_inputs_player_prefs_nonempty("supervisors", "students")

        self._check_inputs_player_capacity("projects", "students")
        self._check_inputs_player_capacity("supervisors", "students")
        self._check_inputs_supervisor_capacities_sufficient()
        self._check_inputs_supervisor_capacities_necessary()

    def _check_inputs_player_prefs_all_reciprocated(self, party):
        """Check everyone has only ranked players who ranked them.

        In the case of supervisors, this means checking the students who
        ranked at least one of their projects.
        """

        if party == "supervisors":
            for supervisor in self.supervisors:
                for student in supervisor.prefs:
                    student_prefs_supervisors = {
                        p.supervisor for p in student.prefs
                    }
                    if supervisor not in student_prefs_supervisors:
                        warnings.warn(
                            PreferencesChangedWarning(
                                f"{supervisor} ranked {student} but they did "
                                "not rank any of their projects."
                            )
                        )

                        if self.clean:
                            for project in supervisor.projects:
                                project._forget(student)

        else:
            super()._check_inputs_player_prefs_all_reciprocated(party)

    def _check_inputs_player_reciprocated_all_prefs(self, party, other_party):
        """Check everyone has ranked all the players who ranked them.

        In the case of supervisors, this means checking the students who
        ranked at least one of their projects.
        """

        if party == "supervisors":
            for supervisor in self.supervisors:
                students_that_ranked = [
                    student
                    for student in self.students
                    if any(
                        project in student.prefs
                        for project in supervisor.projects
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

                        if self.clean:
                            for project in set(supervisor.projects) & set(
                                student.prefs
                            ):
                                student._forget(project)

        else:
            super()._check_inputs_player_reciprocated_all_prefs(
                party, other_party
            )

    def _check_inputs_supervisor_capacities_sufficient(self):
        """Check each supervisor has space for its largest project."""

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

                    if self.clean:
                        project.capacity = supervisor.capacity

    def _check_inputs_supervisor_capacities_necessary(self):
        """Check each supervisor has no surplus given their projects."""

        for supervisor in self.supervisors:
            total_project_capacity = sum(
                p.capacity for p in supervisor.projects
            )

            if supervisor.capacity > total_project_capacity:
                warnings.warn(
                    CapacityChangedWarning(
                        f"{supervisor} has a capacity of "
                        f"{supervisor.capacity} but their projects have a "
                        f"capacity of {total_project_capacity}"
                    )
                )

                if self.clean:
                    supervisor.capacity = total_project_capacity


def _check_student_unhappy(student, project):
    """Check whether a student is unhappy given a project.

    An unhappy student is either unmatched or they prefer the project to
    their current match.
    """

    return student.matching is None or student.prefers(
        project, student.matching
    )


def _check_project_unhappy(project, student):
    """Check whether a project is unhappy given a student.

    A project is unhappy because either:

    - they and their supervisor are under-subscribed;
    - they are under-subscribed, their supervisor is full, and either
      the student is in the supervisor's matching or the supervisor
      prefers the student to their worst current matching;
    - the project is full and their supervisor prefers the student to
      the worst student in the project's matching.
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


def _make_players(
    student_prefs,
    supervisor_prefs,
    project_supervisors,
    project_capacities,
    supervisor_capacities,
):
    """Make a set of students, projects and supervisors."""

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
    """Make ``Player``, ``Project`` and ``Supervisor`` instances."""

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
