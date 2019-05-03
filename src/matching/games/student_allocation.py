""" The Student Allocation Problem solver and core algorithm. """

from matching import Game, Matching

from .util import delete_pair, match_pair


class StudentAllocation(Game):
    """ A class for solving instances of the Student Allocation problem (SA)
    using an adapted Gale-Shapley algorithm.

    Parameters
    ==========
    students : `list`
        The students in the game. Each student must rank a subset of the
        projects.
    projects : `list`
        The projects in the game. Each project has a faculty member associated
        with it that governs its preferences.
    faculty : `list`
        The faculty members in the game. Each faculty member oversees a distinct
        subset of projects and ranks all of those students that have ranked at
        least one of its projects.

    Attributes
    ==========
    matching : `matching.matching.Matching`
        Once the game is solved, a matching is available. This `Matching` object
        behaves much like a dictionary that uses projects as keys and their
        student matches as values. Initialises as `None`.
    blocking_pairs : `list` of (`student`, `project`)-tuples
        The student-project pairs that satisfy the following conditions:
            - The student has a preference of the project;
            - either the student is unmatched, or they prefer the project to
              their current project;
            - either:
                - the project or its faculty is under-subscribed, or
                - the project is under-subscribed and the faculty is at
                  capacity, and the student is matched to a project offered by
                  the faculty or the faculty prefers the student to its worst
                  currently matched student, or
                - the project is at capacity and its faculty prefers the student
                  to its worst currently matched student.
        Such pairs are said to 'block' the matching. Initialises as `None`.
    """

    def __init__(self, students, projects, faculty):

        self.students = students
        self.projects = projects
        self.faculty = faculty
        super().__init__()

        self._check_inputs()

    def solve(self, optimal="student"):
        """ Solve the instance of SA using either the student- or
        faculty-optimal algorithm. """

        self._matching = Matching(
            student_allocation(
                self.students, self.projects, self.faculty, optimal
            )
        )
        return self.matching

    def check_validity(self):
        """ Check whether the current matching is valid. """

        self._check_student_matching()
        self._check_project_capacity()
        self._check_project_matching()
        self._check_faculty_capacity()
        self._check_faculty_matching()

        return True

    def check_stability(self):
        """ Check for the existence of any blocking pairs in the current
        matching, thus determining the stability of the matching. """

        blocking_pairs = []
        for student in self.students:
            for project in self.projects:
                if project in student.prefs:
                    if _check_student_unhappy(
                        student, project
                    ) and _check_project_unhappy(project, student):
                        blocking_pairs.append((student, project))

        return not any(blocking_pairs)

    def _check_student_matching(self):
        """ Check that no student is matched to an unacceptable project. """

        errors = []
        for student in self.students:
            if (
                student.matching is not None
                and student.matching not in student.prefs
            ):
                errors.append(
                    ValueError(
                        f"{student} is matched to {student.matching} but "
                        "they do not appear in their preference list: "
                        f"{student.prefs}."
                    )
                )

        if errors:
            raise Exception(*errors)

        return True

    def _check_project_capacity(self):
        """ Check that no projects are over-subscribed. """

        errors = []
        for project in self.projects:
            if len(project.matching) > project.capacity:
                errors.append(
                    ValueError(
                        f"{project} is matched to {project.matching} which "
                        f"if over their capacity of {project.capacity}."
                    )
                )

        if errors:
            raise Exception(*errors)

        return True

    def _check_project_matching(self):
        """ Check that no project is matched to an unacceptable student. """

        errors = []
        for project in self.projects:
            for student in project.matching:
                if student not in project.prefs:
                    errors.append(
                        ValueError(
                            f"{project} has {student} in their matching but "
                            "they do not appear in their preference list: "
                            f"{project.prefs}."
                        )
                    )

        if errors:
            raise Exception(*errors)

        return True

    def _check_faculty_capacity(self):
        """ Check that no faculty member is over-subscribed. """

        errors = []

        for faculty in self.faculty:
            if len(faculty.matching) > faculty.capacity:
                errors.append(
                    ValueError(
                        f"{faculty} is matched to {faculty.matching} which "
                        f"if over their capacity of {faculty.capacity}."
                    )
                )

        if errors:
            raise Exception(*errors)

        return True

    def _check_faculty_matching(self):
        """ Check that no faculty member is matched to an unacceptable student.
        """

        errors = []
        for faculty in self.faculty:
            for student in faculty.matching:
                if student not in faculty.prefs:
                    errors.append(
                        ValueError(
                            f"{faculty} has {student} in their matching but "
                            "they do not appear in their preference list: "
                            f"{faculty.prefs}."
                        )
                    )

        if errors:
            raise Exception(*errors)

        return True

    def _check_inputs(self):
        """ Check that the players in the game have valid preferences, and in
        the case of projects and faculty: capacities. """

        self._check_student_prefs()
        self._check_project_prefs()
        self._check_faculty_prefs()

        self._check_init_project_capacities()
        self._check_init_faculty_capacities()

    def _check_student_prefs(self):
        """ Make sure that each student's preference list is a subset of the
        available projects. Otherwise, raise an error. """

        errors = []
        for student in self.students:
            if not set(student.prefs).issubset(set(self.projects)):
                errors.append(
                    ValueError(
                        f"{student} has ranked a non-project: "
                        f"{set(student.prefs)} != {set(self.projects)}"
                    )
                )

        if errors:
            raise Exception(*errors)

        return True

    def _check_project_prefs(self):
        """ Make sure that each project ranks all and only those students that
        ranked it. """

        errors = []
        for project in self.projects:
            students_that_ranked = [
                student for student in self.students if project in student.prefs
            ]
            if set(project.prefs) != set(students_that_ranked):
                errors.append(
                    ValueError(
                        f"{project} has not ranked the students that ranked "
                        f"it: {set(project.prefs)} != "
                        f"{set(students_that_ranked)}"
                    )
                )

        if errors:
            raise Exception(*errors)

        return True

    def _check_faculty_prefs(self):
        """ Make sure that each faculty member ranks all and only those students
        that ranked at least one project that they offer. """

        errors = []
        for faculty in self.faculty:
            students_that_ranked = [
                student
                for student in self.students
                if any(
                    [project in student.prefs for project in faculty.projects]
                )
            ]
            if set(faculty.prefs) != set(students_that_ranked):
                errors.append(
                    ValueError(
                        f"{faculty} has not ranked the students that ranked at "
                        f"least one of its projects: {set(faculty.prefs)} != "
                        f"{set(students_that_ranked)}"
                    )
                )

        if errors:
            raise Exception(*errors)

        return True

    def _check_init_project_capacities(self):
        """ Check that each project has at least one space but no more than
        their faculty member. """

        errors = []
        for project in self.projects:
            if (
                project.capacity < 1
                or project.capacity > project.faculty.capacity
            ):
                errors.append(
                    ValueError(
                        f"{project} does not have a valid capacity: "
                        f"{project.capacity}"
                    )
                )

        if errors:
            raise Exception(*errors)

        return True

    def _check_init_faculty_capacities(self):
        """ Check that each faculty member has sufficient spaces for their
        projects. """

        errors = []
        for faculty in self.faculty:
            project_capacities = [proj.capacity for proj in faculty.projects]
            if faculty.capacity < max(project_capacities):
                errors.append(
                    ValueError(
                        f"{faculty} does not have enough space to provide for "
                        "their largest project"
                    )
                )
            elif faculty.capacity > sum(project_capacities):
                errors.append(
                    ValueError(
                        f"{faculty} can offer more spaces than their projects "
                        "can provide"
                    )
                )

        if errors:
            raise Exception(*errors)

        return True


