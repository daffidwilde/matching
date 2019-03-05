""" Unit tests for the SA solver. """

from matching.games import StudentAllocation

from .params import STUDENT_ALLOCATION, make_game


@STUDENT_ALLOCATION
def test_init(
    student_names,
    project_names,
    faculty_names,
    project_capacities,
    seed,
):
    """ Test that an instance of StudentAllocation is created correctly. """

    students, projects, faculty, game = make_game(
        student_names,
        project_names,
        faculty_names,
        project_capacities,
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
