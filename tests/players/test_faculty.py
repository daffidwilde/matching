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


@given(name=text(), capacity=integers(), pref_names=lists(text(), min_size=1))
def test_set_prefs(name, capacity, pref_names):
    """ Test that a Faculty can set its preferences correctly, and the
    preferences of its project(s). """

    faculty = Faculty(name, capacity)
    projects = [Project(i, capacity) for i in range(3)]
    students = []
    for name in pref_names:
        student = Student(name)
        student.prefs = projects
        students.append(student)

    faculty.projects = projects
    faculty.set_prefs(students)
    assert faculty.prefs == students
    assert faculty.pref_names == pref_names
    for project in faculty.projects:
        assert project.prefs == students
        assert project.pref_names == pref_names
