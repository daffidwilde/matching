""" Unit tests for the SA solver. """

import pytest

from matching import Matching
from matching import Player as Student
from matching.games import StudentAllocation
from matching.players import Project, Supervisor

from .params import STUDENT_ALLOCATION, make_game


@STUDENT_ALLOCATION
def test_init(student_names, project_names, supervisor_names, capacities, seed):
    """ Test that an instance of StudentAllocation is created correctly. """

    students, projects, supervisors, game = make_game(
        student_names, project_names, supervisor_names, capacities, seed
    )

    assert game.students == students
    assert game.projects == projects
    assert game.supervisors == supervisors
    assert all([student.matching is None for student in game.students])
    assert all([project.matching == [] for project in game.projects])
    assert all([supervisor.matching == [] for supervisor in game.supervisors])
    assert game.matching is None
    assert game.blocking_pairs is None


@STUDENT_ALLOCATION
def test_inputs_student_prefs(
    student_names, project_names, supervisor_names, capacities, seed
):
    """ Test that each student's preference list is a subset of the available
    projects, and check that an Exception is raised if not. """

    _, _, _, game = make_game(
        student_names, project_names, supervisor_names, capacities, seed
    )

    assert game._check_student_prefs()

    student = game.students[0]
    student.prefs = [Project("foo", None)]
    with pytest.raises(Exception):
        game._check_student_prefs()


@STUDENT_ALLOCATION
def test_inputs_project_prefs(
    student_names, project_names, supervisor_names, capacities, seed
):
    """ Test that each project's preference list is a permutation of the
    students that have ranked it, and check that an Exception is raised if not.
    """

    _, _, _, game = make_game(
        student_names, project_names, supervisor_names, capacities, seed
    )

    assert game._check_project_prefs()

    project = game.projects[0]
    project.prefs = [Student("foo")]
    with pytest.raises(Exception):
        game._check_project_prefs()


@STUDENT_ALLOCATION
def test_inputs_supervisor_prefs(
    student_names, project_names, supervisor_names, capacities, seed
):
    """ Test that each supervisor's preference list is a permutation of the
    students that have ranked at least one project that they provide. Otherwise,
    check that an Exception is raised. """

    _, _, _, game = make_game(
        student_names, project_names, supervisor_names, capacities, seed
    )

    assert game._check_supervisor_prefs()

    supervisor = game.supervisors[0]
    supervisor.prefs = [Student("foo")]
    with pytest.raises(Exception):
        game._check_supervisor_prefs()


@STUDENT_ALLOCATION
def test_inputs_project_capacities(
    student_names, project_names, supervisor_names, capacities, seed
):
    """ Test that each project has at least one space but no more than its
    supervisor can offer. Otherwise, raise an Exception. """

    _, _, _, game = make_game(
        student_names, project_names, supervisor_names, capacities, seed
    )

    assert game._check_init_project_capacities()

    project = game.projects[0]
    project.capacity = -1
    with pytest.raises(Exception):
        game._check_init_project_capacities()

    project.capacity = project.supervisor.capacity + 1
    with pytest.raises(Exception):
        game._check_init_project_capacities()


@STUDENT_ALLOCATION
def test_inputs_supervisor_capacities(
    student_names, project_names, supervisor_names, capacities, seed
):
    """ Test that each supervisor has enough space to accommodate their largest
    project, but does not offer a surplus of spaces from their projects.
    Otherwise, raise an Exception. """

    _, _, _, game = make_game(
        student_names, project_names, supervisor_names, capacities, seed
    )

    assert game._check_init_supervisor_capacities()

    supervisor = game.supervisors[0]
    supervisor.capacity = 0
    with pytest.raises(Exception):
        game._check_init_supervisor_capacities()

    supervisor.capacity = 1e6
    with pytest.raises(Exception):
        game._check_init_supervisor_capacities()


@STUDENT_ALLOCATION
def test_solve(
    student_names, project_names, supervisor_names, capacities, seed
):
    """ Test that StudentAllocation can solve games correctly. """

    for optimal in ["student", "supervisor"]:
        students, projects, _, game = make_game(
            student_names, project_names, supervisor_names, capacities, seed
        )

        matching = game.solve(optimal)
        assert isinstance(matching, Matching)
        assert set(matching.keys()) == set(projects)
        matched_students = [
            stud for match in matching.values() for stud in match
        ]
        assert matched_students != [] and set(matched_students).issubset(
            set(students)
        )

        for student in matched_students:
            supervisor = student.matching.supervisor
            assert student in supervisor.matching

        for student in set(students) - set(matched_students):
            assert student.matching is None


