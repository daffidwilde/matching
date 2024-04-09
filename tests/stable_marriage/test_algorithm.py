"""Integration tests for the Stable Marriage Problem algorithm."""

import numpy as np
from hypothesis import given

from .strategies import mocked_game, st_ranks


def _assert_matching_is_valid_shape(matching, suitor_ranks, reviewer_ranks):
    """Assert that the matching has the right shape and elements."""

    assert isinstance(matching, dict)

    assert (np.sort(list(matching.keys())) == np.unique(suitor_ranks)).all()
    assert (
        np.sort(list(matching.values())) == np.unique(reviewer_ranks)
    ).all()


@given(st_ranks())
def test_stable_marriage_suitor_optimal(ranks):
    """Test that the SM algorithm is valid and suitor-optimal."""

    suitor_ranks, reviewer_ranks = ranks
    game = mocked_game(*ranks)

    matching = game._stable_marriage()

    _assert_matching_is_valid_shape(matching, suitor_ranks, reviewer_ranks)

    for reviewer, suitor in matching.items():
        suitor_rank = game.suitor_ranks[suitor]
        preferred_reviewers, *_ = np.where(suitor_rank < suitor_rank[reviewer])
        for preferred in preferred_reviewers:
            preferred_rank = game.reviewer_ranks[preferred]
            partner = matching[preferred]
            assert preferred_rank[suitor] > preferred_rank[partner]


@given(st_ranks())
def test_stable_marriage_reviewer_pessimal(ranks):
    """Test that the SM algorithm is valid and reviewer-pessimal."""

    suitor_ranks, reviewer_ranks = ranks
    game = mocked_game(*ranks)

    matching = game._stable_marriage()

    _assert_matching_is_valid_shape(matching, suitor_ranks, reviewer_ranks)

    for reviewer, suitor in matching.items():
        reviewer_rank = game.reviewer_ranks[reviewer]
        lesser_suitors, *_ = np.where(reviewer_rank > reviewer_rank[suitor])

        for lesser in lesser_suitors:
            lesser_rank = game.suitor_ranks[lesser]
            partner = next(
                rev for rev, sui in matching.items() if sui == lesser
            )
            assert lesser_rank[partner] < lesser_rank[reviewer]