def _check_student_unhappy(student, project):
    """ Determine whether `student` is unhappy either because they are unmatched
    or because they prefer `project` to their current matching. """

    return student.matching is None or student.prefers(
        project, student.matching
    )


def _check_project_unhappy(project, student):
    """ Determine whether `project` is unhappy because either:
            - they and their faculty are under-subscribed;
            - they are under-subscribed, their faculty is full, and either
              `student` is in the faculty's matching or the faculty prefers
              `student` to their worst current matching;
            - `project` is full and their faculty prefers `student` to the worst
              student in the matching of `project`.
    """

    faculty = project.faculty

    project_undersubscribed = len(project.matching) < project.capacity
    both_undersubscribed = (
        project_undersubscribed and len(faculty.matching) < faculty.capacity
    )

    faculty_full = len(faculty.matching) == faculty.capacity
    swap_available = student in faculty.matching or faculty.prefers(
        student, faculty.get_worst_match()
    )

    project_upsetting_faculty = len(
        project.matching
    ) == project.capacity and faculty.prefers(
        student, project.get_worst_match()
    )

    return (
        both_undersubscribed
        or (project_undersubscribed and faculty_full and swap_available)
        or project_upsetting_faculty
    )


def unmatch_pair(student, project):
    """ Unmatch a student-project pair. """

    student.unmatch()
    project.unmatch(student)


