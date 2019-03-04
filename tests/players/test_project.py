""" Unit tests for the `Project` class of players. """

from hypothesis import given
from hypothesis.strategies import integers, lists, text

from matching import Player as Student
from matching.players import Faculty, Project


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


@given(name=text(), capacity=integers())
def test_set_faculty(name, capacity):
    """ Check that a project can update its faculty member and that it is added
    to the faculty's project list. """

    project = Project(name, capacity)
    faculty = Faculty("foo", capacity)

    project.set_faculty(faculty)
    assert project.faculty == faculty
    assert faculty.projects == [project]


@given(name=text(), capacity=integers(), pref_names=lists(text(), min_size=1))
def test_match(name, capacity, pref_names):
    """ Check that a project can match to a student, and match its faculty to
    them, too. """

    project = Project(name, capacity)
    faculty = Faculty("foo", capacity)
    project.faculty = faculty
    students = [Student(student) for student in pref_names]

    project.prefs = students
    faculty.prefs = students
    for i, student in enumerate(students[:-1]):
        project.match(student)
        assert project.matching == students[: i + 1]
        assert faculty.matching == students[: i + 1]

    project.match(students[-1])
    assert project.matching == students
    assert faculty.matching == students


@given(name=text(), capacity=integers(), pref_names=lists(text(), min_size=1))
def test_unmatch(name, capacity, pref_names):
    """ Check that a project can break a matching with a student, and break that
    matching for their faculty member, too. """

    project = Project(name, capacity)
    faculty = Faculty("foo", capacity)
    project.faculty = faculty
    students = [Student(student) for student in pref_names]

    project.matching = students
    faculty.matching = students
    for i, student in enumerate(students[:-1]):
        project.unmatch(student)
        assert project.matching == students[i + 1 :]
        assert faculty.matching == students[i + 1 :]

    project.unmatch(students[-1])
    assert project.matching == []
    assert faculty.matching == []
