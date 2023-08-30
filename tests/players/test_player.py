"""Tests for the Player class."""

from hypothesis import given
from hypothesis.strategies import lists, text

from matching import Player


@given(name=text(), pref_names=lists(text(), min_size=1))
def test_get_favourite(name, pref_names):
    """Test for findings a player's favourite player."""

    player = Player(name)
    others = [Player(other) for other in pref_names]

    player.set_prefs(others)
    favourite = others[0]
    assert player.get_favourite() == favourite


@given(name=text(), pref_names=lists(text(), min_size=1))
def test_match(name, pref_names):
    """Test that a player can match to another player correctly."""

    player = Player(name)
    other = Player(pref_names[0])

    player._match(other)
    assert player.matching == other


@given(name=text(), pref_names=lists(text(), min_size=1))
def test_unmatch(name, pref_names):
    """Test that a player can unmatch from another player correctly."""

    player = Player(name)
    other = Player(pref_names[0])

    player.matching = other
    player._unmatch()
    assert player.matching is None


@given(name=text(), pref_names=lists(text(), min_size=1))
def test_get_successors(name, pref_names):
    """Test that a player can get its successors."""

    player = Player(name)
    others = [Player(other) for other in pref_names]

    player.set_prefs(others)
    player.matching = others[0]
    if len(player._original_prefs) > 1:
        successors = others[1:]
        assert player.get_successors() == successors
    else:
        assert player.get_successors() == []


@given(name=text(), pref_names=lists(text(), min_size=1, unique=True))
def test_check_if_match_unacceptable(name, pref_names):
    """Test that the acceptability of a match is caught correctly."""

    player = Player(name)
    others = [Player(other) for other in pref_names]

    message = player.unmatched_message()
    assert player.check_if_match_is_unacceptable() == message

    player.set_prefs(others[:-1])
    player._match(others[-1])
    message = player.not_in_preferences_message(others[-1])
    assert player.check_if_match_is_unacceptable() == message

    player.set_prefs(others)
    assert player.check_if_match_is_unacceptable() is None
