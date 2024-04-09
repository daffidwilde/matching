"""A collection of example tests for SM."""

import numpy as np
import pytest

from matching.games import StableMarriage


def test_pride_and_prejudice():
    """Test the example from Jane Austen's Pride and Prejudice.

    This example appears in the SM Discussion documentation.
    """

    suitor_preferences = {
        "B": ("J", "E", "L", "C"),
        "C": ("J", "E", "L", "C"),
        "D": ("E", "J", "C", "L"),
        "W": ("L", "J", "E", "C"),
    }
    reviewer_preferences = {
        "C": ("B", "D", "C", "W"),
        "E": ("W", "D", "B", "C"),
        "J": ("B", "W", "D", "C"),
        "L": ("B", "W", "D", "C"),
    }

    game = StableMarriage.from_preferences(
        suitor_preferences, reviewer_preferences
    )
    matching = game.solve()

    assert dict(matching) == {2: 0, 0: 1, 1: 2, 3: 3}


def test_readme_example():
    """Verify the example used in the README."""

    suitor_preferences = {
        "A": ["D", "E", "F"],
        "B": ["D", "F", "E"],
        "C": ["F", "D", "E"],
    }
    reviewer_preferences = {
        "D": ["B", "C", "A"],
        "E": ["A", "C", "B"],
        "F": ["C", "B", "A"],
    }

    game = StableMarriage.from_preferences(
        suitor_preferences, reviewer_preferences
    )
    matching = game.solve()

    assert dict(matching) == {1: 0, 0: 1, 2: 2}


def test_matchingr_example():
    """Test the example from the MatchingR vignette."""

    uM = np.array([[1.0, 0.5, 0.0], [0.5, 0.0, 0.5]])
    uW = np.array([[0.0, 1.0], [0.5, 0.0], [1.0, 0.5]])

    with pytest.warns(UserWarning, match="do not match"):
        game = StableMarriage.from_utilities(uM, uW)

    matching = game.solve()

    assert dict(matching) == {0: 1, 1: 0}
