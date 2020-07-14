""" Tests for the Student Allocation algorithm. """

import numpy as np

from matching.algorithms.student_allocation import (
    student_optimal, student_allocation, supervisor_optimal
)

from .params import STUDENT_ALLOCATION, make_players


@STUDENT_ALLOCATION
def test_student_allocation(
    student_names, project_names, supervisor_names, capacities, seed, clean
):
    """ Verify that the student allocation algorithm produces a valid solution
    to an instance of SA. """

    np.random.seed(seed)
    students, projects, supervisors = make_players(
        student_names, project_names, supervisor_names, capacities
    )
    matching = student_allocation(students, projects, supervisors)

    assert set(projects) == set(matching.keys())

    matched_students = {s for ss in matching.values() for s in ss}
    for student in students:
        if student.matching:
            assert student in matched_students
        else:
            assert student not in matched_students


@STUDENT_ALLOCATION
def test_student_optimal(
    student_names, project_names, supervisor_names, capacities, seed, clean
):
    """ Verify that the student-optimal algorithm produces a solution that is
    indeed student-optimal. """

    np.random.seed(seed)
    students, projects, _ = make_players(
        student_names, project_names, supervisor_names, capacities
    )
    matching = student_optimal(students, projects)

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
    student_names, project_names, supervisor_names, capacities, seed, clean
):
    """ Verify that the supervisor-optimal algorithm produces a solution that is
    indeed supervisor-optimal. """

    np.random.seed(seed)
    students, projects, supervisors = make_players(
        student_names, project_names, supervisor_names, capacities
    )
    matching = supervisor_optimal(projects, supervisors)

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
