""" Tests for the capacitated Gale-Shapley algorithm. """

import numpy as np

from matching.algorithms import hospitalresident
from .params import HOSPITAL_RESIDENT, make_hospitals, make_residents


@HOSPITAL_RESIDENT
def test_resident_optimal(resident_names, hospital_names, capacities, seed):
    """ Verify that the hospital-resident algorithm produces a valid,
    resident-optimal matching for an instance of HR. """

    np.random.seed(seed)
    residents = make_residents(resident_names, hospital_names)
    hospitals = make_hospitals(residents, capacities)
    matching = hospitalresident(residents, hospitals, optimal="resident")

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
    residents = make_residents(resident_names, hospital_names)
    hospitals = make_hospitals(residents, capacities)
    matching = hospitalresident(residents, hospitals, optimal="hospital")

    assert set(hospitals) == set(matching.keys())

    for hospital, matches in matching.items():
        old_idx = -np.infty
        for resident in matches:
            idx = hospital.pref_names.index(resident.name)
            assert idx >= old_idx
            old_idx = idx
