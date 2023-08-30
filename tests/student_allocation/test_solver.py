"""Unit tests for the SA solver."""

import warnings

import pytest

from matching import MultipleMatching
from matching import Player as Student
from matching.exceptions import (
    CapacityChangedWarning,
    MatchingError,
    PreferencesChangedWarning,
)
from matching.games import StudentAllocation
from matching.players import Project, Supervisor

from .util import STUDENT_ALLOCATION, make_connections, make_game


@STUDENT_ALLOCATION
def test_init(
    student_names, project_names, supervisor_names, capacities, seed, clean
):
    """Test for correct instantiation given some players."""

    students, projects, supervisors, game = make_game(
        student_names, project_names, supervisor_names, capacities, seed, clean
    )

    for student, game_student in zip(students, game.students):
        assert student.name == game_student.name
        assert student._pref_names == game_student._pref_names

    for project, game_project in zip(projects, game.projects):
        assert project.name == game_project.name
        assert project._pref_names == game_project._pref_names
        assert project.capacity == game_project.capacity
        assert project.supervisor.name == game_project.supervisor.name

    for supervisor, game_supervisor in zip(supervisors, game.supervisors):
        assert supervisor.name == game_supervisor.name
        assert supervisor._pref_names == game_supervisor._pref_names
        assert supervisor.capacity == game_supervisor.capacity

        supervisor_projects = [p.name for p in supervisor.projects]
        game_supervisor_projects = [p.name for p in game_supervisor.projects]
        assert supervisor_projects == game_supervisor_projects

    assert all([student.matching is None for student in game.students])
    assert all([project.matching == [] for project in game.projects])
    assert all([supervisor.matching == [] for supervisor in game.supervisors])
    assert game.matching is None
    assert game.blocking_pairs is None
    assert game.clean is clean


@STUDENT_ALLOCATION
def test_create_from_dictionaries(
    student_names, project_names, supervisor_names, capacities, seed, clean
):
    """Test for correct instantiation given from dictionaries."""

    stud_prefs, sup_prefs, proj_sups, proj_caps, sup_caps = make_connections(
        student_names, project_names, supervisor_names, capacities, seed
    )

    game = StudentAllocation.create_from_dictionaries(
        stud_prefs, sup_prefs, proj_sups, proj_caps, sup_caps, clean
    )

    for student in game.students:
        assert student._pref_names == stud_prefs[student.name]
        assert student.matching is None

    for project in game.projects:
        assert project.supervisor.name == proj_sups[project.name]
        assert project.matching == []

    for supervisor in game.supervisors:
        assert supervisor._pref_names == sup_prefs[supervisor.name]
        assert supervisor.matching == []

    assert game.matching is None
    assert game.clean is clean


@STUDENT_ALLOCATION
def test_remove_supervisor_and_projects(
    student_names, project_names, supervisor_names, capacities, seed, clean
):
    """Test that a supervisor and its projects can be removed."""

    *_, game = make_game(
        student_names, project_names, supervisor_names, capacities, seed, clean
    )

    supervisor = game.supervisors[0]
    projects = supervisor.projects

    game._remove_player(supervisor, "supervisors")
    assert supervisor not in game.supervisors
    assert all(project not in game.projects for project in projects)


@STUDENT_ALLOCATION
def test_remove_student(
    student_names, project_names, supervisor_names, capacities, seed, clean
):
    """Test that a student can be removed."""

    *_, game = make_game(
        student_names, project_names, supervisor_names, capacities, seed, clean
    )

    student = game.students[0]

    game._remove_player(student, "students", "projects")
    assert student not in game.students


@STUDENT_ALLOCATION
def test_check_inputs(
    student_names, project_names, supervisor_names, capacities, seed, clean
):
    """Test that inputs to an instance of SA can be verified."""

    *_, game = make_game(
        student_names, project_names, supervisor_names, capacities, seed, clean
    )

    with warnings.catch_warnings(record=True):
        warnings.simplefilter("error")
        game.check_inputs()

    assert game.students == game._all_students
    assert game.projects == game._all_projects
    assert game.supervisors == game._all_supervisors


@STUDENT_ALLOCATION
def test_check_inputs_project_prefs_all_reciprocated(
    student_names, project_names, supervisor_names, capacities, seed, clean
):
    """Test that each project has ranked only students that ranked it.

    If not, check that a warning is caught and the project has forgotten
    any such students.
    """

    *_, game = make_game(
        student_names, project_names, supervisor_names, capacities, seed, clean
    )

    project = game.projects[0]
    student = project.prefs[0]
    student._forget(project)

    with pytest.warns(PreferencesChangedWarning) as record:
        game._check_inputs_player_prefs_all_reciprocated("projects")

    assert len(record) == 1

    message = str(record[0].message)

    assert message.startswith(project.name)
    assert student.name in message

    if clean:
        assert student not in project.prefs