def student_allocation(students, projects, faculty, optimal="student"):
    """ Solve an instance of SA by treating it as a bi-level HR. A unique,
    stable and optimal matching is found for the given set of students, projects
    and faculty. The optimality of the matching is found with respect to one
    party and is subsequently the worst stable matching for the other.

    Parameters
    ==========
    students : `list`
        The students in the game. Each student must rank a subset of the
        elements of `projects`.
    projects : `list`
        The projects in the game. Each project is offered by a member of
        `faculty` that governs its preferences.
    faculty : `list`)`
        The faculty in the game. Each member of the faculty offers a distinct
        subset of `projects` and ranks all the students that have ranked at
        least one of these projects.
    optimal : `str`, optional
        Which party the matching should be optimised for. Must be one of
        `"student"` and `"faculty"`. Defaults to `"student"`.

    Returns
    =======
    matching : `Matching`
        A dictionary-like object using the `projects` as keys and their matches
        (made from `students`) as values.
    """

    if optimal == "student":
        return student_optimal(students, projects)
    if optimal == "faculty":
        return faculty_optimal(projects, faculty)


def student_optimal(students, projects):
    """ Solve the instance of SA to be student-optimal. The algorithm is as
    follows:

        0. Set all students to be unassigned, and every project (and faculty
        member) to be totally unsubscribed.

        1. Take any student, :math:`s`, that is unassigned and has a non-empty
        preference list, and consider their most preferred project, :math:`p`.
        Let :math:`f` denote the faculty member that offers :math:`p`. Assign
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
        faculty = project.faculty

        match_pair(student, project)

        if len(project.matching) > project.capacity:
            worst = project.get_worst_match()
            unmatch_pair(worst, project)
            free_students.append(worst)

        elif len(faculty.matching) > faculty.capacity:
            worst = faculty.get_worst_match()
            worst_project = worst.matching
            unmatch_pair(worst, worst_project)
            free_students.append(worst)

        if len(project.matching) == project.capacity:
            successors = project.get_successors()
            for successor in successors:
                delete_pair(project, successor)
                if not successor.prefs:
                    free_students.remove(successor)

        if len(faculty.matching) == faculty.capacity:
            successors = faculty.get_successors()
            for successor in successors:

                faculty_projects = [
                    project
                    for project in faculty.projects
                    if project in successor.prefs
                ]

                for project in faculty_projects:
                    delete_pair(project, successor)
                if not successor.prefs:
                    free_students.remove(successor)

    return {p: p.matching for p in projects}


def faculty_optimal(projects, faculty):
    """ Solve the instance of SA to be faculty-optimal. The algorithm is as
    follows:

        0. Set all students to be unassigned, and every project (and faculty
        member) to be totally unsubscribed.

        1. Take any faculty member, :math:`f`, that is under-subscribed and
        whose preference list contains at least one student that is not
        currently matched to at least one acceptable (though currently
        under-subscribed) project offered by :math:`f`. Consider the faculty
        member's most preferred such student, :math:`s`, and that student's most
        preferred such project, :math:`p`.

        2. If :math:`s` is matched to some other project, :math:`p'`, then
        unmatch them. In any case, match :math:`s` and :math:`p` (and thus
        :math:`f`).

        3. For each successor, :math:`p'`, to :math:`p` in the preference list
        of :math:`s`, delete the pair :math:`(p', s)` from the game.

        4. Go to 1 until there are no such lecturers, then end.
    """

    free_faculty = faculty[:]
    while free_faculty:

        facult = free_faculty.pop()
        student, project = facult.get_favourite()

        if student.matching:
            curr_match = student.matching
            unmatch_pair(student, curr_match)

        match_pair(student, project)

        successors = student.get_successors()
        for successor in successors:
            delete_pair(student, successor)

        free_faculty = [f for f in faculty if f.get_favourite() is not None]

    return {p: p.matching for p in projects}
