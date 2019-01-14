""" Tests for the Matcher class. """

import pytest

from matching import Matcher


def test_init():
    """ Test the default parameters makes a valid instance of a Matcher. """

    match = Matcher()

    assert match.suitors is None
    assert match.reviewers is None
    assert match.matching is None
    assert match.blocking_pairs is None


def test_no_solve():
    """ Verify Matcher raises a NotImplementedError when attempting to call
    the `solve` method. """

    with pytest.raises(NotImplementedError):
        match = Matcher()
        match.solve()


def test_no_check_stability():
    """ Verify Matcher raises a NotImplementedError when attempting to call
    the `check_stability` method. """

    with pytest.raises(NotImplementedError):
        match = Matcher()
        match.check_stability()
