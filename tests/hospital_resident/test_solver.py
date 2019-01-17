""" Unit tests for the HR solver. """

import numpy as np
import pytest

from matching import HospitalResident, Matching

from .params import HOSPITAL_RESIDENT, _make_hospitals, _make_residents


@HOSPITAL_RESIDENT
def test_init(resident_names, hospital_names, capacities, seed):
    """ Test that an instance of HospitalResident is created correctly. """

    np.random.seed(seed)
    residents = _make_residents(resident_names, hospital_names)
    hospitals = _make_hospitals(residents, capacities)
    match = HospitalResident(residents, hospitals)

    assert match.suitors == residents
    assert match.reviewers == hospitals
    assert all(
        [suitor.matching is None for suitor in match.suitors]
    )
    assert all(
        [reviewer.matching == [] for reviewer in match.reviewers]
    )
    assert match.matching is None


@HOSPITAL_RESIDENT
def test_inputs_suitor_prefs(resident_names, hospital_names, capacities, seed):
    """ Test that each suitor's preference list is a subset of the available
    reviewer names, and check that an Exception is raised if not. """

    np.random.seed(seed)
    residents = _make_residents(resident_names, hospital_names)
    hospitals = _make_hospitals(residents, capacities)
    match = HospitalResident(residents, hospitals)

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

    np.random.seed(seed)
    residents = _make_residents(resident_names, hospital_names)
    hospitals = _make_hospitals(residents, capacities)
    match = HospitalResident(residents, hospitals)

    assert match._check_reviewer_prefs()

    match.reviewers[0].pref_names.pop()

    with pytest.raises(Exception):
        match._check_reviewer_prefs()


@HOSPITAL_RESIDENT
def test_solve(resident_names, hospital_names, capacities, seed):
    """ Test that HospitalResident can solve games correctly. """

    np.random.seed(seed)
    residents = _make_residents(resident_names, hospital_names)
    hospitals = _make_hospitals(residents, capacities)
    match = HospitalResident(residents, hospitals)

    for optimal in ["suitor", "resident", "reviewer", "hospital"]:
        matching = match.solve(optimal)
        assert isinstance(matching, Matching)
        assert set(matching.keys()) == set(hospitals)
        matched_residents = [
            res for match in matching.values() for res in match
        ]
        assert (
            matched_residents != []
            and set(matched_residents).issubset(set(residents))
        )

        for resident in set(residents) - set(matched_residents):
            assert resident.matching is None
