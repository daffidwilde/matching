""" Tests for the BaseGame class. """
import warnings

import pytest
from hypothesis import given
from hypothesis.strategies import booleans, lists, text

from matching import BaseGame, Player
from matching.exceptions import PreferencesChangedWarning


class DummyGame(BaseGame):
    def solve(self):
        raise NotImplementedError()

    def check_stability(self):
        raise NotImplementedError()

    def check_validity(self):
        raise NotImplementedError()


def test_init():
    """ Test the default parameters makes a valid instance of BaseGame. """

    match = DummyGame()

    assert isinstance(match, BaseGame)
    assert match.matching is None
    assert match.blocking_pairs is None


@given(
    name=text(),
    other_names=lists(text(), min_size=1, unique=True),
    clean=booleans(),
)
def test_check_inputs_player_prefs_unique(name, other_names, clean):
    """ Test that a game can verify its players have unique preferences. """

    player = Player(name)
    others = [Player(other) for other in other_names]
    player.set_prefs(others + others[:1])

    game = DummyGame(clean)
    game.players = [player]

    with warnings.catch_warnings(record=True) as w:
        game._check_inputs_player_prefs_unique("players")

        message = w[-1].message
        assert isinstance(message, PreferencesChangedWarning)
        assert str(message).startswith(name)
        assert others[0].name in str(message)
        if clean:
            assert player.pref_names == other_names


def test_no_solve():
    """ Verify BaseGame raises a NotImplementedError when calling the `solve`
    method. """

    with pytest.raises(NotImplementedError):
        match = DummyGame()
        match.solve()


def test_no_check_stability():
    """ Verify BaseGame raises a NotImplementedError when calling the
    `check_stability` method. """

    with pytest.raises(NotImplementedError):
        match = DummyGame()
        match.check_stability()


def test_no_check_validity():
    """ Verify BaseGame raises a NotImplementError when calling the
    `check_validity` method. """

    with pytest.raises(NotImplementedError):
        match = DummyGame()
        match.check_validity()
