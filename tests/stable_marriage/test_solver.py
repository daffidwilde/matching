""" Unit tests for the SM solver. """

import pytest

from matching import Matching
from matching.games import StableMarriage

from .params import STABLE_MARRIAGE, make_players, make_prefs


@STABLE_MARRIAGE
def test_init_players(player_names, seed):
    """ Test that the StableMarriage solver takes two sets of preformed players
    correctly. """

    suitors, reviewers = make_players(player_names, seed)
    game = StableMarriage(suitors, reviewers)

    assert game.suitors == suitors
    assert game.reviewers == reviewers
    assert all(
        [player.matching is None for player in game.suitors + game.reviewers]
    )
    assert game.matching is None


@STABLE_MARRIAGE
def test_init_preferences(player_names, seed):
    """ Test that the StableMarriage solver can take two preference dictionaries
    correctly. """

    suitor_prefs, reviewer_prefs = make_prefs(player_names, seed)
    game = StableMarriage(
        suitor_prefs=suitor_prefs, reviewer_prefs=reviewer_prefs
    )

    for suitor in game.suitors:
        pref_names = [reviewer.name for reviewer in suitor.prefs]
        assert suitor_prefs[suitor.name] == pref_names
        assert suitor.matching is None

    for reviewer in game.reviewers:
        pref_names = [suitor.name for suitor in reviewer.prefs]
        assert reviewer_prefs[reviewer.name] == pref_names
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
def test_solve_players(player_names, seed):
    """ Test that StableMarriage can solve games correctly when passed players.
    """

    for optimal in ["suitor", "reviewer"]:
        suitors, reviewers = make_players(player_names, seed)
        game = StableMarriage(suitors, reviewers)

        matching = game.solve(optimal)
        assert isinstance(matching, Matching)
        assert set(matching.keys()) == set(suitors)
        assert set(matching.values()) == set(reviewers)


@STABLE_MARRIAGE
def test_solve_preferences(player_names, seed):
    """ Test that StableMarriage can solve games correctly when passed
    preferences. """

    for optimal in ["suitor", "reviewer"]:
        suitor_prefs, reviewer_prefs = make_prefs(player_names, seed)
        game = StableMarriage(
            suitor_prefs=suitor_prefs, reviewer_prefs=reviewer_prefs
        )

        matching = game.solve(optimal)
        assert isinstance(matching, Matching)
        assert set(matching.keys()) == set(game.suitors)
        assert set(matching.values()) == set(game.reviewers)


@STABLE_MARRIAGE
def test_check_validity(player_names, seed):
    """ Test that StableMarriage finds no errors when the game is solved. """

    suitors, reviewers = make_players(player_names, seed)
    game = StableMarriage(suitors, reviewers)

    game.solve()
    assert game.check_validity()


@STABLE_MARRIAGE
def test_all_gameed(player_names, seed):
    """ Test that StableMarriage recognises a valid matching requires all
    players to be gameed as players and as part of the game. """

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
    reviewers = [Player(1), Player(2)]

    suitors[0].set_prefs(reviewers)
    suitors[1].set_prefs(reviewers[::-1])

    reviewers[0].set_prefs(suitors)
    reviewers[1].set_prefs(suitors[::-1])

    game = StableMarriage(suitors, reviewers)

    matching = game.solve()
    assert game.check_stability()

    (s_a, s_b), (r_1, r_2) = game.suitors, game.reviewers
    matching[s_a] = r_2
    matching[s_b] = r_1

    assert not game.check_stability()
