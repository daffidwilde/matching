""" Useful functions and decorators for the SM tests. """

import numpy as np

from hypothesis import given
from hypothesis.strategies import composite, integers, sampled_from, sets

from matching import Player


def make_players(suitor_names, reviewer_names):
    """ Given some names, make a valid set each of suitors and reviewers. """

    suitors, reviewers = (
        [
            Player(name, np.random.permutation([o for o in others]).tolist())
            for name in names
        ]
        for names, others in [
            (suitor_names, reviewer_names),
            (reviewer_names, suitor_names),
        ]
    )

    return suitors, reviewers


@composite
def get_player_names(draw, suitor_pool, reviewer_pool):
    """ A custom strategy for drawing lists of suitor and reviewer names of
    equal size from their respective pools. """

    suitor_names = draw(
        sets(sampled_from(suitor_pool), min_size=1, max_size=len(suitor_pool))
    )

    reviewer_names = draw(
        sets(
            sampled_from(reviewer_pool),
            min_size=len(suitor_names),
            max_size=len(suitor_names),
        )
    )

    return suitor_names, reviewer_names


GALE_SHAPLEY = given(
    player_names=get_player_names(
        suitor_pool=["A", "B", "C"], reviewer_pool=["X", "Y", "Z"]
    ),
    seed=integers(min_value=0),
)
