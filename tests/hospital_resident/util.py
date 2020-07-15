""" Toolbox for HR tests. """

import itertools as it
from collections import defaultdict

import numpy as np
from hypothesis import given
from hypothesis.strategies import (
    booleans, composite, integers, lists, permutations, sampled_from, text
)

from matching import Player as Resident
from matching.games import HospitalResident
from matching.players import Hospital


@composite
def names(draw, taken_from, size):
    """ A strategy for getting player names. """

    names = draw(lists(taken_from, min_size=size, max_size=size, unique=True))
    return names


@composite
def connections(
    draw,
    residents_from=text(),
    hospitals_from=text(),
    min_residents=1,
    max_residents=5,
    min_hospitals=1,
    max_hospitals=3,
):
    """ A custom strategy for making a set of connections between players. """

    num_residents = draw(integers(min_residents, max_residents))
    num_hospitals = draw(integers(min_hospitals, max_hospitals))

    resident_names = draw(names(residents_from, num_residents))
    hospital_names = draw(names(hospitals_from, num_hospitals))

    resident_prefs = {}
    hospital_prefs = {h: [] for h in hospital_names}
    for resident in resident_names:
        hospitals = draw(
            lists(sampled_from(hospital_names), min_size=1, unique=True)
        )
        resident_prefs[resident] = hospitals
        for hospital in hospitals:
            hospital_prefs[hospital].append(resident)

    capacities = {}
    for hospital, residents in list(hospital_prefs.items()):
        if residents:
            capacities[hospital] = draw(integers(min_residents, max_residents))
        else:
            del hospital_prefs[hospital]

    return resident_prefs, hospital_prefs, capacities


@composite
def players(draw, **kwargs):
    """ A custom strategy for making a set of residents and hospitals. """

    resident_prefs, hospital_prefs, capacities = draw(connections(**kwargs))

    residents = [Resident(name) for name in resident_prefs]
    hospitals = [Hospital(name, cap) for name, cap in capacities.items()]

    residents = _get_preferences(residents, hospitals, resident_prefs)
    hospitals = _get_preferences(hospitals, residents, hospital_prefs)

    return residents, hospitals


def _get_preferences(party, others, preferences):
    """ Get and assign preference instances. """

    for player in party:
        names = preferences[player.name]
        prefs = []
        for name in names:
            for other in others:
                if other.name == name:
                    prefs.append(other)
                    break

        player.set_prefs(prefs)

    return party


@composite
def games(draw, clean=booleans(), **kwargs):
    """ A custom strategy for making a game instance. """

    residents, hospitals = draw(players(**kwargs))

    return HospitalResident(residents, hospitals, clean)


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


def make_game(resident_names, hospital_names, capacities, seed, clean):
    """ Make all of the residents and hospitals, and the match itself. """

    np.random.seed(seed)
    residents, hospitals = make_players(
        resident_names, hospital_names, capacities
    )
    game = HospitalResident(residents, hospitals, clean)

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
    capacities=lists(
        elements=integers(min_value=2, max_value=4), min_size=3, max_size=3,
    ),
    seed=integers(min_value=0, max_value=2 ** 32 - 1),
    clean=booleans(),
)
