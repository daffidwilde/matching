""" Unit tests for the `Faculty` class of players. """

from hypothesis import given
from hypothesis.strategies import integers, lists, text

from matching import Player as Student
from matching.players import Faculty, Project


@given(name=text(), capacity=integers())
def test_init(name, capacity):
    """ Make an instance of Faculty and check their attributes are correct. """

    faculty = Faculty(name, capacity)

    assert faculty.name == name
    assert faculty.capacity == capacity
    assert faculty.projects == []
    assert faculty.prefs is None
    assert faculty.pref_names is None
    assert faculty.matching == []

