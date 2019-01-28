""" Hypothesis decorators for SM tests. """

import numpy as np

from hypothesis import given
from hypothesis.strategies import composite, integers, lists, sampled_from

from matching import Player


@composite
def _get_player_names(draw, suitor_pool, reviewer_pool):
    """ A custom strategy for drawing lists of suitor and reviewer names of
    equal size from their respective pools. """

    suitor_names = draw(
        lists(
            sampled_from(suitor_pool),
            min_size=1,
            max_size=len(suitor_pool),
            unique=True,
        )
    )

    reviewer_names = draw(
        lists(
            sampled_from(reviewer_pool),
            min_size=len(suitor_names),
            max_size=len(suitor_names),
            unique=True,
        )
    )

    return suitor_names, reviewer_names


def _make_players(suitor_names, reviewer_names, seed):
    """ Given some names, make a valid set each of suitors and reviewers. """

    np.random.seed(seed)
    suitors, reviewers = (
        [Player(name, np.random.permutation(others).tolist()) for name in names]
        for names, others in [
            (suitor_names, reviewer_names),
            (reviewer_names, suitor_names),
        ]
    )

    return suitors, reviewers


STABLE_MARRIAGE = given(
    player_names=_get_player_names(
        suitor_pool=["A", "B", "C"], reviewer_pool=["X", "Y", "Z"]
    ),
    seed=integers(min_value=0, max_value=2 ** 32 - 1),
)
