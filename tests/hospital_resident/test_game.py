"""Unit tests for the HospitalResident class."""

from unittest import mock

import numpy as np
from hypothesis import given

from matching.games import HospitalResident

from ..common import mocked_game
from .strategies import (
    st_preferences_capacities,
    st_ranks_capacities,
    st_utilities_capacities,
)


@given(st_ranks_capacities())
def test_init(ranks_capacities):
    """Check instantiation given some rankings and capacities."""

    resident_ranks, hospital_ranks, capacities = ranks_capacities
    game = mocked_game(HospitalResident, *ranks_capacities)

    assert isinstance(game, HospitalResident)
    assert (game.resident_ranks == resident_ranks).all()
    assert (game.hospital_ranks == hospital_ranks).all()
    assert (game.capacities == capacities).all()

    assert game.num_residents == len(resident_ranks)
    assert game.num_hospitals == len(hospital_ranks)
    assert game.matching is None
    assert game._preference_lookup is None


@given(st_utilities_capacities())
def test_from_utilities(utilities_capacities):
    """Check instantiation from utility matrices."""

    *utilities, capacities = utilities_capacities
    resident_utility, hospital_utility = utilities

    with (
        mock.patch(
            "matching.games.HospitalResident.check_input_validity"
        ) as validator,
        mock.patch("matching.convert.utility_to_rank") as ranker,
    ):
        effects = (resident_utility.argsort(), hospital_utility.argsort())
        ranker.side_effect = list(effects)
        game = HospitalResident.from_utilities(
            resident_utility, hospital_utility, capacities
        )

    assert isinstance(game, HospitalResident)
    assert (game.resident_ranks == effects[0]).all()
    assert (game.hospital_ranks == effects[1]).all()
    assert (game.capacities == capacities).all()

    assert game.num_residents == len(resident_utility)
    assert game.num_hospitals == len(hospital_utility)
    assert game.matching is None
    assert game._preference_lookup is None

    assert ranker.call_count == 2
    for call, utility in zip(ranker.call_args_list, utilities):
        arg, *_ = call.args
        assert np.array_equal(arg, utility)

    validator.assert_called_once_with()


@given(st_preferences_capacities())
def test_from_preferences(preferences_capacities):
    """Check instantiation from preference list dictionaries."""

    *preferences, capacities = preferences_capacities
    resident_preferences, hospital_preferences = preferences

    with (
        mock.patch(
            "matching.games.HospitalResident.check_input_validity"
        ) as validator,
        mock.patch("matching.convert.preference_to_rank") as ranker,
    ):
        effects = (
            np.array(list(resident_preferences.values())),
            np.array(list(hospital_preferences.values())),
        )
        ranker.side_effect = list(effects)
        game = HospitalResident.from_preferences(
            resident_preferences, hospital_preferences, capacities
        )

    assert isinstance(game, HospitalResident)
    assert (game.resident_ranks == effects[0]).all()
    assert (game.hospital_ranks == effects[1]).all()

    assert game.num_residents == len(resident_preferences)
    assert game.num_hospitals == len(hospital_preferences)
    assert game.matching is None

    assert isinstance(game._preference_lookup, dict)
    assert game._preference_lookup == {
        "residents": sorted(resident_preferences),
        "hospitals": sorted(hospital_preferences),
    }

    assert isinstance(game.capacities, np.ndarray)
    assert game.capacities.shape == (len(hospital_preferences),)
    for cap, hospital in zip(
        game.capacities, game._preference_lookup["hospitals"]
    ):
        assert cap == capacities.get(hospital)

    assert ranker.call_count == 2
    for call, preference, others in zip(
        ranker.call_args_list,
        preferences,
        (hospital_preferences, resident_preferences),
    ):
        assert call.args == (preference, sorted(others))

    validator.assert_called_once_with()
