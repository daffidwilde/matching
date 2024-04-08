"""Unit tests for the StableMarriage class."""

import warnings
from unittest import mock

import numpy as np
import pytest
from hypothesis import given

from matching.games import StableMarriage

from .strategies import (
    mocked_game,
    st_player_ranks,
    st_preferences,
    st_ranks,
    st_utilities,
)


@given(st_ranks())
def test_init(ranks):
    """Test for correct instantiation given some rankings."""

    suitor_ranks, reviewer_ranks = ranks
    game = mocked_game(suitor_ranks, reviewer_ranks)

    assert (game.suitor_ranks == suitor_ranks).all()
    assert (game.reviewer_ranks == reviewer_ranks).all()

    assert game.num_suitors == len(suitor_ranks)
    assert game.num_reviewers == len(reviewer_ranks)
    assert game.matching is None


@given(st_utilities())
def test_from_utilities(utilities):
    """Test the utility matrix builder."""

    suitor_utility, reviewer_utility = utilities

    with mock.patch(
        "matching.games.StableMarriage.check_input_validity"
    ) as validator, mock.patch("matching.convert.utility_to_rank") as ranker:
        effects = (suitor_utility.argsort(), reviewer_utility.argsort())
        ranker.side_effect = list(effects)
        game = StableMarriage.from_utilities(suitor_utility, reviewer_utility)

    assert isinstance(game, StableMarriage)
    assert (game.suitor_ranks == effects[0]).all()
    assert (game.reviewer_ranks == effects[1]).all()

    assert game.num_suitors == len(suitor_utility)
    assert game.num_reviewers == len(reviewer_utility)
    assert game.matching is None

    assert ranker.call_count == 2
    for call, utility in zip(ranker.call_args_list, utilities):
        arg, *_ = call.args
        assert np.array_equal(arg, utility)

    validator.assert_called_once_with()


@given(st_preferences())
def test_from_preferences(preferences):
    """Test the preference list builder."""

    suitor_prefs, reviewer_prefs = preferences

    with mock.patch(
        "matching.games.StableMarriage.check_input_validity"
    ) as validator, mock.patch(
        "matching.convert.preference_to_rank"
    ) as ranker:
        effects = (
            np.array(list(suitor_prefs.values())),
            np.array(list(reviewer_prefs.values())),
        )
        ranker.side_effect = list(effects)
        game = StableMarriage.from_preferences(suitor_prefs, reviewer_prefs)

    assert isinstance(game, StableMarriage)
    assert (game.suitor_ranks == effects[0]).all()
    assert (game.reviewer_ranks == effects[1]).all()

    assert game.num_suitors == len(suitor_prefs)
    assert game.num_reviewers == len(reviewer_prefs)
    assert game.matching is None

    assert ranker.call_count == 2
    for call, preference, others in zip(
        ranker.call_args_list,
        preferences,
        (reviewer_prefs.keys(), suitor_prefs.keys()),
    ):
        assert call.args == (preference, tuple(others))

    validator.assert_called_once_with()


@given(st_ranks())
def test_check_number_of_players_no_warning(ranks):
    """Test the number of players can be checked without warning."""

    game = mocked_game(*ranks)

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        game._check_number_of_players()


@given(st_ranks())
def test_check_number_of_players_warning(ranks):
    """Test for a warning when the player sets are not the same size."""

    suitor_ranks, reviewer_ranks = ranks
    suitor_ranks = np.vstack((suitor_ranks, suitor_ranks[-1][::-1]))

    game = mocked_game(suitor_ranks, reviewer_ranks)

    match = (
        r"^Number of suitors \(\d{1,2}\) "
        r"and reviewers \(\d{1,2}\) do not match."
    )
    with pytest.warns(UserWarning, match=match):
        game._check_number_of_players()


@given(st_player_ranks())
def test_check_player_ranks_no_warning(player_ranks):
    """Test the rank checker runs without warning for a valid set."""

    suitor_ranks, reviewer_ranks, player, ranks, side = player_ranks
    game = mocked_game(suitor_ranks, reviewer_ranks)

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        game._check_player_ranks(player, ranks, side)


@given(st_player_ranks())
def test_check_player_ranks_warning(player_ranks):
    """Test the rank checker gives a warning for an invalid set."""

    suitor_ranks, reviewer_ranks, player, ranks, side = player_ranks
    ranks[-1] = 1000

    game = mocked_game(suitor_ranks, reviewer_ranks)

    match = f"{side.title()} {player} has not strictly ranked"
    with pytest.warns(UserWarning, match=match):
        game._check_player_ranks(player, ranks, side)


def _zip_enumerated_ranks_with_side(ranks, side):
    """Attach the side to a list of enumerated rankings."""

    return ((i, rank, side) for i, rank in enumerate(ranks))


@given(st_ranks())
def test_check_input_validity(ranks):
    """Test the logic of the input validator."""

    suitor_ranks, reviewer_ranks = ranks
    game = mocked_game(*ranks)

    with mock.patch(
        "matching.games.StableMarriage._check_number_of_players"
    ) as check_num_players, mock.patch(
        "matching.games.StableMarriage._check_player_ranks"
    ) as check_player_ranks:
        game.check_input_validity()

    check_num_players.assert_called_once_with()

    assert check_player_ranks.call_count == (
        len(suitor_ranks) + len(reviewer_ranks)
    )

    suitor_args = _zip_enumerated_ranks_with_side(suitor_ranks, "suitor")
    reviewer_args = _zip_enumerated_ranks_with_side(reviewer_ranks, "reviewer")
    for call, (player, rank, side) in zip(
        check_player_ranks.call_args_list, [*suitor_args, *reviewer_args]
    ):
        call_player, call_rank, call_side = call.args
        assert call_player == player
        assert (call_rank == rank).all()

        assert call_side == side


@given(st_ranks())
def test_invert_player_sets(ranks):
    """Test that the player set attributes can be swapped."""

    suitor_ranks, reviewer_ranks = ranks
    game = mocked_game(*ranks)

    game._invert_player_sets()

    assert (game.suitor_ranks == reviewer_ranks).all()
    assert (game.reviewer_ranks == suitor_ranks).all()
    assert game.num_suitors == len(reviewer_ranks)
    assert game.num_reviewers == len(suitor_ranks)
