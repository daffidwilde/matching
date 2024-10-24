"""Unit tests for the HospitalResident class."""

from hypothesis import given

from matching.games import HospitalResident

from ..common import mocked_game
from .strategies import st_ranks_capacities


@given(st_ranks_capacities())
def test_init(ranks_capacities):
    """Check instantiation given some rankings and capacities."""

    resident_ranks, hospital_ranks, capacities = ranks_capacities
    game = mocked_game(HospitalResident, *ranks_capacities)

    assert (game.resident_ranks == resident_ranks).all()
    assert (game.hospital_ranks == hospital_ranks).all()
    assert (game.capacities == capacities).all()

    assert game.num_residents == len(resident_ranks)
    assert game.num_hospitals == len(hospital_ranks)
    assert game.matching is None
    assert game._preference_lookup is None
