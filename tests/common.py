"""Objects used among many tests."""

from unittest import mock

import numpy as np
from hypothesis import strategies as st
from hypothesis.extra import numpy as st_numpy


def mocked_game(game, *args):
    """Create an instance of a game that mocks its input validator."""
    with mock.patch(f"matching.games.{game.__name__}.check_input_validity") as validator:
        instance = game(*args)

    validator.assert_called_once_with()

    return instance


@st.composite
def st_single_ranks(draw, nrows: int, ncols: int | None = None):
    """Create a single rank matrix."""
    if ncols is None:
        ncols = nrows

    rank = draw(
        st.lists(
            st.permutations(range(ncols)),
            min_size=nrows,
            max_size=nrows,
        )
    )

    return np.array(rank)


@st.composite
def st_single_utilities(draw, nrows: int, ncols: int | None = None):
    """Create a single utility matrix."""
    if ncols is None:
        ncols = nrows

    utility = draw(
        st_numpy.arrays(
            dtype=float,
            elements=st.floats(0, 1, allow_nan=False),
            shape=(nrows, ncols),
        )
    )

    return utility


@st.composite
def st_sizes(draw, nmin=1, nmax=5):
    """Create a size for a side in a game."""
    return draw(st.integers(nmin, nmax))
