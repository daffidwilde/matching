""" Tests for each algorithm on small example cases. """

import itertools
import numpy as np

from hypothesis import given, settings
from hypothesis.strategies import (
    dictionaries,
    integers,
    permutations,
    sampled_from,
)

from matching.algorithms import galeshapley, resident_hospital


@given(
    suitor_preferences=dictionaries(
        keys=sampled_from(["A", "B", "C"]),
        values=permutations(["D", "E", "F"]),
        min_size=3,
        max_size=3,
    ),
    reviewer_preferences=dictionaries(
        keys=sampled_from(["D", "E", "F"]),
        values=permutations(["A", "B", "C"]),
        min_size=3,
        max_size=3,
    ),
)
def test_galeshapley(suitor_preferences, reviewer_preferences):
    """ Assert that the Gale-Shapley algorithm produces a valid solution to an
    uncapacitated matching game. """

    matching = galeshapley(suitor_preferences, reviewer_preferences)

    assert set(suitor_preferences.keys()) == set(matching.keys())
    assert set(reviewer_preferences.keys()) == set(matching.values())

    for suitor, reviewer in matching.items():
        assert suitor and reviewer


def _get_inputs(values):
    """ Generate the list of all possible ordered subsets of values. """

    power_set = set(
        [
            tuple(set(prod))
            for prod in itertools.product(values, repeat=len(values))
        ]
    )
    power_perms = [itertools.permutations(comb) for comb in power_set]

    ordered_power_set = []
    for perm in power_perms:
        for item in perm:
            ordered_power_set.append(list(item))

    return ordered_power_set


def _make_hospital_prefs(resident_prefs):

    hospitals = []
    for val in resident_prefs.values():
        for item in val:
            if item not in hospitals:
                hospitals.append(item)

    hospital_prefs = {
        h: np.random.permutation(
            [r for r in resident_prefs if h in resident_prefs[r]]
        ).tolist()
        for h in hospitals
    }

    return hospital_prefs


@given(
    resident_preferences=dictionaries(
        keys=sampled_from(["A", "B", "C", "D"]),
        values=sampled_from(_get_inputs(["X", "Y", "Z"])),
        min_size=4,
        max_size=4,
    ),
    capacities=dictionaries(
        keys=sampled_from(["X", "Y", "Z"]),
        values=integers(min_value=1),
        min_size=3,
        max_size=3,
    ),
    seed=integers(min_value=0),
)
@settings(deadline=None)
def test_extended_galeshapley(resident_preferences, capacities, seed):
    """ Example used on the NRMP website for the capacitated Gale-Shapley
    algorithm. Again, this example is easily solved on paper. """

    if all(resident_preferences.values()):
        np.random.seed(seed)

        hospital_preferences = _make_hospital_prefs(resident_preferences)
        matching = resident_hospital(
            resident_preferences, hospital_preferences, capacities
        )

        # assert set(resident_preferences.keys()) == set(matching.values())
        assert set(hospital_preferences.keys()) == set(matching.keys())
    else:
        pass
