"""Objects used among many tests."""

from unittest import mock

import numpy as np
from hypothesis import strategies as st


def mocked_game(game, *args):
    """Create an instance of a game that mocks its input validator."""

    with mock.patch(
        f"matching.games.{game.__name__}.check_input_validity"
    ) as validator:
        instance = game(*args)

    validator.assert_called_once_with()

    return instance


@st.composite
def st_single_ranks(draw, num_rank: int, len_rank: int):
    """Create a single rank matrix."""

    rank = draw(
        st.lists(
            st.permutations(range(len_rank)),
            min_size=num_rank,
            max_size=num_rank,
        )
    )

    return np.array(rank)
