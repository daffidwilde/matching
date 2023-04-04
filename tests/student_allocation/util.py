"""Toolkit for SA tests."""

import itertools as it
from collections import defaultdict

import numpy as np
from hypothesis import given
from hypothesis.strategies import booleans, integers, lists, sampled_from

from matching import Player as Student
from matching.games import StudentAllocation
from matching.players import Project, Supervisor


def get_possible_prefs(players):
    """Get list of possible non-empty preferences from some players."""

    all_ordered_subsets = {
        tuple(set(sub)) for sub in it.product(players, repeat=len(players))
    }

    possible_prefs = [
        list(perm)
        for sub in all_ordered_subsets
        for perm in it.permutations(sub)
    ]

    return possible_prefs


def make_players(student_names, project_names, supervisor_names, capacities):
    """Given some names and capacities, make a set of players for SA."""

    students = [Student(name) for name in student_names]
    projects = [
        Project(name, cap) for name, cap in zip(project_names, capacities)
    ]
    supervisors = [
        Supervisor(name, capacity=None) for name in supervisor_names
    ]

    if len(students) > len(projects):
        students = students[: len(projects)]

    for project in projects:
        project.set_supervisor(np.random.choice(supervisors))

    supervisors = [
        supervisor for supervisor in supervisors if supervisor.projects
    ]
    for supervisor in supervisors:
        capacities = sorted([proj.capacity for proj in supervisor.projects])
        min_cap, max_cap = max(capacities), sum(capacities)
        supervisor.capacity = np.random.randint(min_cap, max_cap + 1)

    possible_prefs = get_possible_prefs(projects)
    logged_prefs = {supervisor: [] for supervisor in supervisors}
    for student in students:
        prefs = possible_prefs[np.random.choice(range(len(possible_prefs)))]
        student.set_prefs(prefs)
        for project in prefs:
            supervisor = project.supervisor
            if student not in logged_prefs[supervisor]:
                logged_prefs[supervisor].append(student)

    for supervisor, studs in logged_prefs.items():
        supervisor.set_prefs(np.random.permutation(studs).tolist())

    projects = [p for p in projects if p.prefs]
    supervisors = [s for s in supervisors if s.prefs]

    return students, projects, supervisors


def make_game(
    student_names, project_names, supervisor_names, capacities, seed, clean
):
    """Make all of the players and the game itself."""

    np.random.seed(seed)
    students, projects, supervisors = make_players(
        student_names, project_names, supervisor_names, capacities
    )
    game = StudentAllocation(students, projects, supervisors, clean)

    return students, projects, supervisors, game


def make_connections(
    student_names, project_names, supervisor_names, capacities, seed
):
    """Make a set of preferences and affiliations from some names."""

    np.random.seed(seed)
    project_supervisors = {}
    project_capacities = dict(zip(project_names, capacities))
    student_prefs = defaultdict(list)
    supervisor_prefs = defaultdict(list)
    supervisor_projects = defaultdict(list)
    supervisor_capacities = defaultdict(list)

    for project in project_names:
        supervisor = np.random.choice(supervisor_names)
        project_supervisors[project] = supervisor

    possible_prefs = get_possible_prefs(project_names)
    for student in student_names:
        prefs = possible_prefs[np.random.randint(len(possible_prefs))]
        student_prefs[student].extend(prefs)

        for project in prefs:
            supervisor = project_supervisors[project]
            sup_prefs = supervisor_prefs[supervisor]
            if student not in sup_prefs:
                sup_prefs.append(student)

    chosen_projects = {
        p for projects in student_prefs.values() for p in projects
    }
    for project in set(project_names) - chosen_projects:
        del project_supervisors[project]
        del project_capacities[project]

    for project, supervisor in project_supervisors.items():
        supervisor_projects[supervisor].append(project)

    supervisor_capacities = dict(supervisor_capacities)
    for supervisor, projects in supervisor_projects.items():
        values = [project_capacities[project] for project in projects]
        capacity = np.random.randint(max(values), sum(values) + 1)
        supervisor_capacities[supervisor] = capacity

    for supervisor in supervisor_prefs:
        np.random.shuffle(supervisor_prefs[supervisor])

    return (
        student_prefs,
        supervisor_prefs,
        project_supervisors,
        project_capacities,
        supervisor_capacities,
    )


STUDENT_ALLOCATION = given(
    student_names=lists(
        elements=sampled_from(["A", "B", "C", "D"]),
        min_size=1,
        max_size=4,
        unique=True,
    ),
    project_names=lists(
        elements=sampled_from(["P", "Q", "R", "S", "T"]),
        min_size=5,
        max_size=5,
        unique=True,
    ),
    supervisor_names=lists(
        elements=sampled_from(["X", "Y", "Z"]),
        min_size=1,
        max_size=3,
        unique=True,
    ),
    capacities=lists(
        integers(min_value=1, max_value=2), min_size=5, max_size=5
    ),
    seed=integers(min_value=0, max_value=2**32 - 1),
    clean=booleans(),
)
