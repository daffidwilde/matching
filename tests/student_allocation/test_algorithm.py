""" Tests for the Student Allocation algorithm. """

import numpy as np

from matching.games import student_allocation

from .params import STUDENT_ALLOCATION, make_players

@STUDENT_ALLOCATION
def test_student_optimal(student_names, project_names, faculty_names,
        project_capacities, seed):

    np.random.seed(seed)
    students, projects, faculty = make_players(student_names, project_names,
            faculty_names, project_capacities)
    matching = student_allocation(students, projects, faculty,
            optimal="student")

    assert set(projects) == set(matching.keys())
    assert all(
        [
            s in set(students)
            for s in {
                s_match for matches in matching.values() for s_match in matches
            }
        ]
    )

    for student in students:
        if student.matching:
            assert student.prefs.index(student.matching) == 0
