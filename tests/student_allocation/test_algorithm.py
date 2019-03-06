""" Tests for the Student Allocation algorithm. """

import numpy as np

from matching.games import student_allocation

from .params import STUDENT_ALLOCATION, make_players

@STUDENT_ALLOCATION
def test_student_optimal(student_names, project_names, faculty_names,
        capacities, seed):
    """ Verify that the student allocation algorithm produces a valid,
    student-optimal solution to an instance of SA. """

    np.random.seed(seed)
    students, projects, faculty = make_players(student_names, project_names,
            faculty_names, capacities)
    matching = student_allocation(students, projects, faculty,
            optimal="student")

    assert set(projects) == set(matching.keys())
    assert all(
        [
            s in set(students)
            for s in {
                match for matches in matching.values() for match in matches
            }
        ]
    )

    for student in students:
        if student.matching:
            assert student.prefs.index(student.matching) == 0


@STUDENT_ALLOCATION
def test_faculty_optimal(student_names, project_names, faculty_names,
        capacities, seed):
    """ Verify that the student allocation algorithm produces a valid,
    faculty-optimal solution to an instance of SA. """

    np.random.seed(seed)
    students, projects, faculty = make_players(student_names, project_names,
            faculty_names, capacities)
    matching = student_allocation(students, projects, faculty,
            optimal="faculty")

    assert set(projects) == set(matching.keys())
    assert all(
        [
            s in set(students)
            for s in {
                match for matches in matching.values() for match in matches
            }
        ]
    )

    for facult in faculty:
        old_idx = -np.infty
        for student in facult.matching:
            idx = facult.prefs.index(student)
            assert idx >= old_idx
            old_idx = idx
