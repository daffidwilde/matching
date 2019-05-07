""" Unit tests for the solvers.util functions. """

from hypothesis import given
from hypothesis.strategies import lists, text

from matching import Player
from matching.games.util import delete_pair, match_pair


@given(name=text(), pref_names=lists(text(), min_size=1))
def test_delete_pair(name, pref_names):
    """ Verify that two players can forget each other. """

    others = [Player(other) for other in pref_names]

    for other in others:
        player = Player(name)
        other.set_prefs([player])
        player.set_prefs(others)

        delete_pair(player, other)
        assert player.prefs == [o for o in others if o != other]
        assert other.prefs == []


@given(name=text(), pref_names=lists(text(), min_size=1))
def test_match_pair(name, pref_names):
    """ Verify that two players can be matched to one another. """

    others = [Player(other) for other in pref_names]

    for other in others:
        player = Player(name)
        other.set_prefs([player])
        player.set_prefs(others)

        match_pair(player, other)
        assert player.matching == other
        assert other.matching == player
