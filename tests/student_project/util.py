"""Utilities for SP tests."""

import hypothesis.strategies as st
import numpy as np

from ..common import st_single_ranks, st_single_utilities, st_sizes


@st.composite
def st_sizes(draw, smin, smax, pmin, pmax, fmin, fmax):
    """Create a sensible number of players in a game."""
    ssize = draw(st.integers(smin, smax))
    fsize = draw(st.integers(fmin, fmax))
    psize = draw(st.integers(max(pmin, fsize), pmax))

    return ssize, psize, fsize


@st.composite
def st_affiliations(draw, psize, fsize):
    """Create a project affiliation array."""
    faculty = list(range(fsize))
    diff = psize - fsize
    extra = draw(st.lists(st.integers(0, fsize - 1), min_size=diff, max_size=diff))
    affiliations = draw(st.permutations(faculty + extra))

    return np.array(affiliations)


@st.composite
def st_capacities(draw, psize, fsize, affiliations):
    """Create a set of valid capacity vectors."""
    supervisor_capacities = draw(st.lists(st.integers(1, 3), min_size=fsize, max_size=fsize))
    project_capacities = draw(st.lists(st.integers(1, 2), min_size=psize, max_size=psize))

    for proj, sup in enumerate(affiliations):
        pcap = project_capacities[proj]
        scap = supervisor_capacities[sup]
        if pcap > scap:
            project_capacities[proj] = scap

    for sup, scap in enumerate(supervisor_capacities):
        total_project_capacity = sum(
            pcap for proj, pcap in enumerate(project_capacities) if affiliations[proj] == sup
        )
        if scap > total_project_capacity:
            supervisor_capacities[sup] = total_project_capacity

    return np.array(project_capacities), np.array(supervisor_capacities)


@st.composite
def st_ranks_capacities(draw, smin=1, smax=5, pmin=1, pmax=5, fmin=1, fmax=3):
    """Create a set of rankings and capacities for a test."""
    ssize, psize, fsize = draw(st_sizes(smin, smax, pmin, pmax, fmin, fmax))

    student_ranks = draw(st_single_ranks(ssize, psize))
    supervisor_ranks = draw(st_single_ranks(fsize, ssize))

    affiliations = draw(st_affiliations(psize, fsize))
    project_capacities, supervisor_capacities = draw(st_capacities(psize, fsize, affiliations))

    return student_ranks, supervisor_ranks, affiliations, project_capacities, supervisor_capacities


@st.composite
def st_utilities_capacities(draw, smin=1, smax=5, pmin=1, pmax=5, fmin=1, fmax=3):
    """Create a set of utilities and capacities for a test."""
    ssize, psize, fsize = draw(st_sizes(smin, smax, pmin, pmax, fmin, fmax))

    student_utilities = draw(st_single_utilities(ssize, psize))
    supervisor_utilities = draw(st_single_utilities(fsize, ssize))

    affiliations = draw(st_affiliations(psize, fsize))
    project_capacities, supervisor_capacities = draw(st_capacities(psize, fsize, affiliations))

    return student_utilities, supervisor_utilities, affiliations, project_capacities, supervisor_capacities


@st.composite
def st_preferences_capacities(draw, smin=1, smax=5, pmin=1, pmax=5, fmin=1, fmax=3):
    """Create a set of preferences and capacities for a test."""
    ssize, psize, fsize = draw(st_sizes(smin, smax, pmin, pmax, fmin, fmax))

    students = [f"S{s}" for s in range(ssize)]
    projects = [f"P{p}" for p in range(psize)]
    supervisors = [f"F{f}" for f in range(fsize)]

    student_preferences = {s: draw(st.permutations(projects)) for s in students}
    supervisor_preferences = {f: draw(st.permutations(students)) for f in supervisors}

    affiliation_array = draw(st_affiliations(psize, fsize))
    affiliations = {proj: supervisors[aff] for proj, aff in zip(projects, affiliation_array)}

    project_cap_array, supervisor_cap_array = draw(st_capacities(psize, fsize, affiliation_array))
    project_capacities = dict(zip(projects, project_cap_array))
    supervisor_capacities = dict(zip(supervisors, supervisor_cap_array))

    return student_preferences, supervisor_preferences, affiliations, project_capacities, supervisor_capacities
