"""Unit tests for the `Hospital` player class."""

from hypothesis import given
from hypothesis.strategies import integers, lists, text

from matching import Player as Resident
from matching.players import Hospital

capacity = integers(min_value=1)
pref_names = lists(text(), min_size=1)


@given(name=text(), capacity=capacity)
def test_init(name, capacity):
    """Test for correct hospital instantiation."""

    hospital = Hospital(name, capacity)

    assert hospital.name == name
    assert hospital.capacity == capacity
    assert hospital.prefs == []
    assert hospital.matching == []
    assert hospital._pref_names == []
    assert hospital._original_prefs is None
    assert hospital._original_capacity == capacity


@given(name=text(), capacity=capacity, pref_names=pref_names)
def test_get_favourite(name, capacity, pref_names):
    """Test for finding a hospital's favourite feasible resident."""

    hospital = Hospital(name, capacity)
    others = [Resident(other) for other in pref_names]

    hospital.set_prefs(others)
    assert hospital.get_favourite() == others[0]

    hospital.matching = others
    assert hospital.get_favourite() is None


@given(name=text(), capacity=capacity, pref_names=pref_names)
def test_match(name, capacity, pref_names):
    """Test that a hospital can match to a player correctly."""

    hospital = Hospital(name, capacity)
    others = [Resident(other) for other in pref_names]

    hospital.set_prefs(others)
    for i, other in enumerate(others[:-1]):
        hospital._match(other)
        assert hospital.matching == others[: i + 1]

    hospital._match(others[-1])
    assert hospital.matching == others


@given(name=text(), capacity=capacity, pref_names=pref_names)
def test_unmatch(name, capacity, pref_names):
    """Test that a hospital can unmatch from a player correctly."""

    hospital = Hospital(name, capacity)
    others = [Resident(other) for other in pref_names]

    hospital.matching = others
    for i, other in enumerate(others[:-1]):
        hospital._unmatch(other)
        assert hospital.matching == others[i + 1 :]

    hospital._unmatch(others[-1])
    assert hospital.matching == []


@given(name=text(), capacity=capacity, pref_names=pref_names)
def test_get_worst_match(name, capacity, pref_names):
    """Test that a hospital can return its worst match."""

    hospital = Hospital(name, capacity)
    others = [Resident(other) for other in pref_names]

    hospital.matching = [others[0]]
    assert hospital.get_worst_match() == others[0]

    hospital.matching = others
    assert hospital.get_worst_match() == others[-1]


@given(name=text(), capacity=capacity, pref_names=pref_names)
def test_get_successors(name, capacity, pref_names):
    """Test that a hospital can get its successors.

    Successors are residents lower on their preference list than their
    worst current match. If no such successors exist, check for an empty
    list.
    """

    hospital = Hospital(name, capacity)
    others = [Resident(other) for other in pref_names]

    hospital.set_prefs(others)
    hospital.matching = [others[0]]
    assert hospital.get_successors() == others[1:]

    hospital.matching = others
    assert hospital.get_successors() == []


@given(name=text(), capacity=capacity, pref_names=pref_names)
def test_check_if_match_is_unacceptable(name, capacity, pref_names):
    """Test for the acceptability of a hospital's matches."""

    hospital = Hospital(name, capacity)
    others = [Resident(other) for other in pref_names]

    assert hospital.check_if_match_is_unacceptable() == []

    hospital.set_prefs(others[:-1])
    hospital.matching = [others[-1]]
    message = hospital.not_in_preferences_message(others[-1])
    assert hospital.check_if_match_is_unacceptable() == [message]


@given(name=text(), capacity=capacity, pref_names=pref_names)
def test_check_if_oversubscribed(name, capacity, pref_names):
    """Test that a hospital can verify whether it is oversubscribed."""

    hospital = Hospital(name, capacity)
    others = [Resident(other) for other in pref_names]

    assert hospital.check_if_oversubscribed() is False

    hospital.matching = others
    hospital.capacity = 0
    message = hospital.oversubscribed_message()
    assert hospital.check_if_oversubscribed() == message
