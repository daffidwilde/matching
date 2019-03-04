""" Unit tests for the `Project` class of players. """

from hypothesis import given
from hypothesis.strategies import integers, lists, text

from matching import Project


@given(name=text(), capacity=integers())
def test_init(name, capacity):
    """ Make an instance of Project and check their attributes are correct. """

    project = Project(name, capacity)

    assert project.name == name
    assert project.capacity == capacity
    assert project.faculty is None
    assert project.prefs is None
    assert project.pref_names is None
    assert project.matching == []
