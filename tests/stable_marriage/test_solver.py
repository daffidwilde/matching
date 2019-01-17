""" Unit tests for the SM solvers. """

import pytest

from matching import StableMarriage, Matching

from .params import STABLE_MARRIAGE, _make_players


@STABLE_MARRIAGE
def test_init(player_names, seed):
    """ Test that the StableMarriage solver takes parameters correctly. """

    suitor_names, reviewer_names = player_names
    suitors, reviewers = _make_players(suitor_names, reviewer_names, seed)
    match = StableMarriage(suitors, reviewers)

    assert match.suitors == suitors
    assert match.reviewers == reviewers
    assert all(
        [player.matching is None for player in match.suitors + match.reviewers]
    )
    assert match.matching == {}


@STABLE_MARRIAGE
def test_inputs_num_players(player_names, seed):
    """ Test StableMarriage raises a ValueError when a different number of
    suitors and reviewers are passed. """

    suitor_names, reviewer_names = player_names
    suitors, reviewers = _make_players(suitor_names, reviewer_names, seed)

    suitors = suitors[:-1]

    with pytest.raises(ValueError):
        StableMarriage(suitors, reviewers)


@STABLE_MARRIAGE
def test_inputs_player_ranks(player_names, seed):
    """ Test StableMarriage raises a ValueError when a player has not ranked all
    members of the opposing party. """

    suitor_names, reviewer_names = player_names
    suitors, reviewers = _make_players(suitor_names, reviewer_names, seed)

    suitors[0].pref_names = suitors[0].pref_names[:-1]

    with pytest.raises(ValueError):
        StableMarriage(suitors, reviewers)


@STABLE_MARRIAGE
def test_solve(player_names, seed):
    """ Test that StableMarriage can solve games correctly. """

    suitor_names, reviewer_names = player_names
    suitors, reviewers = _make_players(suitor_names, reviewer_names, seed)
    match = StableMarriage(suitors, reviewers)

    for optimal in ["suitor", "reviewer"]:
        matching = match.solve(optimal)
        assert isinstance(matching, Matching)
        assert set(matching.keys()) == set(suitors)
        assert set(matching.values()) == set(reviewers)


@STABLE_MARRIAGE
def test_check_validity(player_names, seed):
    """ Test that StableMarriage finds no errors when the game is solved. """

    suitor_names, reviewer_names = player_names
    suitors, reviewers = _make_players(suitor_names, reviewer_names, seed)
    match = StableMarriage(suitors, reviewers)

    match.solve()
    assert not match.check_validity()


@STABLE_MARRIAGE
def test_validity_all_matched_game(player_names, seed):
    """ Test that StableMarriage recognises a valid matching requires all
    players to be matched as players and as part of the game. """

    suitor_names, reviewer_names = player_names
    suitors, reviewers = _make_players(suitor_names, reviewer_names, seed)
    match = StableMarriage(suitors, reviewers)

    matching = match.solve()
    matching[match.suitors[0]].matching = None

    with pytest.raises(Exception):
        match.check_validity()


@STABLE_MARRIAGE
def test_validity_consistent(player_names, seed):
    """ Test that StableMarriage recognises a valid matching requires there to
    be consistency between the game's matching and its players'. """

    suitor_names, reviewer_names = player_names
    suitors, reviewers = _make_players(suitor_names, reviewer_names, seed)
    match = StableMarriage(suitors, reviewers)

    matching = match.solve()
    matching[match.suitors[0]].matching = matching[match.suitors[-1]]
    list(matching.keys())[0].matching = list(matching.values())[-1]

    with pytest.raises(Exception):
        match.check_validity()


def test_check_stability():
    """ Test that StableMarriage can recognise whether a matching is stable. """

    from matching import Player

    suitors = [Player("A", [1, 2]), Player("B", [2, 1])]
    reviewers = [Player(1, ["A", "B"]), Player(2, ["B", "A"])]
    match = StableMarriage(suitors, reviewers)

    matching = match.solve()
    assert match.check_stability()

    (P_A, P_B), (P_1, P_2) = match.suitors, match.reviewers
    matching[P_A] = P_2
    matching[P_B] = P_1

    assert not match.check_stability()
