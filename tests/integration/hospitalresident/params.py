""" Useful functions and decorators for the HR tests. """

import itertools as it
import numpy as np

from hypothesis import given
from hypothesis.strategies import dictionaries, integers, sampled_from, sets

from matching import Player


def get_possible_prefs(values):
    """ Generate the list of all possible preference lists made from values."""

    all_ordered_subsets = set(
        [tuple(set(sub)) for sub in it.product(values, repeat=len(values))]
    )

    possible_prefs = [
        list(perm)
        for sub in all_ordered_subsets
        for perm in it.permutations(sub)
    ]

    return possible_prefs


def make_residents(resident_names, hospital_names):
    """ Given some names, make a valid set of residents. """

    possible_preferences = get_possible_prefs(hospital_names)
    residents = [
        Player(
            name,
            possible_preferences[
                np.random.choice(range(len(possible_preferences)))
            ],
        )
        for name in resident_names
    ]

    return sorted(residents, key=lambda res: res.name)


def make_hospitals(residents, capacities):
    """ Given some residents, make a valid set of hospitals. """

    available_hospital_names = set([h for r in residents for h in r.pref_names])

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


HOSPITAL_RESIDENT = given(
    resident_names=sets(
        elements=sampled_from(["A", "B", "C", "D"]), min_size=1, max_size=4
    ),
    hospital_names=sets(
        elements=sampled_from(["X", "Y", "Z"]), min_size=1, max_size=3
    ),
    capacities=dictionaries(
        keys=sampled_from(["X", "Y", "Z"]),
        values=integers(min_value=2),
        min_size=3,
        max_size=3,
    ),
    seed=integers(min_value=0),
)
