""" Toolkit for SA tests. """

import itertools as it

import numpy as np
from hypothesis import given
from hypothesis.strategies import integers, lists, sampled_from

from matching import Player as Student
from matching.games import StudentAllocation
from matching.players import Faculty, Project


def get_possible_prefs(players):
    """ Generate the list of all possible non-empty preference lists made from a
    list of players. """

    all_ordered_subsets = {
        tuple(set(sub)) for sub in it.product(players, repeat=len(players))
    }

    possible_prefs = [
        list(perm)
        for sub in all_ordered_subsets
        for perm in it.permutations(sub)
    ]

    return possible_prefs


def make_players(
    student_names,
    project_names,
    faculty_names,
    project_capacities,
    faculty_capacities,
):
    """ Given some names and capacities, make a set of players for SA. """

    students = [Student(name) for name in student_names]
    projects = [
        Project(name, cap)
        for name, cap in zip(project_names, project_capacities)
    ]
    faculty = [
        Faculty(name, cap)
        for name, cap in zip(faculty_names, faculty_capacities)
    ]

    for project in projects:
        project.set_faculty(np.random.choice(faculty))

    faculty = [f for f in faculty if f.projects != []]

    possible_prefs = get_possible_prefs(projects)
    logged_prefs = {}
    for student in students:
        prefs = possible_prefs[np.random.choice(range(len(possible_prefs)))]
        student.set_prefs(prefs)
        for project in prefs:
            facult = project.faculty
            try:
                logged_prefs[facult] += [student]
            except KeyError:
                logged_prefs[facult] = [student]

    for facult, studs in logged_prefs.items():
        facult.set_prefs(np.random.permutation(studs).tolist())

    return students, projects, faculty


def make_game(
    student_names,
    project_names,
    faculty_names,
    project_capacities,
    faculty_capacities,
    seed,
):
    """ Make all of the players and the game itself. """

    np.random.seed(seed)
    students, projects, faculty = make_players(
        student_names,
        project_names,
        faculty_names,
        project_capacities,
        faculty_capacities,
    )
    game = StudentAllocation(students, projects, faculty)

    return students, projects, faculty, game


STUDENT_ALLOCATION = given(
    student_names=lists(
        elements=sampled_from(["A", "B", "C", "D"]),
        min_size=1,
        max_size=4,
        unique=True,
    ),
    project_names=lists(
        elements=sampled_from(["J", "K", "L", "M", "N"]),
        min_size=1,
        max_size=5,
        unique=True,
    ),
    faculty_names=lists(
        elements=sampled_from(["X", "Y", "Z"]),
        min_size=1,
        max_size=3,
        unique=True,
    ),
    project_capacities=lists(integers(min_value=4), min_size=1, max_size=5),
    faculty_capacities=lists(integers(min_value=4), min_size=1, max_size=3),
    seed=integers(min_value=0, max_value=2 ** 32 - 1),
)
