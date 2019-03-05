""" Unit tests for the SA solver. """

from matching import Matching

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


@STUDENT_ALLOCATION
def test_solve(student_names, project_names, faculty_names, project_capacities, seed):
    """ Test that StudentAllocation can solve games correctly. """

    for optimal in ["student", "faculty"]:
        students, projects, _, game = make_game(
            student_names, project_names, faculty_names, project_capacities, seed
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
