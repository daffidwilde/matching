"""Unit tests for the SR solver."""

import warnings

import pytest
from hypothesis import given

from matching import Player, SingleMatching
from matching.exceptions import MatchingError, NoStableMatchingWarning
from matching.games import StableRoommates

from .util import connections, games, players


@given(players=players())
def test_init(players):
    """Test for correct instantiation given a set of players."""

    game = StableRoommates(players)

    for player, game_player in zip(players, game.players):
        assert player.name == game_player.name
        assert player._pref_names == game_player._pref_names

    assert game.matching is None


@given(preferences=connections())
def test_create_from_dictionary(preferences):
    """Test for correct instantiation given a preference dictionary."""

    game = StableRoommates.create_from_dictionary(preferences)

    for player in game.players:
        assert preferences[player.name] == player._pref_names
        assert player.matching is None

    assert game.matching is None


@given(players=players())
def test_check_inputs(players):
    """Test for error if any player has not ranked all other players."""

    players[0].prefs = players[0].prefs[:-1]

    with pytest.raises(Exception):
        StableRoommates(players)


@given(game=games())
def test_solve(game):
    """Test for a reasonable matching when solving."""

    with warnings.catch_warnings(record=True) as w:
        matching = game.solve()

    assert isinstance(matching, SingleMatching)

    players = sorted(game.players, key=lambda p: p.name)
    matching_keys = sorted(matching.keys(), key=lambda k: k.name)

    for game_player, player in zip(matching_keys, players):
        assert game_player.name == player.name
        assert game_player._pref_names == player._pref_names

    for player, match in matching.items():
        if match is None:
            message = w[-1].message
            assert str(player) in str(message)
            assert player.prefs == []
        else:
            assert match in game.players


@given(game=games())
def test_check_validity(game):
    """Test for error if any players are left unmatched."""

    with warnings.catch_warnings(record=True) as w:
        matching = game.solve()

    if None in matching.values():
        message = w[-1].message
        assert isinstance(message, NoStableMatchingWarning)
        with pytest.raises(MatchingError):
            game.check_validity()

    else:
        assert game.check_validity()


def test_stability():
    """Test for recognising a stable matching."""

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
