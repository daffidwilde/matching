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

    assert match.suitors == residents
    assert match.reviewers == hospitals
    assert all([suitor.matching is None for suitor in match.suitors])
    assert all([reviewer.matching == [] for reviewer in match.reviewers])
    assert match.matching is None


@HOSPITAL_RESIDENT
def test_inputs_suitor_prefs(resident_names, hospital_names, capacities, seed):
    """ Test that each suitor's preference list is a subset of the available
    reviewer names, and check that an Exception is raised if not. """

    _, _, match = _make_match(resident_names, hospital_names, capacities, seed)

    assert match._check_suitor_prefs()

    match.suitors[0].pref_names = [1, 2, 3]

    with pytest.raises(Exception):
        match._check_suitor_prefs()


@HOSPITAL_RESIDENT
def test_inputs_reviewer_prefs(
    resident_names, hospital_names, capacities, seed
):
    """ Test that each reviewer has ranked all and only those suitors that have
    ranked it, and check that an Exception is raised if not. """

    _, _, match = _make_match(resident_names, hospital_names, capacities, seed)

    assert match._check_reviewer_prefs()

    match.reviewers[0].pref_names.pop()

    with pytest.raises(Exception):
        match._check_reviewer_prefs()


@HOSPITAL_RESIDENT
def test_solve(resident_names, hospital_names, capacities, seed):
    """ Test that HospitalResident can solve games correctly. """

    for optimal in ["suitor", "resident", "reviewer", "hospital"]:
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
def test_suitor_matching(resident_names, hospital_names, capacities, seed):
    """ Test that HospitalResident recognises a valid matching requires a suitor
    to have a preference of their match, if they have one. """

    _, _, match = _make_match(resident_names, hospital_names, capacities, seed)

    match.solve()
    match.suitors[0].matching = Player(name="foo", pref_names=[])

    with pytest.raises(Exception):
        match._check_suitor_matching()


@HOSPITAL_RESIDENT
def test_reviewer_matching(resident_names, hospital_names, capacities, seed):
    """ Test that HospitalResident recognises a valid matching requires a
    reviewer to have a preference of each of its matches, if any. """

    _, _, match = _make_match(resident_names, hospital_names, capacities, seed)

    match.solve()
    match.reviewers[0].matching.append(Player(name="foo", pref_names=[]))

    with pytest.raises(Exception):
        match._check_reviewer_matching()


@HOSPITAL_RESIDENT
def test_reviewer_capacity(resident_names, hospital_names, capacities, seed):
    """ Test that HospitalResident recognises a valid matching requires all
    reviewers to not be over-subscribed. """

    _, _, match = _make_match(resident_names, hospital_names, capacities, seed)

    match.solve()
    match.reviewers[0].matching = range(match.reviewers[0].capacity + 1)

    with pytest.raises(Exception):
        match._check_reviewer_capacity()


def test_check_stability():
    """ Test that HospitalResident can recognise whether a matching is stable or
    not. """

    residents = [Player("A", [1, 2]), Player("B", [2]), Player("C", [2, 1])]
    hospitals = [Player(1, ["C", "A"], 3), Player(2, ["A", "B", "C"], 3)]
    match = HospitalResident(residents, hospitals)

    matching = match.solve()
    assert match.check_stability()

    (P_A, P_B, P_C), (P_1, P_2) = match.suitors, match.reviewers
    matching[P_1] = [P_C]
    matching[P_2] = [P_A, P_B]

    assert not match.check_stability()
