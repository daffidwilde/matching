""" Tests for the Game class. """

import pytest

from matching import Game


def test_init():
    """ Test the default parameters makes a valid instance of Game. """

    match = Game()

    assert match.matching is None
    assert match.blocking_pairs is None


def test_no_solve():
    """ Verify Game raises a NotImplementedError when calling the `solve`
    method. """

    with pytest.raises(NotImplementedError):
        match = Game()
        match.solve()


def test_no_check_stability():
    """ Verify Game raises a NotImplementedError when calling the
    `check_stability` method. """

    with pytest.raises(NotImplementedError):
        match = Game()
        match.check_stability()


def test_no_check_validity():
    """ Verify Game raises a NotImplementError when calling the
    `check_validity` method. """

    with pytest.raises(NotImplementedError):
        match = Game()
        match.check_validity()
