""" Tests for the SM solvers. """

from matching import StableMarriage

from tests.stable_marriage.params import STABLE_MARRIAGE, _make_players

@STABLE_MARRIAGE
def test_init(player_names, seed):
    """ Test that an instance of the GaleShapley solver can be created. """

    suitor_names, reviewer_names = player_names
    suitors, reviewers = _make_players(suitor_names, reviewer_names, seed)
    match = StableMarriage(suitors, reviewers)

    assert match.suitors == suitors
    assert match.reviewers == reviewers
    assert all(
        [player.match is None for player in match.suitors + match.reviewers]
    )
    assert match.matching is None
