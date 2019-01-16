""" Tests for the BaseSolver class. """

import pytest

from matching import BaseSolver


def test_init():
    """ Test the default parameters makes a valid instance of BaseSolver. """

    match = BaseSolver()

    assert match.suitors is None
    assert match.reviewers is None
    assert match.matching == {}
    assert match.blocking_pairs is None


def test_no_solve():
    """ Verify BaseSolver raises a NotImplementedError when calling the `solve`
    method. """

    with pytest.raises(NotImplementedError):
        match = BaseSolver()
        match.solve()


def test_no_check_stability():
    """ Verify BaseSolver raises a NotImplementedError when calling the
    `check_stability` method. """

    with pytest.raises(NotImplementedError):
        match = BaseSolver()
        match.check_stability()


def test_no_check_validity():
    """ Verify BaseSolver raises a NotImplementError when calling the
    `check_validity` method. """

    with pytest.raises(NotImplementedError):
        match = BaseSolver()
        match.check_validity()


def test_no_update_matching():
    """ Verify BaseSolver raises a NotImplementedError when calling the
    `update_matching` method. """

    with pytest.raises(NotImplementedError):
        match = BaseSolver()
        match.update_matching()
