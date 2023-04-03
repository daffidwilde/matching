"""Unit tests for the `Supervisor` player class."""

from hypothesis import given
from hypothesis.strategies import integers, lists, text

from matching import Player as Student
from matching.players import Project, Supervisor


@given(name=text(), capacity=integers())
def test_init(name, capacity):
    """Test for correct supervisor instantiation."""

    supervisor = Supervisor(name, capacity)

    assert supervisor.name == name
    assert supervisor.capacity == capacity
    assert supervisor.projects == []
    assert supervisor.prefs == []
    assert supervisor.matching == []
    assert supervisor._pref_names == []
    assert supervisor._original_prefs is None


@given(name=text(), capacity=integers(), pref_names=lists(text(), min_size=1))
def test_set_prefs(name, capacity, pref_names):
    """Test that a supervisor can set its preferences correctly.

    This also means passing on their preferences to the correct
    project(s).
    """

    supervisor = Supervisor(name, capacity)
    projects = [Project(i, capacity) for i in range(3)]
    students = []
    for sname in pref_names:
        student = Student(sname)
        student.set_prefs(projects)
        students.append(student)

    supervisor.projects = projects
    supervisor.set_prefs(students)
    assert supervisor.prefs == students
    assert supervisor._pref_names == pref_names
    assert supervisor._original_prefs == students

    for project in supervisor.projects:
        assert project.prefs == students
        assert project._pref_names == pref_names
        assert project._original_prefs == students
