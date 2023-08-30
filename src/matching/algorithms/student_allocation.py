""" Functions for the SA algorithm. """

from .util import _delete_pair, _match_pair


def unmatch_pair(student, project):
    """Unmatch a student-project pair."""

    student._unmatch()
    project._unmatch(student)


def student_allocation(students, projects, supervisors, optimal="student"):
    """Solve an instance of SA by treating it as a bi-level HR instance.

    A unique, stable and optimal matching is found for the given set of
    students, projects and supervisors. The optimality of the matching
    is found with respect to one party and is subsequently the worst
    stable matching for the other.

    Parameters
    ----------
    students : list of Player
        The students in the game. Each student must rank a subset of the
        elements of ``projects``.
    projects : list of Project
        The projects in the game. Each project is offered by a
        supervisor that governs its preferences.
    supervisors : list of Supervisor
        The supervisors in the game. Each supervisor offers a unique
        subset of ``projects`` and ranks all the students that have
        ranked at least one of these projects.
    optimal : str, optional
        Which party the matching should be optimised for. Must be one of
        ``"student"`` and ``"supervisor"``. Defaults to the former.

    Returns
    -------
    matching : Matching
        A dictionary-like object where the keys are the members of
        ``projects`` and their student matches are the values.
    """

    if optimal == "student":
        return student_optimal(students, projects)
    if optimal == "supervisor":
        return supervisor_optimal(projects, supervisors)


def student_optimal(students, projects):
    """Solve the instance of SA to be student-optimal.

    The student-optimal algorithm is as follows:

        0. Set all students to be unassigned, and every project and
           supervisor to be totally unsubscribed.

        1. Take any student, :math:`s`, that is unassigned and has a
           non-empty preference list, and consider their most preferred
           project, :math:`p`. Let :math:`f` denote the supervisor that
           offers :math:`p`. Assign :math:`s` to be matched to :math:`p`
           (and thus :math:`f`).

        2. If :math:`p` is now over-subscribed, find its worst current
           match, :math:`s'`. Unmatch :math:`p` and :math:`s'`. Else if
           :math:`f` is over-subscribed, find their worst current match,
           :math:`s''`, and the project they are currently subscribed
           to, :math:`p'`. Unmatch :math:`p'` and :math:`s''`.

        3. If :math:`p` is now at capacity, find their worst current
           match, :math:`s'`. For each successor, :math:`t`, to
           :math:`s'` in the preference list of :math:`p`, delete the
           pair :math:`(p, t)` from the game.

        4. If :math:`f` is at capacity, find their worst current match,
           :math:`s'`. For each successor, :math:`t`, to :math:`s'` in
           the preference list of :math:`f`, for each project,
           :math:`p'`, offered by :math:`f` that :math:`t` finds
           acceptable, delete the pair :math:`(p', t)` from the game.

        5. Go to 1 until there are no such students left, then end.
    """

    free_students = students[:]
    while free_students:
        student = free_students.pop()
        project = student.get_favourite()
        supervisor = project.supervisor

        _match_pair(student, project)

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
                _delete_pair(project, successor)
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
                    _delete_pair(project, successor)
                if not successor.prefs:
                    free_students.remove(successor)

    return {p: p.matching for p in projects}


def supervisor_optimal(projects, supervisors):
    """Solve the instance of SA to be supervisor-optimal.

    The supervisor-optimal algorithm is as follows:

        0. Set all students to be unassigned, and every project and
           supervisor to be totally unsubscribed.

        1. Take any supervisor member, :math:`f`, that is
           under-subscribed and whose preference list contains at least
           one student that is not currently matched to at least one
           acceptable (though currently under-subscribed) project
           offered by :math:`f`. Consider the supervisor's most
           preferred such student, :math:`s`, and that student's most
           preferred such project, :math:`p`.

        2. If :math:`s` is matched to some other project, :math:`p'`,
           then unmatch them. In any case, match :math:`s` and :math:`p`
           (and thus :math:`f`).

        3. For each successor, :math:`p'`, to :math:`p` in the
           preference list of :math:`s`, delete the pair :math:`(p', s)`
           from the game.

        4. Go to 1 until there are no such supervisors, then end.
    """

    free_supervisors = supervisors[:]
    while free_supervisors:
        supervisor = free_supervisors.pop()
        student, project = supervisor.get_favourite()

        if student.matching:
            curr_match = student.matching
            unmatch_pair(student, curr_match)

        _match_pair(student, project)

        successors = student.get_successors()
        for successor in successors:
            _delete_pair(student, successor)

        free_supervisors = [
            supervisor
            for supervisor in supervisors
            if supervisor.get_favourite() is not None
        ]

    return {p: p.matching for p in projects}
