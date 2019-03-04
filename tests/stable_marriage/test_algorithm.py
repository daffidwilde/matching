""" Integration tests for the Stable Marriage Problem algorithm. """

from matching.games import stable_marriage

from .params import STABLE_MARRIAGE, make_players


@STABLE_MARRIAGE
def test_suitor_optimal(player_names, seed):
    """ Verify that the suitor-oriented Gale-Shapley algorithm produces a valid,
    suitor-optimal matching for an instance of SM. """

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
    """ Verify that the reviewer-oriented Gale-Shapley algorithm produces a
    valid, reviewer-optimal matching for an instance of SM. """

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
