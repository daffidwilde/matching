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
def test_inputs_resident_prefs(
    resident_names, hospital_names, capacities, seed
):
    """ Test that each resident's (suitor's) preference list is a subset of the
    available reviewer names, and check that a ValueError is raised if not. """

    np.random.seed(seed)
    residents = _make_residents(resident_names, hospital_names)
    hospitals = _make_hospitals(residents, capacities)
    match = HospitalResident(residents, hospitals)

    assert match._check_resident_prefs()

    match.suitors[0].pref_names = [1, 2, 3]

    with pytest.raises(ValueError):
        match._check_resident_prefs()