@STUDENT_ALLOCATION
def test_check_inputs_supervisor_prefs_all_reciprocated(
    student_names, project_names, supervisor_names, capacities, seed, clean
):
    """Test that each supervisor has ranked only students who ranked it.

    If not, check that a warning is caught and the supervisor and its
    projects have forgotten any such students.
    """

    *_, game = make_game(
        student_names, project_names, supervisor_names, capacities, seed, clean
    )

    supervisor = game.supervisors[0]
    student = supervisor.prefs[0]
    projects = supervisor.projects
    for project in student.prefs:
        if project in projects:
            student._forget(project)

    with pytest.warns(PreferencesChangedWarning) as record:
        game._check_inputs_player_prefs_all_reciprocated("supervisors")

    assert len(record) == 1

    message = str(record[0].message)

    assert message.startswith(supervisor.name)
    assert student.name in message

    if clean:
        assert student not in supervisor.prefs
        assert all(
            student not in project.prefs for project in supervisor.projects
        )


@STUDENT_ALLOCATION
def test_check_inputs_project_reciprocated_all_prefs(
    student_names, project_names, supervisor_names, capacities, seed, clean
):
    """Test that each project has ranked all students that ranked it.

    If not, check that a warning is caught and any such student has
    forgotten the project.
    """

    *_, game = make_game(
        student_names, project_names, supervisor_names, capacities, seed, clean
    )

    project = game.projects[0]
    student = project.prefs[0]
    project._forget(student)

    with pytest.warns(PreferencesChangedWarning) as record:
        game._check_inputs_player_reciprocated_all_prefs(
            "projects", "students"
        )

    assert len(record) == 1

    message = str(record[0].message)

    assert message.startswith(student.name)
    assert project.name in message

    if clean:
        assert project not in student.prefs


@STUDENT_ALLOCATION
def test_check_inputs_supervisor_reciprocated_all_prefs(
    student_names, project_names, supervisor_names, capacities, seed, clean
):
    """Test that each supervisor ranked all students who ranked "them".

    That is, all students who ranked at least one of its projects. If
    not, check that a warning is caught and any such student has
    forgotten all projects belonging to that supervisor.
    """

    *_, game = make_game(
        student_names, project_names, supervisor_names, capacities, seed, clean
    )

    supervisor = game.supervisors[0]
    student = supervisor.prefs[0]
    supervisor.prefs.remove(student)

    with pytest.warns(PreferencesChangedWarning) as record:
        game._check_inputs_player_reciprocated_all_prefs(
            "supervisors", "students"
        )

    assert len(record) == 1

    message = str(record[0].message)

    assert message.startswith(student.name)
    assert supervisor.name in message

    if clean:
        assert supervisor not in student.prefs
        assert all(
            project not in student.prefs for project in supervisor.projects
        )


@STUDENT_ALLOCATION
def test_check_inputs_supervisor_capacities_sufficient(
    student_names, project_names, supervisor_names, capacities, seed, clean
):
    """Test that each project is no larger than its supervisor.

    If not, check that a warning is caught and that their capacity is
    updated to their supervisor's.
    """

    *_, game = make_game(
        student_names, project_names, supervisor_names, capacities, seed, clean
    )

    project = game.projects[0]
    supervisor_capacity = project.supervisor.capacity
    project.capacity = supervisor_capacity + 1

    with pytest.warns(CapacityChangedWarning) as record:
        game._check_inputs_supervisor_capacities_sufficient()

    assert len(record) == 1

    message = str(record[0].message)

    assert message.startswith(project.name)
    assert str(project.capacity) in message
    assert str(supervisor_capacity) in message

    if clean:
        assert project.capacity == supervisor_capacity


@STUDENT_ALLOCATION
def test_check_inputs_supervisor_capacities_necessary(
    student_names, project_names, supervisor_names, capacities, seed, clean
):
    """Test that each supervisor does not have surplus capacity.

    If not, check that a warning is caught and that their capacity is
    updated to be the sum of its projects.
    """

    *_, game = make_game(
        student_names, project_names, supervisor_names, capacities, seed, clean
    )

    supervisor = game.supervisors[0]
    total_project_capacity = sum(p.capacity for p in supervisor.projects)
    supervisor.capacity = total_project_capacity + 1

    with pytest.warns(CapacityChangedWarning) as record:
        game._check_inputs_supervisor_capacities_necessary()

    assert len(record) == 1

    message = str(record[0].message)

    assert message.startswith(supervisor.name)
    assert str(supervisor.capacity) in message
    assert str(total_project_capacity) in message

    if clean:
        assert supervisor.capacity == total_project_capacity


