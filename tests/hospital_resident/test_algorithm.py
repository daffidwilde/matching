""" Tests for the Hospital-Resident algorithm. """

import numpy as np

from matching.algorithms.hospital_resident import (
    hospital_optimal, hospital_resident, resident_optimal
)

from .params import HOSPITAL_RESIDENT, make_players


@HOSPITAL_RESIDENT
def test_hospital_resident(
    resident_names, hospital_names, capacities, seed, clean
):
    """ Verify that the hospital-resident algorithm produces a valid solution
    for an instance of HR. """

    np.random.seed(seed)
    residents, hospitals = make_players(
        resident_names, hospital_names, capacities
    )
    matching = hospital_resident(residents, hospitals)

    assert set(hospitals) == set(matching.keys())

    matched_residents = {r for rs in matching.values() for r in rs}
    for resident in residents:
        if resident.matching:
            assert resident in matched_residents
        else:
            assert resident not in matched_residents


@HOSPITAL_RESIDENT
def test_resident_optimal(
    resident_names, hospital_names, capacities, seed, clean
):
    """ Verify that the resident-optimal algorithm produces a solution that is
    indeed resident-optimal. """

    np.random.seed(seed)
    residents, hospitals = make_players(
        resident_names, hospital_names, capacities
    )
    matching = resident_optimal(residents, hospitals)

    assert set(hospitals) == set(matching.keys())
    assert all(
        [
            r in set(residents)
            for r in {
                r_match for matches in matching.values() for r_match in matches
            }
        ]
    )

    for resident in residents:
        if resident.matching:
            assert resident.prefs.index(resident.matching) == 0


@HOSPITAL_RESIDENT
def test_hospital_optimal(
    resident_names, hospital_names, capacities, seed, clean
):
    """ Verify that the hospital-optimal algorithm produces a solution that is
    indeed hospital-optimal. """

    np.random.seed(seed)
    _, hospitals = make_players(
        resident_names, hospital_names, capacities
    )
    matching = hospital_optimal(hospitals)

    assert set(hospitals) == set(matching.keys())

    for hospital, matches in matching.items():
        old_idx = -np.infty
        for resident in matches:
            idx = hospital.prefs.index(resident)
            assert idx >= old_idx
            old_idx = idx
