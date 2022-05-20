""" Tests for the BasePlayer class. """
from hypothesis import given
from hypothesis.strategies import text

from matching import BasePlayer

from .util import player_others


@given(name=text())
def test_init(name):
    """Make a Player instance and test that their attributes are correct."""

    player = BasePlayer(name)
    assert player.name == name
    assert player.prefs == []
    assert player.matching is None
    assert player._pref_names == []
    assert player._original_prefs is None


@given(name=text())
def test_repr(name):
    """Test that a Player instance is represented by the string version of
    their name."""

    player = BasePlayer(name)
    assert repr(player) == name

    player = BasePlayer(0)
    assert repr(player) == str(0)


@given(name=text())
def test_unmatched_message(name):
    """Test that a Player instance can return a message saying they are
    unmatched. This is could be a lie."""

    player = BasePlayer(name)

    message = player.unmatched_message()
    assert message.startswith(name)
    assert "unmatched" in message


@given(player_others=player_others())
def test_not_in_preferences_message(player_others):
    """Test that a Player instance can return a message saying they are matched
    to another player who does not appear in their preferences. This could be a
    lie."""

    player, others = player_others

    other = others.pop()
    player.set_prefs(others)
    message = player.not_in_preferences_message(other)
    assert message.startswith(player.name)
    assert str(player.prefs) in message
    assert other.name in message


@given(player_others=player_others())
def test_set_prefs(player_others):
    """Test that a Player instance can set its preferences correctly."""

    player, others = player_others

    player.set_prefs(others)
    assert player.prefs == others
    assert player._pref_names == [o.name for o in others]
    assert player._original_prefs == others


@given(player_others=player_others())
def test_keep_original_prefs(player_others):
    """Test that a Player instance keeps a record of their original preference
    list even when their preferences are updated."""

    player, others = player_others

    player.set_prefs(others)
    player.set_prefs([])
    assert player.prefs == []
    assert player._pref_names == []
    assert player._original_prefs == others


@given(player_others=player_others())
def test_forget(player_others):
    """Test that a Player instance can forget another player."""

    player, others = player_others
    player.set_prefs(others)

    for i, other in enumerate(others[:-1]):
        player._forget(other)
        assert player.prefs == others[i + 1 :]

    player._forget(others[-1])
    assert player.prefs == []
    assert player._original_prefs == others


@given(player_others=player_others())
def test_prefers(player_others):
    """Test that a Player instance can compare its preference between two
    players."""

    player, others = player_others

    player.set_prefs(others)
    for i, other in enumerate(others[:-1]):
        assert player.prefers(other, others[i + 1])
