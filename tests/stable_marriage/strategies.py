"""Composite strategies for SM unit tests."""

from unittest import mock

import numpy as np
from hypothesis import strategies as st
from hypothesis.extra import numpy as st_numpy

from matching.games import StableMarriage


@st.composite
def st_single_ranks(draw, size):
    """Create a single rank matrix."""

    rank = draw(
        st.lists(st.permutations(range(size)), min_size=size, max_size=size)
    )

    return np.array(rank)


@st.composite
def st_ranks(draw, pmin=1, pmax=5):
    """Create a set of rankings for a test."""

    size = draw(st.integers(pmin, pmax))
    suitor_ranks = draw(st_single_ranks(size))
    reviewer_ranks = draw(st_single_ranks(size))

    return suitor_ranks, reviewer_ranks


@st.composite
def st_player_ranks(draw, pmin=1, pmax=5):
    """Create a set of ranks, and choose a player from it."""

    suitor_ranks, reviewer_ranks = draw(st_ranks(pmin, pmax))
    side = draw(st.sampled_from(("suitor", "reviewer")))
    side_ranks = suitor_ranks if side == "suitor" else reviewer_ranks
    player, ranks = draw(st.sampled_from(list(enumerate(side_ranks))))

    return suitor_ranks, reviewer_ranks, player, ranks, side


@st.composite
def st_single_utilities(draw, size):
    """Create a single utility matrix."""

    utility = draw(
        st_numpy.arrays(
            dtype=float,
            elements=st.floats(0, 1, allow_nan=False),
            shape=(size, size),
        )
    )

    return utility


@st.composite
def st_utilities(draw, pmin=1, pmax=5):
    """Create a set of utility matrices."""

    size = draw(st.integers(pmin, pmax))
    suitor_utility = draw(st_single_utilities(size))
    reviewer_utility = draw(st_single_utilities(size))

    return suitor_utility, reviewer_utility


@st.composite
def st_preferences(draw, pmin=1, pmax=5):
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
