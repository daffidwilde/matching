""" Hypothesis decorators for SM tests. """

import numpy as np
from hypothesis import given
from hypothesis.strategies import composite, integers, lists, sampled_from

from matching import Player


@composite
def get_player_names(draw, suitor_pool, reviewer_pool):
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


def make_players(player_names, seed):
    """ Given some names, make a valid set each of suitors and reviewers. """

    np.random.seed(seed)
    suitor_names, reviewer_names = player_names
    suitors = [Player(name) for name in suitor_names]
    reviewers = [Player(name) for name in reviewer_names]

    for suitor in suitors:
        suitor.set_prefs(np.random.permutation(reviewers).tolist())
    for reviewer in reviewers:
        reviewer.set_prefs(np.random.permutation(suitors).tolist())

    return suitors, reviewers


def make_prefs(player_names, seed):
    """ Given some names, make a valid set of preferences for each the suitors
    and reviewers. """

    np.random.seed(seed)
    suitor_names, reviewer_names = player_names
    suitor_prefs = {
        name: np.random.permutation(reviewer_names).tolist()
        for name in suitor_names
    }
    reviewer_prefs = {
        name: np.random.permutation(suitor_names).tolist()
        for name in reviewer_names
    }

    return suitor_prefs, reviewer_prefs


STABLE_MARRIAGE = given(
    player_names=get_player_names(
        suitor_pool=["A", "B", "C"], reviewer_pool=["X", "Y", "Z"]
    ),
    seed=integers(min_value=0, max_value=2 ** 32 - 1),
)
