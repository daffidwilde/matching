"""Strategies for HR tests."""

from hypothesis.strategies import (
    booleans,
    composite,
    integers,
    lists,
    sampled_from,
    text,
)

from matching import Player as Resident
from matching.games import HospitalResident
from matching.players import Hospital


@composite
def names(draw, taken_from, size):
    """A strategy for getting player names."""

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
    """A custom strategy for connecting players."""

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
    """A custom strategy for making a set of residents and hospitals."""

    resident_prefs, hospital_prefs, capacities = draw(connections(**kwargs))

    residents = [Resident(name) for name in resident_prefs]
    hospitals = [Hospital(name, cap) for name, cap in capacities.items()]

    residents = _get_preferences(residents, hospitals, resident_prefs)
    hospitals = _get_preferences(hospitals, residents, hospital_prefs)

    return residents, hospitals


def _get_preferences(party, others, preferences):
    """Get and assign preference instances."""

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
    """A custom strategy for making a game instance."""

    residents, hospitals = draw(players(**kwargs))
    return HospitalResident(residents, hospitals, draw(clean))
