""" Tests for the Player class. """

from hypothesis import given
from hypothesis.strategies import lists, text

from matching import Player


@given(name=text())
def test_init(name):
    """ Make an instance of Player and check their attributes are correct. """

    player = Player(name)

    assert player.name == name
    assert player.prefs is None
    assert player.pref_names is None
    assert player.matching is None


@given(name=text())
def test_repr(name):
    """ Verify that a Player instance is represented by their name. """

    player = Player(name)

    assert repr(player) == name


@given(name=text(), pref_names=lists(text(), min_size=1))
def test_set_prefs(name, pref_names):
    """ Verify a Player can set its preferences correctly. """

    player = Player(name)
    others = [Player(other) for other in pref_names]

    player.set_prefs(others)
    assert player.prefs == others
    assert player.pref_names == [other.name for other in others]


@given(name=text(), pref_names=lists(text(), min_size=1))
def test_get_favourite(name, pref_names):
    """ Check the correct player is returned as the favourite of a player. """

    player = Player(name)
    others = [Player(other) for other in pref_names]

    player.set_prefs(others)
    favourite = others[0]
    assert player.get_favourite() == favourite


@given(name=text(), pref_names=lists(text(), min_size=1))
def test_match(name, pref_names):
    """ Check that a player can match to another player correctly. """

    player = Player(name)
    other = Player(pref_names[0])

    player.match(other)
    assert player.matching == other


@given(name=text(), pref_names=lists(text(), min_size=1))
def test_unmatch(name, pref_names):
    """ Check that a player can unmatch from another player correctly. """

    player = Player(name)
    other = Player(pref_names[0])

    player.matching = other
    player.unmatch()
    assert player.matching is None


@given(name=text(), pref_names=lists(text(), min_size=1))
def test_forget(name, pref_names):
    """ Test that a player can forget somebody. """

    player = Player(name)
    others = [Player(other) for other in pref_names]

    player.set_prefs(others)
    for i, other in enumerate(others[:-1]):
        player.forget(other)
        assert player.prefs == others[i + 1 :]

    player.forget(others[-1])
    assert player.prefs == []
    assert player.pref_names == pref_names


@given(name=text(), pref_names=lists(text(), min_size=1))
def test_get_successors(name, pref_names):
    """ Test that the correct successors to another player in a player's
    preference list are found. """

    player = Player(name)
    others = [Player(other) for other in pref_names]

    player.set_prefs(others)
    player.matching = others[0]
    if len(player.pref_names) > 1:
        successors = others[1:]
        assert player.get_successors() == successors
    else:
        assert player.get_successors() == []


@given(name=text(), pref_names=lists(text(), min_size=1, unique=True))
def test_prefers(name, pref_names):
    """ Test that a comparison of preference between two other players can be
    found for a player. """

    player = Player(name)
    others = [Player(other) for other in pref_names]

    player.set_prefs(others)
    for i, other in enumerate(others[:-1]):
        assert player.prefers(other, others[i + 1])
