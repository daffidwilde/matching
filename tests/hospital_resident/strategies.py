"""Composite strategies for HR unit tests."""

import numpy as np
from hypothesis import strategies as st

from ..common import st_single_ranks, st_single_utilities


@st.composite
def st_sizes(draw, hmin, hmax, rmin, rmax):
    """Create sizes for the resident and hospital sets."""

    hsize = draw(st.integers(hmin, hmax))
    rsize = draw(st.integers(rmin, rmax))

    return hsize, rsize


@st.composite
def st_capacities(draw, size):
    """Create a capacity vector."""

    capacities = draw(st.lists(st.integers(1, 3), min_size=size, max_size=size))

    return np.array(capacities)


@st.composite
def st_ranks_capacities(draw, hmin=1, hmax=3, rmin=1, rmax=5):
    """Create a set of rankings and capacities for a test."""

    hsize, rsize = draw(st_sizes(hmin, hmax, rmin, rmax))

    resident_ranks = draw(st_single_ranks(rsize, hsize))
    hospital_ranks = draw(st_single_ranks(hsize, rsize))
    capacities = draw(st_capacities(hsize))

    return resident_ranks, hospital_ranks, capacities


@st.composite
def st_utilities_capacities(draw, hmin=1, hmax=3, rmin=1, rmax=5):
    """Create a set of utilities and capacities for a test."""

    hsize, rsize = draw(st_sizes(hmin, hmax, rmin, rmax))

    resident_utility = draw(st_single_utilities(rsize, hsize))
    hospital_utility = draw(st_single_utilities(hsize, rsize))
    capacities = draw(st_capacities(hsize))

    return resident_utility, hospital_utility, capacities


@st.composite
def st_preferences_capacities(draw, hmin=1, hmax=3, rmin=1, rmax=5):
    """Create a set of preferences and capacities for a test."""

    hsize, rsize = draw(st_sizes(hmin, hmax, rmin, rmax))

    residents = draw(st.lists(st.integers(), min_size=rsize, max_size=rsize, unique=True))
    hospitals = draw(st.lists(st.text(), min_size=hsize, max_size=hsize, unique=True))

    resident_preferences = {r: draw(st.permutations(hospitals)) for r in residents}
    hospital_preferences = {h: draw(st.permutations(residents)) for h in hospitals}
    capacities = dict(zip(hospital_preferences, draw(st_capacities(hsize))))

    return resident_preferences, hospital_preferences, capacities


@st.composite
def st_preference_matchings(draw, hmin=1, hmax=3, rmin=1, rmax=5):
    """Create a set of preferences and a matching to go with them."""

    resident_preferences, hospital_preferences, capacities = draw(
        st_preferences_capacities(hmin, hmax, rmin, rmax)
    )

    matched_residents = draw(
        st.lists(st.sampled_from(list(resident_preferences.keys())), unique=True)
    )
    resident_matching = {}
    spaces = capacities.copy()
    for resident in matched_residents:
        resident_idx = list(resident_preferences.keys()).index(resident)
        hospital = draw(st.sampled_from(resident_preferences[resident]))
        hospital_idx = list(hospital_preferences.keys()).index(hospital)
        if spaces[hospital]:
            resident_matching[resident_idx] = hospital_idx
            spaces[hospital] -= 1

    matching = {
        hospital: [r for r in resident_matching if resident_matching[r] == hospital]
        for hospital, _ in enumerate(hospital_preferences)
        if hospital in resident_matching.values()
    }

    return resident_preferences, hospital_preferences, capacities, matching
