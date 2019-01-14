""" Tests for the Gale-Shapley algorithm. """

import numpy as np

from matching import Player
from matching.algorithms import stable_matching

from .params import STABLE_MATCHING, _make_players


@STABLE_MATCHING
def test_suitor_optimal(player_names, seed):
    """ Verify that the suitor-oriented Gale-Shapley algorithm produces a valid,
    suitor-optimal matching for an instance of SM. """

    suitor_names, reviewer_names = player_names
    suitors, reviewers = _make_players(suitor_names, reviewer_names, seed)
    matching = stable_matching(suitors, reviewers, optimal="suitor")

    assert set(suitors) == set(matching.keys())
    assert set(reviewers) == set(matching.values())

    for suitor, reviewer in matching.items():
        idx = suitor.pref_names.index(reviewer.name)
        preferred = [r for r in reviewers if r.name in suitor.pref_names[:idx]]
        for rev in preferred:
            partner = rev.match
            assert rev.pref_names.index(suitor.name) > rev.pref_names.index(
                partner.name
            )


@STABLE_MATCHING
def test_reviewer_optimal(player_names, seed):
    """ Verify that the reviewer-oriented Gale-Shapley algorithm produces a
    valid, reviewer-optimal matching for an instance of SM. """

    suitor_names, reviewer_names = player_names
    suitors, reviewers = _make_players(suitor_names, reviewer_names, seed)
    matching = stable_matching(suitors, reviewers, optimal="reviewer")

    assert set(suitors) == set(matching.keys())
    assert set(reviewers) == set(matching.values())

    for suitor, reviewer in matching.items():
        idx = reviewer.pref_names.index(suitor.name)
        preferred = [s for s in suitors if s.name in reviewer.pref_names[:idx]]
        for sui in preferred:
            partner = sui.match
            assert sui.pref_names.index(reviewer.name) > sui.pref_names.index(
                partner.name
            )
