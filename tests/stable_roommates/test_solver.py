""" Unit tests for the SR solver. """

import pytest

from matching import Matching
from matching.games import StableRoommates

from .params import STABLE_ROOMMATES, make_players, make_prefs


@STABLE_ROOMMATES
def test_init(player_names, seed):
    """ Test that the StableRoommates solver takes a set of preformed players
    correctly. """

    players = make_players(player_names, seed)
    game = StableRoommates(players)

    for player, game_player in zip(players, game.players):
        assert player.name == game_player.name
        assert player.pref_names == game_player.pref_names

    assert all([player.matching is None for player in game.players])
    assert game.matching is None


@STABLE_ROOMMATES
def test_create_from_dictionary(player_names, seed):
    """ Test that StableRoommates solver can take a preference dictionary
    correctly. """

    player_prefs = make_prefs(player_names, seed)
    game = StableRoommates.create_from_dictionary(player_prefs)

    for player in game.players:
        assert player_prefs[player.name] == player.pref_names
        assert player.matching is None

    assert game.matching is None


@STABLE_ROOMMATES
def test_check_inputs(player_names, seed):
    """ Test StableRoommates raises a ValueError when a player has not ranked
    all other players. """

    players = make_players(player_names, seed)
    game = StableRoommates(players)

    players[0].prefs = players[0].prefs[:-1]
    with pytest.raises(Exception):
        StableRoommates(players)


@STABLE_ROOMMATES
def test_solve(player_names, seed):
    """ Test that StableRoommates can solve games correctly when passed players.
    """

    players = make_players(player_names, seed)
    game = StableRoommates(players)

    matching = game.solve()
    assert isinstance(matching, Matching)

    players = sorted(players, key=lambda p: p.name)
    matching_keys = sorted(matching.keys(), key=lambda k: k.name)

    for game_player, player in zip(matching_keys, players):
        assert game_player.name == player.name
        assert game_player.pref_names == player.pref_names

    for match in matching.values():
        assert match is None or match in game.players


@STABLE_ROOMMATES
def test_check_validity(player_names, seed):
    """ Test that StableRoommates can raise a ValueError if any players are left
    unmatched. """

    players = make_players(player_names, seed)
    game = StableRoommates(players)

    matching = game.solve()
    if None in matching.values():
        with pytest.raises(Exception):
            game.check_validity()

    else:
        assert game.check_validity()


def test_stability():
    """ Test that StableRoommates can recognise whether a matching is stable.
    """

    from matching import Player

    players = [Player("A"), Player("B"), Player("C"), Player("D")]
    a, b, c, d = players

    a.set_prefs([b, c, d])
    b.set_prefs([c, d, a])
    c.set_prefs([d, b, a])
    d.set_prefs([a, b, c])

    game = StableRoommates(players)

    matching = game.solve()
    assert game.check_stability()

    a, b, c, d = game.players

    matching[a] = c
    matching[b] = d
    matching[c] = a
    matching[d] = b

    assert not game.check_stability()

    matching[a] = None
    matching[c] = None
    assert not game.check_stability()