@STUDENT_ALLOCATION
def test_check_validity(
    student_names, project_names, supervisor_names, capacities, seed
):
    """ Test that StudentAllocation finds a valid matching when the game is
    solved. """

    _, _, _, game = make_game(
        student_names, project_names, supervisor_names, capacities, seed
    )

    game.solve()
    assert game.check_validity()


@STUDENT_ALLOCATION
def test_check_student_matching(
    student_names, project_names, supervisor_names, capacities, seed
):
    """ Test that StudentAllocation recognises a valid matching requires a
    student to have a preference of their match, if they have one. """

    _, _, _, game = make_game(
        student_names, project_names, supervisor_names, capacities, seed
    )

    game.solve()
    assert game._check_student_matching()

    student = game.students[0]
    student.matching = Project(name="foo", capacity=0)
    with pytest.raises(Exception):
        game._check_student_matching()


@STUDENT_ALLOCATION
def test_check_project_matching(
    student_names, project_names, supervisor_names, capacities, seed
):
    """ Test that StudentAllocation recognises a valid matching requires a
    project to have a preference of each of their matches, if they have any. """

    _, _, _, game = make_game(
        student_names, project_names, supervisor_names, capacities, seed
    )

    game.solve()
    assert game._check_project_matching()

    project = game.projects[0]
    project.matching.append(Student(name="foo"))
    with pytest.raises(Exception):
        game._check_project_matching()


@STUDENT_ALLOCATION
def test_check_supervisor_matching(
    student_names, project_names, supervisor_names, capacities, seed
):
    """ Test that StudentAllocation recognises a valid matching requires each
    supervisor to have a preference of each of their matches, if they have
    any. """

    _, _, _, game = make_game(
        student_names, project_names, supervisor_names, capacities, seed
    )

    game.solve()
    assert game._check_supervisor_matching()

    supervisor = game.supervisors[0]
    supervisor.matching.append(Student(name="foo"))
    with pytest.raises(Exception):
        game._check_supervisor_matching()


@STUDENT_ALLOCATION
def test_check_project_capacity(
    student_names, project_names, supervisor_names, capacities, seed
):
    """ Test that StudentAllocation recognises a valid matching requires all
    projects to not be over-subscribed. """

    _, _, _, game = make_game(
        student_names, project_names, supervisor_names, capacities, seed
    )

    game.solve()
    assert game._check_project_capacity()

    project = game.projects[0]
    project.matching = range(project.capacity + 1)
    with pytest.raises(Exception):
        game._check_project_capacity()


@STUDENT_ALLOCATION
def test_check_supervisor_capacity(
    student_names, project_names, supervisor_names, capacities, seed
):
    """ Test that StudentAllocation recognises a valid matching requires all
    supervisors to not be over-subscribed. """

    _, _, _, game = make_game(
        student_names, project_names, supervisor_names, capacities, seed
    )

    game.solve()
    assert game._check_supervisor_capacity()

    supervisor = game.supervisors[0]
    supervisor.matching = range(supervisor.capacity + 1)
    with pytest.raises(Exception):
        game._check_supervisor_capacity()


def test_check_stability():
    """ Test that StudentAllocation can recognise whether a matching is stable
    or not. """

    students = [Student("A"), Student("B"), Student("C")]
    projects = [Project("P", 2), Project("Q", 2)]
    supervisors = [Supervisor("X", 2), Supervisor("Y", 2)]

    a, b, c = students
    p, q = projects
    x, y = supervisors

    p.set_supervisor(x)
    q.set_supervisor(y)

    a.set_prefs([p, q])
    b.set_prefs([q])
    c.set_prefs([q, p])

    x.set_prefs([c, a])
    y.set_prefs([a, b, c])

    game = StudentAllocation(students, projects, supervisors)

    matching = game.solve()
    assert game.check_stability()

    matching[p] = [c]
    matching[q] = [a, b]

    assert not game.check_stability()
