""" Tests for the BaseGame class. """

import pytest

from matching import BaseGame


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
