"""Tests for the Hospital-Resident algorithm."""

import numpy as np
from hypothesis import given

from matching.algorithms.hospital_resident import (
    hospital_optimal,
    hospital_resident,
    resident_optimal,
)

from .util import players


@given(players_=players())
def test_hospital_resident(players_):
    """Test the algorithm produces a valid solution."""

    residents, hospitals = players_

    matching = hospital_resident(residents, hospitals)
    assert set(hospitals) == set(matching.keys())

    matched_residents = {r for rs in matching.values() for r in rs}
    for resident in residents:
        if resident.matching:
            assert resident in matched_residents
        else:
            assert resident not in matched_residents


@given(players_=players())
def test_resident_optimal(players_):
    """Test that the resident-optimal algorithm is resident-optimal."""

    residents, hospitals = players_

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


@given(players_=players())
def test_hospital_optimal(players_):
    """Test that the hospital-optimal algorithm is hospital-optimal."""

    _, hospitals = players_

    matching = hospital_optimal(hospitals)
    assert set(hospitals) == set(matching.keys())

    for hospital, matches in matching.items():
        old_idx = -np.infty
        for resident in matches:
            idx = hospital.prefs.index(resident)
            assert idx >= old_idx
            old_idx = idx
