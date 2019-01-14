""" Tests for the SM solvers. """

from matching import SMMatcher

from tests.stable_matching.params import STABLE_MATCHING, _make_players

@STABLE_MATCHING
def test_init(player_names, seed):
    """ Test that an instance of the GaleShapley solver can be created. """

    suitor_names, reviewer_names = player_names
    suitors, reviewers = _make_players(suitor_names, reviewer_names, seed)
    match = SMMatcher(suitors, reviewers)

    assert match.suitors == suitors
    assert match.reviewers == reviewers
    assert all(
        [player.match is None for player in match.suitors + match.reviewers]
    )
    assert match.matching is None
