"""Tests for the Student Allocation algorithm."""

import numpy as np

from matching.algorithms.student_allocation import (
    student_allocation,
    student_optimal,
    supervisor_optimal,
)

from .util import STUDENT_ALLOCATION, make_players


@STUDENT_ALLOCATION
def test_student_allocation(
    student_names, project_names, supervisor_names, capacities, seed, clean
):
    """Test for a valid output from the student allocation algorithm."""

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
    """Test that the student-optimal algorithm is student-optimal."""

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
    """Test the supervisor-optimal algorithm is supervisor-optimal."""

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
