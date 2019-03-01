""" Hypothesis decorators for HR tests. """

import itertools as it

import numpy as np
from hypothesis import given
from hypothesis.strategies import dictionaries, integers, lists, sampled_from

from matching import HospitalResident, Player


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


def _make_residents(resident_names, hospital_names):
    """ Given some names, make a valid set of residents. """

    possible_prefs = _get_possible_prefs(hospital_names)
    residents = [
        Player(
            name, possible_prefs[np.random.choice(range(len(possible_prefs)))]
        )
        for name in resident_names
    ]

    return sorted(residents, key=lambda res: res.name)


def _make_hospitals(residents, capacities):
    """ Given some residents and capacities, make a valid set of hospitals. """

    available_hospital_names = {h for r in residents for h in r.pref_names}

    hospitals = [
        Player(
            name,
            np.random.permutation(
                [r.name for r in residents if name in r.pref_names]
            ).tolist(),
            capacities[name],
        )
        for name in available_hospital_names
    ]

    return sorted(hospitals, key=lambda hosp: hosp.name)


def _make_match(resident_names, hospital_names, capacities, seed):
    """ Make all of the residents and hospitals, and the match itself. """

    np.random.seed(seed)
    residents = _make_residents(resident_names, hospital_names)
    hospitals = _make_hospitals(residents, capacities)
    match = HospitalResident(residents, hospitals)

    return residents, hospitals, match


HOSPITAL_RESIDENT = given(
    resident_names=lists(
        elements=sampled_from(["A", "B", "C", "D"]),
        min_size=1,
        max_size=4,
        unique=True,
    ),
    hospital_names=lists(
        elements=sampled_from(["X", "Y", "Z"]),
        min_size=1,
        max_size=3,
        unique=True,
    ),
    capacities=dictionaries(
        keys=sampled_from(["X", "Y", "Z"]),
        values=integers(min_value=2),
        min_size=3,
        max_size=3,
    ),
    seed=integers(min_value=0, max_value=2 ** 32 - 1),
)
