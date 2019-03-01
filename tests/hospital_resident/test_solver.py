""" Unit tests for the HR solver. """

import numpy as np
import pytest

from matching import HospitalResident, Matching, Player

from .params import HOSPITAL_RESIDENT, _make_match


@HOSPITAL_RESIDENT
def test_init(resident_names, hospital_names, capacities, seed):
    """ Test that an instance of HospitalResident is created correctly. """

    residents, hospitals, match = _make_match(
        resident_names, hospital_names, capacities, seed
    )

    assert match.residents == residents
    assert match.hospitals == hospitals
    assert all([resident.matching is None for resident in match.residents])
    assert all([hospital.matching == [] for hospital in match.hospitals])
    assert match.matching is None


@HOSPITAL_RESIDENT
def test_inputs_resident_prefs(resident_names, hospital_names, capacities, seed):
    """ Test that each resident's preference list is a subset of the available
    hospital names, and check that an Exception is raised if not. """

    _, _, match = _make_match(resident_names, hospital_names, capacities, seed)

    assert match._check_resident_prefs()

    match.residents[0].pref_names = [1, 2, 3]

    with pytest.raises(Exception):
        match._check_resident_prefs()


@HOSPITAL_RESIDENT
def test_inputs_hospital_prefs(
    resident_names, hospital_names, capacities, seed
):
    """ Test that each hospital has ranked all and only those residents that have
    ranked it, and check that an Exception is raised if not. """

    _, _, match = _make_match(resident_names, hospital_names, capacities, seed)

    assert match._check_hospital_prefs()

    match.hospitals[0].pref_names.pop()

    with pytest.raises(Exception):
        match._check_hospital_prefs()


@HOSPITAL_RESIDENT
def test_solve(resident_names, hospital_names, capacities, seed):
    """ Test that HospitalResident can solve games correctly. """

    for optimal in ["resident", "resident", "hospital", "hospital"]:
        residents, hospitals, match = _make_match(
            resident_names, hospital_names, capacities, seed
        )

        matching = match.solve(optimal)
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

    _, _, match = _make_match(resident_names, hospital_names, capacities, seed)

    match.solve()
    assert match.check_validity()


@HOSPITAL_RESIDENT
def test_resident_matching(resident_names, hospital_names, capacities, seed):
    """ Test that HospitalResident recognises a valid matching requires a resident
    to have a preference of their match, if they have one. """

    _, _, match = _make_match(resident_names, hospital_names, capacities, seed)

    match.solve()
    match.residents[0].matching = Player(name="foo", pref_names=[])

    with pytest.raises(Exception):
        match._check_resident_matching()


@HOSPITAL_RESIDENT
def test_hospital_matching(resident_names, hospital_names, capacities, seed):
    """ Test that HospitalResident recognises a valid matching requires a
    hospital to have a preference of each of its matches, if any. """

    _, _, match = _make_match(resident_names, hospital_names, capacities, seed)

    match.solve()
    match.hospitals[0].matching.append(Player(name="foo", pref_names=[]))

    with pytest.raises(Exception):
        match._check_hospital_matching()


@HOSPITAL_RESIDENT
def test_hospital_capacity(resident_names, hospital_names, capacities, seed):
    """ Test that HospitalResident recognises a valid matching requires all
    hospitals to not be over-subscribed. """

    _, _, match = _make_match(resident_names, hospital_names, capacities, seed)

    match.solve()
    match.hospitals[0].matching = range(match.hospitals[0].capacity + 1)

    with pytest.raises(Exception):
        match._check_hospital_capacity()


def test_check_stability():
    """ Test that HospitalResident can recognise whether a matching is stable or
    not. """

    residents = [Player("A", [1, 2]), Player("B", [2]), Player("C", [2, 1])]
    hospitals = [Player(1, ["C", "A"], 3), Player(2, ["A", "B", "C"], 3)]
    match = HospitalResident(residents, hospitals)

    matching = match.solve()
    assert match.check_stability()

    (P_A, P_B, P_C), (P_1, P_2) = match.residents, match.hospitals
    matching[P_1] = [P_C]
    matching[P_2] = [P_A, P_B]

    assert not match.check_stability()
