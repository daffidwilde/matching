""" Unit tests for the solvers.util functions. """

from matching import Player
from matching.solvers.util import delete_pair, match_pair, unmatch_pair

from .params import PLAYER


@PLAYER
def test_delete_pair(name, pref_names, capacity):
    """ Verify that two players can forget each other. """

    others = [Player(other, [name]) for other in pref_names]

    for other in others:
        player = Player(name, pref_names, capacity)
        delete_pair(player, other)

        assert set(player.pref_names) == set(pref_names) - set([other.name])
        assert other.pref_names == []


@PLAYER
def test_match_pair(name, pref_names, capacity):
    """ Verify that two players can be matched to one another. """

    others = [Player(other, [name]) for other in pref_names]

    for other in others:
        player = Player(name, pref_names, capacity)
        match_pair(player, other)

        assert (
            player.matching == other
            if capacity == 1
            else player.matching == [other]
        )
        assert other.matching == player


@PLAYER
def test_unmatch_pair(name, pref_names, capacity):
    """ Verify that two players can be unmatched from one another. """

    others = [Player(other, [name]) for other in pref_names]

    for other in others:
        player = Player(name, pref_names, capacity)

        player.matching = other if capacity == 1 else [other]
        other.matching = player
        unmatch_pair(player, other)

        assert (
            player.matching is None if capacity == 1 else player.matching == []
        )
        assert other.matching is None

        player.matching = other if capacity == 1 else [other]
        other.matching = [player]
        unmatch_pair(player, other)

        assert (
            player.matching is None if capacity == 1 else player.matching == []
        )
        assert other.matching == []
