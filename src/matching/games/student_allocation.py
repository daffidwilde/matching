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
    matching : `Matching`
        Once the game is solved, a matching is available. This `Matching` object
        behaves much like a dictionary that uses projects as keys and their
        student matches as values. Initialises as `None`.
    blocking_pairs : `list`
        The project-student pairs that satisfy the following conditions:
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

    def solve(self, optimal="student"):
        """ Solve the instance of SA using either the student- or
        faculty-optimal algorithm. """

        self._matching = Matching(
            student_allocation(self.students, self.projects, self.faculty,
                optimal)
        )
        return self.matching

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