@STUDENT_ALLOCATION
def test_solve(
    student_names, project_names, supervisor_names, capacities, seed, clean
):
    """Test that the class can solve games correctly."""

    for optimal in ["student", "supervisor"]:
        students, projects, _, game = make_game(
            student_names,
            project_names,
            supervisor_names,
            capacities,
            seed,
            clean,
        )

        matching = game.solve(optimal)
        assert isinstance(matching, MultipleMatching)

        projects = sorted(projects, key=lambda p: p.name)
        matching_keys = sorted(matching.keys(), key=lambda k: k.name)
        for game_project, project in zip(matching_keys, projects):
            assert game_project.name == project.name
            assert game_project._pref_names == project._pref_names
            assert game_project.capacity == project.capacity
            assert game_project.supervisor.name == project.supervisor.name

        matched_students = [
            stud for match in matching.values() for stud in match
        ]
        assert matched_students != [] and set(matched_students).issubset(
            set(game.students)
        )

        for student in matched_students:
            supervisor = student.matching.supervisor
            assert student in supervisor.matching

        for student in set(game.students) - set(matched_students):
            assert student.matching is None


@STUDENT_ALLOCATION
def test_check_validity(
    student_names, project_names, supervisor_names, capacities, seed, clean
):
    """Test for a valid matching when the game is solved."""

    *_, game = make_game(
        student_names, project_names, supervisor_names, capacities, seed, clean
    )

    game.solve()
    assert game.check_validity()


@STUDENT_ALLOCATION
def test_check_for_unacceptable_matches_students(
    student_names, project_names, supervisor_names, capacities, seed, clean
):
    """Test that each matched student must have ranked their match."""

    *_, game = make_game(
        student_names, project_names, supervisor_names, capacities, seed, clean
    )
    game.solve()

    student = game.students[0]
    project = Project(name="foo", capacity=0)
    student.matching = project

    with pytest.raises(MatchingError) as e:
        game.check_validity()
        error = e.unacceptable_matches[0]
        assert error.startswith(student.name)
        assert error.endswith(str(student.prefs))
        assert project.name in error


@STUDENT_ALLOCATION
def test_check_for_unacceptable_matches_projects(
    student_names, project_names, supervisor_names, capacities, seed, clean
):
    """Test that each project must rank all their matches."""

    *_, game = make_game(
        student_names, project_names, supervisor_names, capacities, seed, clean
    )
    game.solve()

    project = game.projects[0]
    student = Student(name="foo")
    project.matching.append(student)

    with pytest.raises(MatchingError) as e:
        game.check_validity()
        error = e.unacceptable_matches[0]
        assert error.startswith(project.name)
        assert error.endswith(str(project.prefs))
        assert str(student.name) in error


@STUDENT_ALLOCATION
def test_check_for_unacceptable_matches_supervisors(
    student_names, project_names, supervisor_names, capacities, seed, clean
):
    """Test that each supervisor must rank all their matches."""

    *_, game = make_game(
        student_names, project_names, supervisor_names, capacities, seed, clean
    )
    game.solve()

    supervisor = game.supervisors[0]
    student = Student(name="foo")
    supervisor.matching.append(student)

    with pytest.raises(MatchingError) as e:
        game.check_validity()
        error = e.unacceptable_matches[0]
        assert error.startswith(supervisor.name)
        assert error.endswith(str(supervisor.prefs))
        assert student.name in error


@STUDENT_ALLOCATION
def test_check_for_oversubscribed_projects(
    student_names, project_names, supervisor_names, capacities, seed, clean
):
    """Test that all projects must not be over-subscribed."""

    *_, game = make_game(
        student_names, project_names, supervisor_names, capacities, seed, clean
    )
    game.solve()

    project = game.projects[0]
    project.matching = range(project.capacity + 1)

    with pytest.raises(MatchingError) as e:
        game.check_validity()
        error = e.oversubscribed_players[0]
        assert error.startswith(project.name)
        assert error.endswith(str(project.capacity))
        assert str(project.matching) in e


@STUDENT_ALLOCATION
def test_check_for_oversubscribed_supervisors(
    student_names, project_names, supervisor_names, capacities, seed, clean
):
    """Test that all supervisors must not be over-subscribed."""

    *_, game = make_game(
        student_names, project_names, supervisor_names, capacities, seed, clean
    )
    game.solve()

    supervisor = game.supervisors[0]
    supervisor.matching = range(supervisor.capacity + 1)

    with pytest.raises(MatchingError) as e:
        game.check_validity()
        error = e.oversubscribed_players[0]
        assert error.startswith(supervisor.name)
        assert error.endswith(str(supervisor.capacity))
        assert str(supervisor.matching) in e


def test_check_stability():
    """Test checker for whether a matching is stable or not."""

    students = [Student("A"), Student("B"), Student("C")]
    projects = [Project("P", 2), Project("Q", 2)]
    supervisors = [Supervisor("X", 2), Supervisor("Y", 2)]

    (a, b, c), (p, q), (x, y) = students, projects, supervisors

    p.set_supervisor(x)
    q.set_supervisor(y)

    a.set_prefs([p, q])
    b.set_prefs([q])
    c.set_prefs([q, p])

    x.set_prefs([c, a])
    y.set_prefs([a, b, c])

    game = StudentAllocation(students, projects, supervisors)

    matching = game.solve()
    assert game.check_stability()

    (a, b, c), (p, q) = game.students, game.projects

    matching[p] = [c]
    matching[q] = [a, b]

    assert not game.check_stability()
