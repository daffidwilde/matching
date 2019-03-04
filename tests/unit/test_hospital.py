""" Unit tests for the `Hospital` class of players. """

from hypothesis import given
from hypothesis.strategies import integers, lists, text

from matching import Player as Resident
from matching.players import Hospital


@given(name=text(), capacity=integers())
def test_init(name, capacity):
    """ Make an instance of Hospital and check their attributes are correct. """

    hospital = Hospital(name, capacity)

    assert hospital.name == name
    assert hospital.capacity == capacity
    assert hospital.prefs is None
    assert hospital.pref_names is None
    assert hospital.matching == []


@given(name=text(), capacity=integers(), pref_names=lists(text(), min_size=1))
def test_get_favourite(name, capacity, pref_names):
    """ Check the correct player is returned as the hospital's favourite. """

    hospital = Hospital(name, capacity)
    others = [Resident(other) for other in pref_names]

    hospital.set_prefs(others)
    assert hospital.get_favourite() == others[0]

    hospital.matching = others
    assert hospital.get_favourite() is None


@given(name=text(), capacity=integers(), pref_names=lists(text(), min_size=1))
def test_match(name, capacity, pref_names):
    """ Check that a hospital can match to a player correctly. """

    hospital = Hospital(name, capacity)
    others = [Resident(other) for other in pref_names]

    hospital.set_prefs(others)
    for i, other in enumerate(others[:-1]):
        hospital.match(other)
        assert hospital.matching == others[: i + 1]

    hospital.match(others[-1])
    assert hospital.matching == others


@given(name=text(), capacity=integers(), pref_names=lists(text(), min_size=1))
def test_unmatch(name, capacity, pref_names):
    """ Check that a hospital can unmatch from a player correctly. """

    hospital = Hospital(name, capacity)
    others = [Resident(other) for other in pref_names]

    hospital.matching = others
    for i, other in enumerate(others[:-1]):
        hospital.unmatch(other)
        assert hospital.matching == others[i + 1 :]

    hospital.unmatch(others[-1])
    assert hospital.matching == []


@given(name=text(), capacity=integers(), pref_names=lists(text(), min_size=1))
def test_get_worst_match(name, capacity, pref_names):
    """ Check that a hospital can return its worst match. """

    hospital = Hospital(name, capacity)
    others = [Resident(other) for other in pref_names]

    hospital.matching = [others[0]]
    assert hospital.get_worst_match() == others[0]

    hospital.matching = others
    assert hospital.get_worst_match() == others[-1]


@given(name=text(), capacity=integers(), pref_names=lists(text(), min_size=1))
def test_get_successors(name, capacity, pref_names):
    """ Check that a hospital can get the successors to its worst current match.
    """

    hospital = Hospital(name, capacity)
    others = [Resident(other) for other in pref_names]

    hospital.set_prefs(others)
    hospital.matching = [others[0]]
    assert hospital.get_successors() == others[1:]

    hospital.matching = others
    assert hospital.get_successors() == []
