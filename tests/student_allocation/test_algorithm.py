""" Tests for the Student Allocation algorithm. """

import numpy as np

from matching.games import student_allocation

from .params import STUDENT_ALLOCATION, make_players


@STUDENT_ALLOCATION
def test_student_optimal(
    student_names, project_names, supervisor_names, capacities, seed
):
    """ Verify that the student allocation algorithm produces a valid,
    student-optimal solution to an instance of SA. """

    np.random.seed(seed)
    students, projects, supervisors = make_players(
        student_names, project_names, supervisor_names, capacities
    )
    matching = student_allocation(
        students, projects, supervisors, optimal="student"
    )

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
def test_supervisor_optimal(
    student_names, project_names, supervisor_names, capacities, seed
):
    """ Verify that the student allocation algorithm produces a valid,
    supervisor-optimal solution to an instance of SA. """

    np.random.seed(seed)
    students, projects, supervisors = make_players(
        student_names, project_names, supervisor_names, capacities
    )
    matching = student_allocation(
        students, projects, supervisors, optimal="supervisor"
    )

    assert set(projects) == set(matching.keys())
    assert all(
        [
            s in set(students)
            for s in {
                match for matches in matching.values() for match in matches
            }
        ]
    )

    for supervisor in supervisors:
        old_idx = -np.infty
        for student in supervisor.matching:
            idx = supervisor.prefs.index(student)
            assert idx >= old_idx
            old_idx = idx
