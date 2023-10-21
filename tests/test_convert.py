"""Tests for the `matching.convert` module."""

import itertools

import numpy as np
from hypothesis import given, settings
from hypothesis import strategies as st
from hypothesis.extra.numpy import arrays

from matching import convert


@st.composite
def utilities(draw, smin=1, smax=10, unique=True):
    """Create a utility matrix for a test."""

    shape = draw(st.tuples(st.integers(smin, smax), st.integers(smin, smax)))
    utilities = draw(
        arrays(float, shape, elements=st.floats(0, 1), unique=unique)
    )

    return utilities


@st.composite
def preferences(draw, pmin=1, pmax=10):
    """Create a preference dictionary to test."""

    players = draw(
        st.lists(st.integers(), min_size=pmin, max_size=pmax, unique=True)
    )
    others = draw(
        st.lists(st.text(), min_size=pmin, max_size=pmax, unique=True)
    )

    preference = {player: draw(st.permutations(others)) for player in players}

    return preference


@settings(deadline=600)
@given(utilities())
def test_utility_to_rank(utility):
    """Check that a utility matrix can be converted to ranks.

    We choose not to check that the ranking is correct because the
    function is a wrapper for `scipy.stats.rankdata()`.
    """

    rank = convert.utility_to_rank(utility)

    assert isinstance(rank, np.ndarray)
    assert rank.shape == utility.shape
    assert (np.sort(rank) == np.arange(utility.shape[1])).all()


@given(preferences())
def test_preference_to_rank(preference):
    """Check that a preference dictionary can be converted to ranks."""

    others = list(itertools.chain(*preference.values()))
    rank = convert.preference_to_rank(preference, others)

    assert isinstance(rank, np.ndarray)
    assert rank.shape == (
        len(preference.keys()),
        len(list(preference.values())[0]),
    )

    for row, pref in zip(rank, preference.values()):
        assert [others[r] for r in row] == pref
