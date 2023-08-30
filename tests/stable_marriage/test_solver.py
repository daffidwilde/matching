"""Unit tests for the SM solver."""

import pytest

from matching import Player, SingleMatching
from matching.exceptions import MatchingError
from matching.games import StableMarriage

from .util import STABLE_MARRIAGE, make_players, make_prefs


@STABLE_MARRIAGE
def test_init(player_names, seed):
    """Test for correct instantiation given a set of players."""

    suitors, reviewers = make_players(player_names, seed)
    game = StableMarriage(suitors, reviewers)

    for player, game_player in zip(
        suitors + reviewers, game.suitors + game.reviewers
    ):
        assert player.name == game_player.name
        assert player._pref_names == game_player._pref_names

    assert all(
        [player.matching is None for player in game.suitors + game.reviewers]
    )
    assert game.matching is None


@STABLE_MARRIAGE
def test_create_from_dictionaries(player_names, seed):
    """Test for correct instantiation given a set of dictionaries."""

    suitor_prefs, reviewer_prefs = make_prefs(player_names, seed)
    game = StableMarriage.create_from_dictionaries(
        suitor_prefs, reviewer_prefs
    )

    for suitor in game.suitors:
        assert suitor_prefs[suitor.name] == suitor._pref_names
        assert suitor.matching is None

    for reviewer in game.reviewers:
        assert reviewer_prefs[reviewer.name] == reviewer._pref_names
        assert reviewer.matching is None

    assert game.matching is None


@STABLE_MARRIAGE
def test_inputs_num_players(player_names, seed):
    """Test for error when the player sets are not the same size."""

    suitors, reviewers = make_players(player_names, seed)
    game = StableMarriage(suitors, reviewers)

    assert game._check_num_players()

    suitors = suitors[:-1]

    with pytest.raises(ValueError):
        StableMarriage(suitors, reviewers)


@STABLE_MARRIAGE
def test_inputs_player_ranks(player_names, seed):
    """Test for error when a player has incomplete preferences."""

    suitors, reviewers = make_players(player_names, seed)
    game = StableMarriage(suitors, reviewers)

    for player in game.suitors + game.reviewers:
        assert game._check_player_ranks(player)

    suitors[0].prefs = suitors[0].prefs[:-1]

    with pytest.raises(ValueError):
        StableMarriage(suitors, reviewers)


@STABLE_MARRIAGE
def test_solve(player_names, seed):
    """Test that the class solves games correctly."""

    for optimal in ["suitor", "reviewer"]:
        suitors, reviewers = make_players(player_names, seed)
        game = StableMarriage(suitors, reviewers)

        matching = game.solve(optimal)
        assert isinstance(matching, SingleMatching)

        suitors = sorted(suitors, key=lambda s: s.name)
        reviewers = sorted(reviewers, key=lambda r: r.name)

        matching_keys = sorted(matching.keys(), key=lambda k: k.name)
        matching_values = sorted(matching.values(), key=lambda v: v.name)

        for game_suitor, suitor in zip(matching_keys, suitors):
            assert game_suitor.name == suitor.name
            assert game_suitor._pref_names == suitor._pref_names

        for game_reviewer, reviewer in zip(matching_values, reviewers):
            assert game_reviewer.name == reviewer.name
            assert game_reviewer._pref_names == reviewer._pref_names


@STABLE_MARRIAGE
def test_check_validity(player_names, seed):
    """Test for a valid matching when the game is solved."""

    suitors, reviewers = make_players(player_names, seed)
    game = StableMarriage(suitors, reviewers)

    game.solve()
    assert game.check_validity()


@STABLE_MARRIAGE
def test_check_for_unmatched_players(player_names, seed):
    """Test that all players must be matched to another player."""

    suitors, reviewers = make_players(player_names, seed)
    game = StableMarriage(suitors, reviewers)
    game.solve()

    player = game.suitors[0]
    player.matching = None

    with pytest.raises(MatchingError) as e:
        game.check_validity()
        error = e.unmatched_players[0]
        assert error.startswith(player.name)


@STABLE_MARRIAGE
def test_check_for_players_not_in_matching(player_names, seed):
    """Test that all players must be matched in the matching."""

    suitors, reviewers = make_players(player_names, seed)
    game = StableMarriage(suitors, reviewers)
    matching = game.solve()

    player = game.suitors[0]
    matching[player] = None

    with pytest.raises(MatchingError) as e:
        game.check_validity()
        error = e.players[0]
        assert error.startswith(player.name)


@STABLE_MARRIAGE
def test_matching_consistent(player_names, seed):
    """Test that the game's matching must match the players' matches."""

    suitors, reviewers = make_players(player_names, seed)

    game = StableMarriage(suitors, reviewers)
    game.solve()

    game.suitors[0].matching = None
    game.reviewers[0].matching = None

    with pytest.raises(Exception):
        game._check_matching_consistent()


def test_check_stability():
    """Test checker for whether a matching is stable."""

    suitors = [Player("A"), Player("B")]
    reviewers = [Player("X"), Player("Y")]

    (a, b), (x, y) = suitors, reviewers

    a.set_prefs(reviewers)
    b.set_prefs(reviewers[::-1])

    x.set_prefs(suitors)
    y.set_prefs(suitors[::-1])

    game = StableMarriage(suitors, reviewers)

    matching = game.solve()
    assert game.check_stability()

    (a, b), (x, y) = game.suitors, game.reviewers
    matching[a] = y
    matching[b] = x

    assert not game.check_stability()
