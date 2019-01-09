""" Tests for the Player class. """

from hypothesis import given
from hypothesis.strategies import lists, text

from matching import Player


@given(name=text(), pref_names=lists(text(), min_size=1, max_size=10))
def test_repr(name, pref_names):
    """ Verify that a Player instance is represented by their name. """

    player = Player(name, pref_names)
    assert repr(player) == name


def test_get_favourite_simple():
    """ Check the correct player is returned as the favourite for a simple game
    scenario, i.e. when the player can have a single match. """

    player = Player(name="A", pref_names=["Y", "X", "Z"])
    others = [
        Player(name="X", pref_names=["A"]),
        Player(name="Y", pref_names=["A"]),
        Player(name="Z", pref_names=["A"]),
    ]

    favourite = others[1]
    assert player.get_favourite(others) == favourite


def test_get_favourite_capacitated():
    """ Check the correct player is returned as the favourite for a capacitated
    game scenario, i.e. when the player can have multiple matches at once. """

    player = Player(name="A", pref_names=["Y", "X", "Z"], capacity=2)
    others = [
        Player(name="X", pref_names=["A"]),
        Player(name="Y", pref_names=["A"]),
        Player(name="Z", pref_names=["A"]),
    ]

    favourite = others[1]
    assert player.get_favourite(others) == favourite

    player.match.append(favourite)

    favourite = others[0]
    assert player.get_favourite(others) == favourite


def test_get_worst_match_idx():
    """ Check that the preference index of the worst current match to a
    capacitated player can be found correctly. """

    player = Player(name="A", pref_names=["Y", "X", "Z"], capacity=2)
    others = [
        Player(name="X", pref_names=["A"]),
        Player(name="Y", pref_names=["A"]),
        Player(name="Z", pref_names=["A"]),
    ]

    player.match = [others[1], others[2], others[0]]
    worst_idx = 2
    assert player.get_worst_match_idx() == worst_idx

    player.match = [others[1], others[0]]
    worst_idx = 1
    assert player.get_worst_match_idx() == worst_idx
