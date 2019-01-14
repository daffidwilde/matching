""" Tests for the capacitated Gale-Shapley algorithm. """

import itertools as it

import numpy as np

from matching import Player
from matching.algorithms import hospital_resident

from .params import HOSPITAL_RESIDENT


def _get_possible_prefs(names):
    """ Generate the list of all possible non-empty preference lists made from a
    list of names. """

    all_ordered_subsets = set(
        [tuple(set(sub)) for sub in it.product(names, repeat=len(names))]
    )

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


@HOSPITAL_RESIDENT
def test_resident_optimal(resident_names, hospital_names, capacities, seed):
    """ Verify that the hospital-resident algorithm produces a valid,
    resident-optimal matching for an instance of HR. """

    np.random.seed(seed)
    residents = _make_residents(resident_names, hospital_names)
    hospitals = _make_hospitals(residents, capacities)
    matching = hospital_resident(residents, hospitals, optimal="resident")

    assert set(hospitals) == set(matching.keys())
    assert all(
        [
            r in set(residents)
            for r in set(
                [
                    r_match
                    for matches in matching.values()
                    for r_match in matches
                ]
            )
        ]
    )

    for resident in residents:
        if resident.match:
            assert resident.pref_names.index(resident.match.name) == 0


@HOSPITAL_RESIDENT
def test_hospital_optimal(resident_names, hospital_names, capacities, seed):
    """ Verify that the hospital-resident algorithm produces a valid,
    hospital-optimal matching for an instance of HR. """

    np.random.seed(seed)
    residents = _make_residents(resident_names, hospital_names)
    hospitals = _make_hospitals(residents, capacities)
    matching = hospital_resident(residents, hospitals, optimal="hospital")

    assert set(hospitals) == set(matching.keys())

    for hospital, matches in matching.items():
        old_idx = -np.infty
        for resident in matches:
            idx = hospital.pref_names.index(resident.name)
            assert idx >= old_idx
            old_idx = idx
