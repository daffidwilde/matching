""" Unit tests for the SA solver. """

import pytest

from matching import Matching, Player as Student
from matching.players import Project

from .params import STUDENT_ALLOCATION, make_game


@STUDENT_ALLOCATION
def test_init(
    student_names,
    project_names,
    faculty_names,
    capacities,
    seed,
):
    """ Test that an instance of StudentAllocation is created correctly. """

    students, projects, faculty, game = make_game(
        student_names,
        project_names,
        faculty_names,
        capacities,
        seed,
    )

    assert game.students == students
    assert game.projects == projects
    assert game.faculty == faculty
    assert all([student.matching is None for student in game.students])
    assert all([project.matching == [] for project in game.projects])
    assert all([facult.matching == [] for facult in game.faculty])
    assert game.matching is None
    assert game.blocking_pairs is None


@STUDENT_ALLOCATION
def test_inputs_student_prefs(
    student_names, project_names, faculty_names, capacities, seed
):
    """ Test that each student's preference list is a subset of the available
    projects, and check that an Exception is raised if not. """

    _, _, _, game = make_game(student_names, project_names, faculty_names,
            capacities, seed)

    assert game._check_student_prefs()

    game.students[0].prefs = [Project("foo", None)]
    with pytest.raises(Exception):
        game._check_student_prefs()


@STUDENT_ALLOCATION
def test_inputs_project_prefs(
    student_names, project_names, faculty_names, capacities, seed
):
    """ Test that each project's preference list is a permutation of the
    students that have ranked it, and check that an Exception is raised if not.
    """

    _, _, _, game = make_game(student_names, project_names, faculty_names,
            capacities, seed)

    assert game._check_project_prefs()

    game.projects[0].prefs = [Student("foo")]
    with pytest.raises(Exception):
        game._check_project_prefs()


@STUDENT_ALLOCATION
def test_inputs_faculty_prefs(
    student_names, project_names, faculty_names, capacities, seed
):
    """ Test that each faculty member's preference list is a permutation of the
    students that have ranked at least one project that they provide. Otherwise,
    check that an Exception is raised. """

    _, _, _, game = make_game(student_names, project_names, faculty_names,
            capacities, seed)

    assert game._check_faculty_prefs()

    game.faculty[0].prefs = [Student("foo")]
    with pytest.raises(Exception):
        game._check_faculty_prefs()


@STUDENT_ALLOCATION
def test_inputs_project_capacities(
    student_names, project_names, faculty_names, capacities, seed
):
    """ Test that each project has at least one space but no more than its
    faculty member can offer. Otherwise, raise an Exception. """

    _, _, _, game = make_game(student_names, project_names, faculty_names,
            capacities, seed)

    assert game._check_project_capacities()

    game.projects[0].capacity = -1
    with pytest.raises(Exception):
        game._check_project_capacities()

    game.projects[0].capacity = game.projects[0].faculty.capacity + 1
    with pytest.raises(Exception):
        game._check_project_capacities()


@STUDENT_ALLOCATION
def test_inputs_faculty_capacities(
    student_names, project_names, faculty_names, capacities, seed
):
    """ Test that each faculty member has enough space to accommodate their
    largest project, but does not offer a surplus of spaces from their projects.
    Otherwise, raise an Exception. """

    _, _, _, game = make_game(student_names, project_names, faculty_names,
            capacities, seed)

    assert game._check_faculty_capacities()

    game.faculty[0].capacity = 0
    with pytest.raises(Exception):
        game._check_faculty_capacities()

    game.faculty[0].capacity = 1e6
    with pytest.raises(Exception):
        game._check_faculty_capacities()


@STUDENT_ALLOCATION
def test_solve(student_names, project_names, faculty_names, capacities, seed):
    """ Test that StudentAllocation can solve games correctly. """

    for optimal in ["student", "faculty"]:
        students, projects, _, game = make_game(
            student_names, project_names, faculty_names, capacities, seed
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
            facult = student.matching.faculty
            assert student in facult.matching

        for student in set(students) - set(matched_students):
            assert student.matching is None
