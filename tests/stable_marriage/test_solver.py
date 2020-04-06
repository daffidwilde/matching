""" Unit tests for the SM solver. """

import pytest

from matching import Matching
from matching.games import StableMarriage

from .params import STABLE_MARRIAGE, make_players, make_prefs


@STABLE_MARRIAGE
def test_init(player_names, seed):
    """ Test that the StableMarriage solver takes two sets of preformed players
    correctly. """

    suitors, reviewers = make_players(player_names, seed)
    game = StableMarriage(suitors, reviewers)

    for player, game_player in zip(
        suitors + reviewers, game.suitors + game.reviewers
    ):
        assert player.name == game_player.name
        assert player.pref_names == game_player.pref_names

    assert all(
        [player.matching is None for player in game.suitors + game.reviewers]
    )
    assert game.matching is None


@STABLE_MARRIAGE
def test_create_from_dictionaries(player_names, seed):
    """ Test that the StableMarriage solver can take two preference dictionaries
    correctly. """

    suitor_prefs, reviewer_prefs = make_prefs(player_names, seed)
    game = StableMarriage.create_from_dictionaries(suitor_prefs, reviewer_prefs)

    for suitor in game.suitors:
        assert suitor_prefs[suitor.name] == suitor.pref_names
        assert suitor.matching is None

    for reviewer in game.reviewers:
        assert reviewer_prefs[reviewer.name] == reviewer.pref_names
        assert reviewer.matching is None

    assert game.matching is None


@STABLE_MARRIAGE
def test_inputs_num_players(player_names, seed):
    """ Test StableMarriage raises a ValueError when a different number of
    suitors and reviewers are passed. """

    suitors, reviewers = make_players(player_names, seed)
    game = StableMarriage(suitors, reviewers)

    assert game._check_num_players()

    suitors = suitors[:-1]

    with pytest.raises(ValueError):
        StableMarriage(suitors, reviewers)


@STABLE_MARRIAGE
def test_inputs_player_ranks(player_names, seed):
    """ Test StableMarriage raises a ValueError when a player has not ranked all
    members of the opposing party. """

    suitors, reviewers = make_players(player_names, seed)
    game = StableMarriage(suitors, reviewers)

    for player in game.suitors + game.reviewers:
        assert game._check_player_ranks(player)

    suitors[0].prefs = suitors[0].prefs[:-1]

    with pytest.raises(ValueError):
        StableMarriage(suitors, reviewers)


@STABLE_MARRIAGE
def test_solve(player_names, seed):
    """ Test that StableMarriage can solve games correctly when passed players.
    """

    for optimal in ["suitor", "reviewer"]:
        suitors, reviewers = make_players(player_names, seed)
        game = StableMarriage(suitors, reviewers)

        matching = game.solve(optimal)
        assert isinstance(matching, Matching)

        suitors = sorted(suitors, key=lambda s: s.name)
        reviewers = sorted(reviewers, key=lambda r: r.name)

        matching_keys = sorted(matching.keys(), key=lambda k: k.name)
        matching_values = sorted(matching.values(), key=lambda v: v.name)

        for game_suitor, suitor in zip(matching_keys, suitors):
            assert game_suitor.name == suitor.name
            assert game_suitor.pref_names == suitor.pref_names

        for game_reviewer, reviewer in zip(matching_values, reviewers):
            assert game_reviewer.name == reviewer.name
            assert game_reviewer.pref_names == reviewer.pref_names


@STABLE_MARRIAGE
def test_check_validity(player_names, seed):
    """ Test that StableMarriage finds no errors when the game is solved. """

    suitors, reviewers = make_players(player_names, seed)
    game = StableMarriage(suitors, reviewers)

    game.solve()
    assert game.check_validity()


@STABLE_MARRIAGE
def test_all_matched(player_names, seed):
    """ Test that StableMarriage recognises a valid matching requires all
    players to be matched as players and as part of the game. """

    suitors, reviewers = make_players(player_names, seed)
    game = StableMarriage(suitors, reviewers)

    matching = game.solve()
    matching[game.suitors[0]].matching = None
    game.matching[game.suitors[0]] = None

    with pytest.raises(Exception):
        game._check_all_matched()


@STABLE_MARRIAGE
def test_matching_consistent(player_names, seed):
    """ Test that StableMarriage recognises a valid matching requires there to
    be consistency between the game's matching and its players'. """

    suitors, reviewers = make_players(player_names, seed)

    game = StableMarriage(suitors, reviewers)
    game.solve()

    game.suitors[0].matching = None
    game.reviewers[0].matching = None

    with pytest.raises(Exception):
        game._check_matching_consistent()


def test_check_stability():
    """ Test that StableMarriage can recognise whether a matching is stable. """

    from matching import Player

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
