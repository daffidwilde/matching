""" Unit tests for the SA solver. """

import pytest

from matching import Matching, Player as Student

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

    game.students[0].prefs = [Student("foo")]
    with pytest.raises(Exception):
        game._check_student_prefs()


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
