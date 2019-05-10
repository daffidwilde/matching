""" Toolbox for HR tests. """

import itertools as it
from collections import defaultdict

import numpy as np
from hypothesis import given
from hypothesis.strategies import integers, lists, sampled_from

from matching import Player as Resident
from matching.games import HospitalResident
from matching.players import Hospital


def make_players(resident_names, hospital_names, capacities):
    """ Given some names and capacities, make a set of players for HR. """

    residents = [Resident(name) for name in resident_names]
    hospitals = [
        Hospital(name, capacity)
        for name, capacity in zip(hospital_names, capacities)
    ]

    possible_prefs = get_possible_prefs(hospitals)
    logged_prefs = {}
    for resident in residents:
        prefs = possible_prefs[np.random.randint(len(possible_prefs))]
        resident.set_prefs(prefs)
        for hospital in prefs:
            try:
                logged_prefs[hospital] += [resident]
            except KeyError:
                logged_prefs[hospital] = [resident]

    for hospital, resids in logged_prefs.items():
        hospital.set_prefs(np.random.permutation(resids).tolist())

    return residents, [hosp for hosp in hospitals if hosp.prefs is not None]


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


def make_game(resident_names, hospital_names, capacities, seed):
    """ Make all of the residents and hospitals, and the match itself. """

    np.random.seed(seed)
    residents, hospitals = make_players(
        resident_names, hospital_names, capacities
    )
    game = HospitalResident(residents, hospitals)

    return residents, hospitals, game


def make_prefs(resident_names, hospital_names, seed):
    """ Make a valid set of preferences given a set of names. """

    np.random.seed(seed)
    resident_prefs, hospital_prefs = defaultdict(list), defaultdict(list)
    possible_prefs = get_possible_prefs(hospital_names)

    for resident in resident_names:
        prefs = possible_prefs[np.random.randint(len(possible_prefs))]
        resident_prefs[resident].extend(prefs)
        for hospital in prefs:
            hospital_prefs[hospital].append(resident)

    for hospital in hospital_prefs:
        np.random.shuffle(hospital_prefs[hospital])

    return resident_prefs, hospital_prefs


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
    capacities=lists(elements=integers(min_value=2), min_size=3, max_size=3),
    seed=integers(min_value=0, max_value=2 ** 32 - 1),
)
