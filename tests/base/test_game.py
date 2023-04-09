"""Tests for the BaseGame class."""

import pytest
from hypothesis import given
from hypothesis.strategies import booleans

from matching import BaseGame, Player
from matching.exceptions import (
    PlayerExcludedWarning,
    PreferencesChangedWarning,
)

from .util import player_others


class DummyGame(BaseGame):
    """A blank game class for use in tests."""

    def solve(self):
        """Placeholder solver method."""

    def check_stability(self):
        """Placeholder stability-checker method."""

    def check_validity(self):
        """Placeholder validity-checker method."""


@given(clean=booleans())
def test_init(clean):
    """Make an instance and test it has the correct attributes."""

    game = DummyGame(clean)

    assert isinstance(game, BaseGame)
    assert game.matching is None
    assert game.blocking_pairs is None
    assert game.clean is clean


@given(player_others=player_others())
def test_remove_player(player_others):
    """Test that a player can be removed from a game and its players."""

    player, others = player_others

    player.set_prefs(others)
    for other in others:
        other.set_prefs([player])

    game = DummyGame()
    game.players = [player]
    game.others = others

    game._remove_player(player, "players", "others")

    assert player not in game.players
    assert all(player not in other.prefs for other in game.others)


@given(player_others=player_others(), clean=booleans())
def test_check_inputs_player_prefs_unique(player_others, clean):
    """Test that players have unique preferences."""

    player, others = player_others

    player.set_prefs(others + others[:1])

    game = DummyGame(clean)
    game.players = [player]

    with pytest.warns(PreferencesChangedWarning) as record:
        game._check_inputs_player_prefs_unique("players")

    assert len(record) == 1

    message = str(record[0].message)

    assert message.startswith(player.name)
    assert others[0].name in message

    if clean:
        assert player._pref_names == [o.name for o in others]


@given(player_others=player_others(), clean=booleans())
def test_check_inputs_player_prefs_all_in_party(player_others, clean):
    """Test that players' preferences are subsets of the other party."""

    player, others = player_others

    outsider = Player("foo")
    player.set_prefs([outsider])

    game = DummyGame(clean)
    game.players = [player]
    game.others = others

    with pytest.warns(PreferencesChangedWarning) as record:
        game._check_inputs_player_prefs_all_in_party("players", "others")

    assert len(record) == 1

    message = str(record[0].message)

    assert message.startswith(player.name)
    assert "non-other" in message
    assert outsider.name in message

    if clean:
        assert outsider not in player.prefs


@given(player_others=player_others(), clean=booleans())
def test_check_inputs_player_prefs_nonempty(player_others, clean):
    """Test that players have got nonempty preference lists."""

    player, others = player_others

    player.set_prefs(others)
    other = others[0]

    game = DummyGame(clean)
    game.players = [player]
    game.others = [other]

    with pytest.warns(PlayerExcludedWarning) as record:
        game._check_inputs_player_prefs_nonempty("others", "players")

    assert len(record) == 1

    message = str(record[0].message)

    assert message.startswith(other.name)

    if clean:
        assert other not in game.others
        assert player.prefs == others[1:]
