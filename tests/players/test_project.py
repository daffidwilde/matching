"""Unit tests for the `Project` player class."""

from hypothesis import given
from hypothesis.strategies import integers, lists, text

from matching import Player as Student
from matching.players import Project, Supervisor


@given(name=text(), capacity=integers())
def test_init(name, capacity):
    """Test for correct project instantiation."""

    project = Project(name, capacity)

    assert project.name == name
    assert project.capacity == capacity
    assert project.supervisor is None
    assert project.prefs == []
    assert project.matching == []
    assert project._pref_names == []
    assert project._original_prefs is None


@given(name=text(), capacity=integers())
def test_set_supervisor(name, capacity):
    """Test that a project can set its supervisor and their projects."""

    project = Project(name, capacity)
    supervisor = Supervisor("foo", capacity)

    project.set_supervisor(supervisor)
    assert project.supervisor == supervisor
    assert supervisor.projects == [project]


@given(name=text(), capacity=integers(), pref_names=lists(text(), min_size=1))
def test_match(name, capacity, pref_names):
    """Test that a project can match to a student.

    This also means matching its supervisor to the student.
    """

    project = Project(name, capacity)
    supervisor = Supervisor("foo", capacity)
    project.supervisor = supervisor
    students = [Student(student) for student in pref_names]

    project.prefs = students
    supervisor.prefs = students
    for i, student in enumerate(students[:-1]):
        project._match(student)
        assert project.matching == students[: i + 1]
        assert supervisor.matching == students[: i + 1]

    project._match(students[-1])
    assert project.matching == students
    assert supervisor.matching == students


@given(name=text(), capacity=integers(), pref_names=lists(text(), min_size=1))
def test_unmatch(name, capacity, pref_names):
    """Test that a project can break a matching with a student.

    This also means potentially breaking that matching for their
    supervisor.
    """

    project = Project(name, capacity)
    supervisor = Supervisor("foo", capacity)
    project.supervisor = supervisor
    students = [Student(student) for student in pref_names]

    project.matching = students
    supervisor.matching = students
    for i, student in enumerate(students[:-1]):
        project._unmatch(student)
        assert project.matching == students[i + 1 :]
        assert supervisor.matching == students[i + 1 :]

    project._unmatch(students[-1])
    assert project.matching == []
    assert supervisor.matching == []
