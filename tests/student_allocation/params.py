""" Toolkit for SA tests. """

import itertools as it

import numpy as np
from hypothesis import given
from hypothesis.strategies import dictionaries, integers, lists, sampled_from

from matching import Player, StudentAllocation


def _get_possible_prefs(names):
    """ Generate the list of all possible non-empty preference lists made from a
    list of names. """

    all_ordered_subsets = {
        tuple(set(sub)) for sub in it.product(names, repeat=len(names))
    }

    possible_prefs = [
        list(perm)
        for sub in all_ordered_subsets
        for perm in it.permutations(sub)
    ]

    return possible_prefs


def _make_students(student_names, project_names):
    """ Given some names, make a valid set of students. """

    possible_prefs = _get_possible_prefs(project_names)
    students = [
        Player(
            name, possible_prefs[np.random.choice(range(len(possible_prefs)))]
        )
        for name in student_names
    ]

    return sorted(students, key=lambda stud: stud.name)


def _make_lecturers(students, proj_lect_dict, capacities):
    """ Given some students, relations between projects and lecturers, and
    capacities, make a valid set of lecturers. """

    available_lecturer_names = {
        l
        for s in students
        for l, p in proj_lect_dict.items()
        if p in s.pref_names
    }

    lect_stud_dict = {}
    for lect_name, proj_name in proj_lect_dict.items():
        for student in students:
            if proj_name in student.pref_names:
                try:
                    lect_stud_dict[lect_name] += [student.name]
                except KeyError:
                    lect_stud_dict[lect_name] = [student.name]

    lecturers = [
        Player(
            name,
            np.random.permutation(lect_stud_dict[name]).tolist(),
            capacities[name],
        )
        for name in available_lecturer_names
    ]

    return sorted(lecturers, key=lambda lect: lect.name)


def _make_projects(students, lecturers, proj_lect_dict, capacities):
    """ Given some students, lecturers and capacities, make a valid set of
    projects. """

    available_project_names = {p for s in students for p in s.pref_names}

    projects = []
    for lecturer in lecturers:
        project_names = proj_lect_dict[lecturer.name]
        for name in project_names:
            if name in available_project_names:
                pref_names = []
                for student in students:
                    if name in student.pref_names:
                        pref_names.append(student.name)
                pref_names.sort(key=lecturer.pref_names.index)

                project = Player(name, pref_names, capacities[name])

                projects.append(project)

    return sorted(projects, key=lambda proj: proj.name)


def _make_game(
    student_names, proj_lect_dict, project_capacities, lecturer_capacities, seed
):
    """ Make all of the players and the game itself. """

    np.random.seed(seed)
    project_names = [
        proj for projs in proj_lect_dict.values() for proj in projs
    ]
    students = _make_students(student_names, project_names)
    lecturers = _make_lecturers(students, proj_lect_dict, lecturer_capacities)
    projects = _make_projects(
        students, lecturers, proj_lect_dict, project_capacities
    )
    game = StudentAllocation(students, projects, lecturers)

    return students, projects, lecturers, game


STUDENT_ALLOCATION = given(
    student_names=lists(
        elements=sampled_from(["A", "B", "C", "D"]),
        min_size=1,
        max_size=4,
        unique=True,
    ),
    proj_lect_dict=dictionaries(
        keys=sampled_from(["X", "Y", "Z"]),
        values=lists(
            elements=sampled_from(["J", "K", "L", "M", "N"]),
            min_size=5,
            max_size=5,
        ),
        min_size=3,
        max_size=3,
    ),
    project_capacities=dictionaries(
        keys=sampled_from(["J", "K", "L", "M", "N"]),
        values=integers(min_value=1),
    ),
    lecturer_capacities=dictionaries(
        keys=sampled_from(["X", "Y", "Z"]), values=integers(min_value=2)
    ),
    seed=integers(min_value=0, max_value=2 ** 32 - 1),
)
