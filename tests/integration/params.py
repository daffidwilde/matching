""" Useful functions and decorators for the SM tests. """

import numpy as np

from hypothesis import given
from hypothesis.strategies import (
    composite,
    dictionaries,
    integers,
    lists,
    sampled_from,
)


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


GALE_SHAPLEY = given(
    player_names=_get_player_names(
        suitor_pool=["A", "B", "C"], reviewer_pool=["X", "Y", "Z"]
    ),
    seed=integers(min_value=0),
)


HOSPITAL_RESIDENT = given(
    resident_names=lists(
        elements=sampled_from(["A", "B", "C", "D"]),
        min_size=1,
        max_size=4,
        unique=True,
    ),
    hospital_names=lists(
        elements=sampled_from(["X", "Y", "Z"]),
        min_size=1,
        max_size=3,
        unique=True,
    ),
    capacities=dictionaries(
        keys=sampled_from(["X", "Y", "Z"]),
        values=integers(min_value=2),
        min_size=3,
        max_size=3,
    ),
    seed=integers(min_value=0),
)
