"""Unit tests for StableMarriage class."""

from unittest import mock

import numpy as np
from hypothesis import given
from hypothesis import strategies as st
from hypothesis.extra import numpy as st_numpy

from matching.games import StableMarriage


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
def st_utilities(draw, pmin=1, pmax=10):
    """Create a set of utility matrices."""

    size = draw(st.integers(pmin, pmax))
    suitor_utility = draw(st_single_utilities(size))
    reviewer_utility = draw(st_single_utilities(size))

    return suitor_utility, reviewer_utility


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


@given(st_utilities())
def test_from_utilities(utilities):
    """Test the utility matrix builder."""

    suitor_utility, reviewer_utility = utilities

    with mock.patch(
        "matching.games.StableMarriage.check_input_validity"
    ) as validator, mock.patch("matching.convert.utility_to_rank") as ranker:
        effects = (suitor_utility.argsort(), reviewer_utility.argsort())
        ranker.side_effect = list(effects)
        game = StableMarriage.from_utilities(suitor_utility, reviewer_utility)

    assert isinstance(game, StableMarriage)
    assert (game.suitor_ranks == effects[0]).all()
    assert (game.reviewer_ranks == effects[1]).all()

    assert game.num_suitors == len(suitor_utility)
    assert game.num_reviewers == len(reviewer_utility)
    assert game.matching is None

    assert ranker.call_count == 2
    for call, utility in zip(ranker.call_args_list, utilities):
        arg, *_ = call.args
        assert np.array_equal(arg, utility)

    validator.assert_called_once_with()


@given(st_preferences())
def test_from_preferences(preferences):
    """Test the preference list builder."""

    suitor_prefs, reviewer_prefs = preferences

    with mock.patch(
        "matching.games.StableMarriage.check_input_validity"
    ) as validator, mock.patch(
        "matching.convert.preference_to_rank"
    ) as ranker:
        effects = (
            np.array(list(suitor_prefs.values())),
            np.array(list(reviewer_prefs.values())),
        )
        ranker.side_effect = list(effects)
        game = StableMarriage.from_preferences(suitor_prefs, reviewer_prefs)

    assert isinstance(game, StableMarriage)
    assert (game.suitor_ranks == effects[0]).all()
    assert (game.reviewer_ranks == effects[1]).all()

    assert game.num_suitors == len(suitor_prefs)
    assert game.num_reviewers == len(reviewer_prefs)
    assert game.matching is None

    assert ranker.call_count == 2
    for call, preference, others in zip(
        ranker.call_args_list,
        preferences,
        (reviewer_prefs.keys(), suitor_prefs.keys()),
    ):
        assert call.args == (preference, tuple(others))

    validator.assert_called_once_with()
