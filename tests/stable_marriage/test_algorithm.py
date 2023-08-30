"""Integration tests for the Stable Marriage Problem algorithm."""

from matching.algorithms import stable_marriage

from .util import STABLE_MARRIAGE, make_players


@STABLE_MARRIAGE
def test_suitor_optimal(player_names, seed):
    """Test that the suitor-optimal algorithm is suitor-optimal."""

    suitors, reviewers = make_players(player_names, seed)
    matching = stable_marriage(suitors, reviewers, optimal="suitor")

    assert set(suitors) == set(matching.keys())
    assert set(reviewers) == set(matching.values())

    for suitor, reviewer in matching.items():
        idx = suitor.prefs.index(reviewer)
        preferred = suitor.prefs[:idx]
        for rev in preferred:
            partner = rev.matching
            assert rev.prefs.index(suitor) > rev.prefs.index(partner)


@STABLE_MARRIAGE
def test_reviewer_optimal(player_names, seed):
    """Test that the reviewer-optimal algorithm is reviewer-optimal."""

    suitors, reviewers = make_players(player_names, seed)
    matching = stable_marriage(suitors, reviewers, optimal="reviewer")

    assert set(suitors) == set(matching.keys())
    assert set(reviewers) == set(matching.values())

    for suitor, reviewer in matching.items():
        idx = reviewer.prefs.index(suitor)
        preferred = reviewer.prefs[:idx]
        for suit in preferred:
            partner = suit.matching
            assert suit.prefs.index(reviewer) > suit.prefs.index(partner)
