"""Integration tests for the Stable Marriage Problem algorithm."""

import numpy as np
from hypothesis import given

from .strategies import mocked_game, st_ranks


@given(st_ranks())
def test_stable_marriage(ranks):
    """Test that the SM algorithm is valid and suitor-optimal."""

    suitor_ranks, reviewer_ranks = ranks
    game = mocked_game(*ranks)

    matching = game._stable_marriage()

    assert isinstance(matching, dict)

    assert (np.sort(list(matching.keys())) == np.unique(suitor_ranks)).all()
    assert (
        np.sort(list(matching.values())) == np.unique(reviewer_ranks)
    ).all()

    for reviewer, suitor in matching.items():
        suitor_rank = suitor_ranks[suitor]
        preferred_reviewers, *_ = np.where(suitor_rank < suitor_rank[reviewer])
        for preferred in preferred_reviewers:
            preferred_rank = reviewer_ranks[preferred]
            partner = matching[preferred]
            assert preferred_rank[suitor] > preferred_rank[partner]
