"""Unit tests for the Hospital-Resident algorithms."""

import numpy as np
from hypothesis import given

from matching.games import HospitalResident

from ..common import mocked_game
from .strategies import st_ranks_capacities


def _assert_matching_is_valid_shape(matching, hospital_ranks, resident_ranks, capacities):
    """Assert that the matching has the right shape and elements."""
    assert isinstance(matching, dict)

    matched_hospitals = set(matching.keys())
    matched_residents = set([r for rs in matching.values() for r in rs])

    assert matched_hospitals <= set(np.unique(resident_ranks))
    assert matched_residents <= set(np.unique(hospital_ranks))

    for hospital, residents in matching.items():
        assert len(residents) <= capacities[hospital]


@given(st_ranks_capacities())
def test_resident_optimal_resident_optimal(ranks_capacities):
    """
    Check the resident-optimal algorithm is optimal for residents.

    We affirm this by going through the residents and checking that
    either they are unmatched or they prefer their match to any other
    hospital.
    """
    resident_ranks, hospital_ranks, capacities = ranks_capacities
    game = mocked_game(HospitalResident, *ranks_capacities)

    matching = game._resident_optimal()

    _assert_matching_is_valid_shape(matching, hospital_ranks, resident_ranks, capacities)

    for resident, resident_rank in enumerate(game.resident_ranks):
        hospital = next((h for h, rs in matching.items() if resident in rs), None)
        if hospital is None:
            continue

        preferred_hospitals, *_ = np.where(resident_rank < resident_rank[hospital])
        assert not preferred_hospitals.any()


@given(st_ranks_capacities())
def test_resident_optimal_hospital_pessimal(ranks_capacities):
    """
    Check the resident-optimal algorithm is pessimal for hospitals.

    We affirm this by going through the hospitals and checking that if
    they prefer a resident to their worst current match, then the
    resident matched to them already or prefers their match to the
    hospital.
    """
    resident_ranks, hospital_ranks, capacities = ranks_capacities
    game = mocked_game(HospitalResident, *ranks_capacities)

    matching = game._resident_optimal()

    _assert_matching_is_valid_shape(matching, hospital_ranks, resident_ranks, capacities)

    for hospital, residents in matching.items():
        if not residents:
            continue

        hospital_rank = game.hospital_ranks[hospital]
        worst_match = hospital_rank[residents].max()
        preferred_residents, *_ = np.where(hospital_rank < worst_match)
        for preferred in preferred_residents:
            if preferred in residents:
                continue

            preferred_rank = game.resident_ranks[preferred]
            partner = next((h for h, rs in matching.items() if preferred in rs), None)

            assert partner is not None
            assert preferred_rank[partner] < preferred_rank[hospital]


@given(st_ranks_capacities())
def test_hospital_optimal_hospital_optimal(ranks_capacities):
    """
    Check the hospital-optimal algorithm is optimal for hospitals.

    We affirm this by going through the matching and checking that for
    each hospital, if they prefer a resident to their best current
    match, then the resident prefers their match to the hospital.
    """
    resident_ranks, hospital_ranks, capacities = ranks_capacities
    game = mocked_game(HospitalResident, *ranks_capacities)

    matching = game._hospital_optimal()

    _assert_matching_is_valid_shape(matching, hospital_ranks, resident_ranks, capacities)

    for hospital, residents in matching.items():
        if not residents:
            continue

        hospital_rank = game.hospital_ranks[hospital]
        best_match = hospital_rank[residents].min()
        preferred_residents, *_ = np.where(hospital_rank < best_match)
        for preferred in preferred_residents:
            preferred_rank = game.resident_ranks[preferred]
            partner = next((h for h, rs in matching.items() if preferred in rs), None)

            assert partner is not None
            assert preferred_rank[partner] < preferred_rank[hospital]


@given(st_ranks_capacities())
def test_hospital_optimal_resident_pessimal(ranks_capacities):
    """
    Check the hospital-optimal algorithm is pessimal for residents.

    We affirm this by going through the residents and checking that if
    they prefer a hospital to their current match, then the hospital
    prefers their worst match to the resident.
    """
    resident_ranks, hospital_ranks, capacities = ranks_capacities
    game = mocked_game(HospitalResident, *ranks_capacities)

    matching = game._hospital_optimal()

    _assert_matching_is_valid_shape(matching, hospital_ranks, resident_ranks, capacities)

    for resident, resident_rank in enumerate(game.resident_ranks):
        hospital = next((h for h, rs in matching.items() if resident in rs), None)
        if hospital is None:
            continue

        preferred_hospitals, *_ = np.where(resident_rank < resident_rank[hospital])
        for preferred in preferred_hospitals:
            preferred_matches = matching.get(preferred)
            assert preferred_matches is not None

            preferred_rank = game.hospital_ranks[preferred]
            worst_match = preferred_rank[preferred_matches].max()
            assert preferred_rank[resident] > worst_match
