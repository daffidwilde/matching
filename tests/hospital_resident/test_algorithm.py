""" Tests for the capacitated Gale-Shapley algorithm. """

import numpy as np

from matching.solvers import hospital_resident

from .params import HOSPITAL_RESIDENT, _make_hospitals, _make_residents


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
        if resident.matching:
            assert resident.pref_names.index(resident.matching.name) == 0


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
