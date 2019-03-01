""" Unit tests for the SA solver. """

from matching import StudentAllocation

from .params import STUDENT_ALLOCATION, _make_game


@STUDENT_ALLOCATION
def _test_init(
    student_names, proj_lect_dict, project_capacities, lecturer_capacities, seed
):
    """ Test that an instance of StudentAllocation is created correctly. """

    students, projects, lecturers, game = _make_game(
        student_names,
        proj_lect_dict,
        project_capacities,
        lecturer_capacities,
        seed,
    )

    assert game.students == students
    assert game.projects == projects
    assert game.lecturers == lecturers
    assert all([student.matching is None for student in game.students])
    assert all([project.matching == [] for project in game.projects])
    assert all([lecturer.matching == [] for lecturer in game.lecturers])
    assert game.matching is None
    assert game.blocking_pairs is None
