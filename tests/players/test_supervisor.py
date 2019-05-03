""" Unit tests for the `Supervisor` class of players. """

from hypothesis import given
from hypothesis.strategies import integers, lists, text

from matching import Player as Student
from matching.players import Project, Supervisor


@given(name=text(), capacity=integers())
def test_init(name, capacity):
    """ Make an instance of Supervisor and check their attributes are correct.
    """

    supervisor = Supervisor(name, capacity)

    assert supervisor.name == name
    assert supervisor.capacity == capacity
    assert supervisor.projects == []
    assert supervisor.prefs is None
    assert supervisor.pref_names is None
    assert supervisor.matching == []


@given(name=text(), capacity=integers(), pref_names=lists(text(), min_size=1))
def test_set_prefs(name, capacity, pref_names):
    """ Test that a Supervisor can set its preferences correctly, and the
    preferences of its project(s). """

    supervisor = Supervisor(name, capacity)
    projects = [Project(i, capacity) for i in range(3)]
    students = []
    for sname in pref_names:
        student = Student(sname)
        student.prefs = projects
        students.append(student)

    supervisor.projects = projects
    supervisor.set_prefs(students)
    assert supervisor.prefs == students
    assert supervisor.pref_names == pref_names
    for project in supervisor.projects:
        assert project.prefs == students
        assert project.pref_names == pref_names
