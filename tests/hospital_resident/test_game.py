"""Unit tests for the HospitalResident class."""

import warnings
from unittest import mock

import numpy as np
import pytest
from hypothesis import given
from hypothesis import strategies as st

from matching import matchings
from matching.games import HospitalResident, hospital_resident

from ..common import mocked_game
from .strategies import (
    st_preference_matchings,
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
        mock.patch("matching.games.HospitalResident.check_input_validity") as validator,
        mock.patch("matching.convert.utility_to_rank") as ranker,
    ):
        effects = (resident_utility.argsort(), hospital_utility.argsort())
        ranker.side_effect = list(effects)
        game = HospitalResident.from_utilities(resident_utility, hospital_utility, capacities)

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
        mock.patch("matching.games.HospitalResident.check_input_validity") as validator,
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
    for cap, hospital in zip(game.capacities, game._preference_lookup["hospitals"]):
        assert cap == capacities.get(hospital)

    assert ranker.call_count == 2
    for call, preference, others in zip(
        ranker.call_args_list,
        preferences,
        (hospital_preferences, resident_preferences),
    ):
        assert call.args == (preference, sorted(others))

    validator.assert_called_once_with()


@given(st_ranks_capacities(), st.sampled_from(["resident", "hospital"]), st.booleans())
def test_solve(ranks_capacities, optimal, preference_lookup):
    """
    Check the solver works as it should.

    This method wraps the algorithm functions for the HR game, as well
    as the matching-preference conversion function. So, we mock all of
    these and check they are called correctly.
    """
    resident_ranks, hospital_ranks, capacities = ranks_capacities
    game = mocked_game(HospitalResident, *ranks_capacities)
    game._preference_lookup = preference_lookup

    with (
        mock.patch.object(game, "_resident_optimal") as mock_resident_optimal,
        mock.patch.object(game, "_hospital_optimal") as mock_hospital_optimal,
        mock.patch.object(game, "_convert_matching_to_preferences") as mock_convert,
        mock.patch.object(hospital_resident.matchings, "HRMatching") as mock_matching,
    ):
        matching = game.solve(optimal=optimal)

    assert matching == game.matching == mock_matching.return_value

    if optimal == "resident":
        mock_resident_optimal.assert_called_once_with()
        mock_hospital_optimal.assert_not_called()
        mock_matching.assert_called_once_with(
            mock_resident_optimal.return_value, keys="hospitals", values="residents"
        )
    if optimal == "hospital":
        mock_hospital_optimal.assert_called_once_with()
        mock_resident_optimal.assert_not_called()
        mock_matching.assert_called_once_with(
            mock_hospital_optimal.return_value, keys="hospitals", values="residents"
        )

    if preference_lookup:
        mock_convert.assert_called_once_with()
    else:
        mock_convert.assert_not_called()


@given(st_ranks_capacities(), st.text(min_size=1))
def test_solve_raises_with_bad_optimal(ranks_capacities, optimal):
    """Check that the solver raises an error with a bad optimal value."""
    resident_ranks, hospital_ranks, capacities = ranks_capacities
    game = mocked_game(HospitalResident, *ranks_capacities)

    with pytest.raises(ValueError, match="Invalid choice for `optimal`"):
        game.solve(optimal=optimal)


@given(st_preference_matchings())
def test_convert_matching_to_preferences(preference_matchings):
    """Test that a matching can use the terms from some preferences."""

    resident_prefs, hospital_prefs, capacities, matching = preference_matchings

    # the arrays here aren't used anywhere internally, just placeholders
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        game = HospitalResident.from_preferences(resident_prefs, hospital_prefs, capacities)

    game.matching = matchings.HRMatching(matching)

    game._convert_matching_to_preferences()
    converted = game.matching

    assert isinstance(converted, matchings.HRMatching)
    assert converted.keys_ == "hospitals"
    assert converted.values_ == "residents"

    assert set(converted.keys()) <= set(hospital_prefs)
    assert set([r for rs in converted.values() for r in rs]) <= set(resident_prefs)
