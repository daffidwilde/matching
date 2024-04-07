"""Unit tests for StableMarriage class."""

from unittest import mock

import numpy as np
from hypothesis import given
from hypothesis import strategies as st

from matching.games import StableMarriage


@st.composite
def st_single_ranks(draw, size):
    """Create a single rank matrix."""

    rank = draw(
        st.lists(st.permutations(range(size)), min_size=size, max_size=size)
    )

    return np.array(rank)


@st.composite
def st_ranks(draw, pmin=1, pmax=10):
    """Create a set of rankings for a test."""

    size = draw(st.integers(pmin, pmax))
    suitor_ranks = draw(st_single_ranks(size))
    reviewer_ranks = draw(st_single_ranks(size))

    return suitor_ranks, reviewer_ranks


@st.composite
def st_preferences(draw, pmin=1, pmax=10):
    """Create a set of preferences for a test."""

    size = draw(st.integers(pmin, pmax))
    suitors, reviewers = (
        draw(st.lists(elements, min_size=size, max_size=size, unique=True))
        for elements in (st.integers(), st.text())
    )

    suitor_prefs = {s: draw(st.permutations(reviewers)) for s in suitors}
    reviewer_prefs = {r: draw(st.permutations(suitors)) for r in reviewers}

    return suitor_prefs, reviewer_prefs


def mocked_game(suitor_ranks, reviewer_ranks):
    """Create an instance of SM that mocks the input validator."""

    with mock.patch(
        "matching.games.StableMarriage.check_input_validity"
    ) as validator:
        game = StableMarriage(suitor_ranks, reviewer_ranks)

    validator.assert_called_once_with()

    return game


@given(st_ranks())
def test_init(ranks):
    """Test for correct instantiation given some rankings."""

    suitor_ranks, reviewer_ranks = ranks
    game = mocked_game(suitor_ranks, reviewer_ranks)

    assert (game.suitor_ranks == suitor_ranks).all()
    assert (game.reviewer_ranks == reviewer_ranks).all()

    assert game.num_suitors == len(suitor_ranks)
    assert game.num_reviewers == len(reviewer_ranks)
    assert game.matching is None
