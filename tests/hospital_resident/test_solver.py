""" Unit tests for the HR solver. """

import pytest

from matching import Matching
from matching import Player as Resident
from matching.games import HospitalResident
from matching.players import Hospital

from .params import HOSPITAL_RESIDENT, make_game


@HOSPITAL_RESIDENT
def test_init(resident_names, hospital_names, capacities, seed):
    """ Test that an instance of HospitalResident is created correctly. """

    residents, hospitals, game = make_game(
        resident_names, hospital_names, capacities, seed
    )

    assert game.residents == residents
    assert game.hospitals == hospitals
    assert all([resident.matching is None for resident in game.residents])
    assert all([hospital.matching == [] for hospital in game.hospitals])
    assert game.matching is None


@HOSPITAL_RESIDENT
def test_inputs_resident_prefs(
    resident_names, hospital_names, capacities, seed
):
    """ Test that each resident's preference list is a subset of the available
    hospitals, and check that an Exception is raised if not. """

    _, _, game = make_game(resident_names, hospital_names, capacities, seed)

    assert game._check_resident_prefs()

    game.residents[0].prefs = [Resident("foo")]

    with pytest.raises(Exception):
        game._check_resident_prefs()


@HOSPITAL_RESIDENT
def test_inputs_hospital_prefs(
    resident_names, hospital_names, capacities, seed
):
    """ Test that each hospital has ranked all and only those residents that
    have ranked it, and check that an Exception is raised if not. """

    _, _, game = make_game(resident_names, hospital_names, capacities, seed)

    assert game._check_hospital_prefs()

    game.hospitals[0].prefs.pop()

    with pytest.raises(Exception):
        game._check_hospital_prefs()


@HOSPITAL_RESIDENT
def test_solve(resident_names, hospital_names, capacities, seed):
    """ Test that HospitalResident can solve games correctly. """

    for optimal in ["resident", "hospital"]:
        residents, hospitals, game = make_game(
            resident_names, hospital_names, capacities, seed
        )

        matching = game.solve(optimal)
        assert isinstance(matching, Matching)
        assert set(matching.keys()) == set(hospitals)
        matched_residents = [
            res for match in matching.values() for res in match
        ]
        assert matched_residents != [] and set(matched_residents).issubset(
            set(residents)
        )

        for resident in set(residents) - set(matched_residents):
            assert resident.matching is None


@HOSPITAL_RESIDENT
def test_check_validity(resident_names, hospital_names, capacities, seed):
    """ Test that HospitalResident finds a valid matching when the game is
    solved. """

    _, _, game = make_game(resident_names, hospital_names, capacities, seed)

    game.solve()
    assert game.check_validity()


@HOSPITAL_RESIDENT
def test_resident_matching(resident_names, hospital_names, capacities, seed):
    """ Test that HospitalResident recognises a valid matching requires a resident
    to have a preference of their match, if they have one. """

    _, _, game = make_game(resident_names, hospital_names, capacities, seed)

    game.solve()
    game.residents[0].matching = Resident(name="foo")

    with pytest.raises(Exception):
        game._check_resident_matching()


@HOSPITAL_RESIDENT
def test_hospital_matching(resident_names, hospital_names, capacities, seed):
    """ Test that HospitalResident recognises a valid matching requires a
    hospital to have a preference of each of its matches, if any. """

    _, _, game = make_game(resident_names, hospital_names, capacities, seed)

    game.solve()
    game.hospitals[0].matching.append(Resident(name="foo"))

    with pytest.raises(Exception):
        game._check_hospital_matching()


@HOSPITAL_RESIDENT
def test_hospital_capacity(resident_names, hospital_names, capacities, seed):
    """ Test that HospitalResident recognises a valid matching requires all
    hospitals to not be over-subscribed. """

    _, _, game = make_game(resident_names, hospital_names, capacities, seed)

    game.solve()
    game.hospitals[0].matching = range(game.hospitals[0].capacity + 1)

    with pytest.raises(Exception):
        game._check_hospital_capacity()


def test_check_stability():
    """ Test that HospitalResident can recognise whether a matching is stable or
    not. """

    residents = [Resident("A"), Resident("B"), Resident("C")]
    hospitals = [Hospital("X", 2), Hospital("Y", 2)]

    a, b, c = residents
    x, y = hospitals

    a.set_prefs([x, y])
    b.set_prefs([y])
    c.set_prefs([y, x])

    x.set_prefs([c, a])
    y.set_prefs([a, b, c])

    game = HospitalResident(residents, hospitals)

    matching = game.solve()
    assert game.check_stability()

    matching[x] = [c]
    matching[y] = [a, b]

    assert not game.check_stability()
