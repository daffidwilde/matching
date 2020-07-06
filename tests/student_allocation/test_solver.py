""" Unit tests for the SA solver. """
import warnings

import pytest

from matching import Matching
from matching import Player as Student
from matching.games import StudentAllocation
from matching.players import Project, Supervisor
from matching.warning import (
    InvalidCapacityWarning,
    InvalidPreferencesWarning,
    PlayerExcludedWarning,
)

from .params import STUDENT_ALLOCATION, make_connections, make_game


@STUDENT_ALLOCATION
def test_init(student_names, project_names, supervisor_names, capacities, seed):
    """ Test that an instance of StudentAllocation is created correctly when
    passed a set of players. """

    students, projects, supervisors, game = make_game(
        student_names, project_names, supervisor_names, capacities, seed
    )

    for student, game_student in zip(students, game.students):
        assert student.name == game_student.name
        assert student.pref_names == game_student.pref_names

    for project, game_project in zip(projects, game.projects):
        assert project.name == game_project.name
        assert project.pref_names == game_project.pref_names
        assert project.capacity == game_project.capacity
        assert project.supervisor.name == game_project.supervisor.name

    for supervisor, game_supervisor in zip(supervisors, game.supervisors):
        assert supervisor.name == game_supervisor.name
        assert supervisor.pref_names == game_supervisor.pref_names
        assert supervisor.capacity == game_supervisor.capacity

        supervisor_projects = [p.name for p in supervisor.projects]
        game_supervisor_projects = [p.name for p in game_supervisor.projects]
        assert supervisor_projects == game_supervisor_projects

    assert all([student.matching is None for student in game.students])
    assert all([project.matching == [] for project in game.projects])
    assert all([supervisor.matching == [] for supervisor in game.supervisors])
    assert game.matching is None
    assert game.blocking_pairs is None


@STUDENT_ALLOCATION
def test_create_from_dictionaries(
    student_names, project_names, supervisor_names, capacities, seed
):
    """ Test that StudentAllocation is created correctly when passed
    dictionaries of preferences and affiliations for each party. """

    stud_prefs, sup_prefs, proj_sups, sup_caps = make_connections(
        student_names, project_names, supervisor_names, capacities, seed
    )

    proj_caps = dict(zip(project_names, capacities))
    game = StudentAllocation.create_from_dictionaries(
        stud_prefs, sup_prefs, proj_sups, proj_caps, sup_caps
    )

    for student in game.students:
        assert student.pref_names == stud_prefs[student.name]
        assert student.matching is None

    for project in game.projects:
        assert project.supervisor.name == proj_sups[project.name]
        assert project.matching == []

    for supervisor in game.supervisors:
        assert supervisor.pref_names == sup_prefs[supervisor.name]
        assert supervisor.matching == []

    assert game.matching is None


@STUDENT_ALLOCATION
def test_inputs_student_prefs_all_projects(
    student_names, project_names, supervisor_names, capacities, seed
):
    """ Test that every student has only projects in its preference list. If
    not, check that a warning is caught and the player's preferences are
    changed. """

    _, _, _, game = make_game(
        student_names, project_names, supervisor_names, capacities, seed
    )

    with warnings.catch_warnings(record=True) as w:
        game._check_student_prefs_all_projects()

        assert not w
        assert game.students == game._all_students

    student = game.students[0]
    student.prefs = [Student("foo")]
    with warnings.catch_warnings(record=True) as w:
        game._check_student_prefs_all_projects()

        message = w[-1].message
        assert isinstance(message, InvalidPreferencesWarning)
        assert student.name in str(message)
        assert "foo" in str(message)
        assert student.prefs == []


@STUDENT_ALLOCATION
def test_inputs_student_prefs_all_nonempty(
    student_names, project_names, supervisor_names, capacities, seed
):
    """ Test that every student has a non-empty preference list. If not, check
    that a warning is caught and the player has been removed from the game. """

    _, _, _, game = make_game(
        student_names, project_names, supervisor_names, capacities, seed
    )

    with warnings.catch_warnings(record=True) as w:
        game._check_student_prefs_all_nonempty()

        assert not w
        assert game.students == game._all_students

    student = game.students[0]
    student.prefs = []
    with warnings.catch_warnings(record=True) as w:
        game._check_student_prefs_all_nonempty()

        message = w[-1].message
        assert isinstance(message, PlayerExcludedWarning)
        assert student.name in str(message)
        assert student not in game.students


@STUDENT_ALLOCATION
def test_inputs_project_prefs_all_reciprocate(
    student_names, project_names, supervisor_names, capacities, seed
):
    """ Test that each project has ranked only those students that have ranked
    it. If not, check that a warning is caught and the project has forgotten any
    such players. """

    _, _, _, game = make_game(
        student_names, project_names, supervisor_names, capacities, seed
    )

    with warnings.catch_warnings(record=True) as w:
        game._check_project_prefs_all_reciprocated()

        assert not w
        assert game.projects == game._all_projects

    project = game.projects[0]
    student = project.prefs[0]
    student.forget(project)
    with warnings.catch_warnings(record=True) as w:
        game._check_project_prefs_all_reciprocated()

        message = w[-1].message
        assert isinstance(message, InvalidPreferencesWarning)
        assert project.name in str(message)
        assert student.name in str(message)
        assert student not in project.prefs


@STUDENT_ALLOCATION
def test_inputs_project_reciprocates_all_prefs(
    student_names, project_names, supervisor_names, capacities, seed
):
    """ Test that each project has ranked all those students that have ranked
    it. If not, check that a warning is caught and any such student has
    forgotten the project. """

    _, _, _, game = make_game(
        student_names, project_names, supervisor_names, capacities, seed
    )

    with warnings.catch_warnings(record=True) as w:
        game._check_project_reciprocates_all_prefs()

        assert not w
        assert game.projects == game._all_projects

    project = game.projects[0]
    student = project.prefs[0]
    project.forget(student)
    with warnings.catch_warnings(record=True) as w:
        game._check_project_reciprocates_all_prefs()

        message = w[-1].message
        assert isinstance(message, InvalidPreferencesWarning)
        assert project.name in str(message)
        assert student.name in str(message)
        assert project not in student.prefs


@STUDENT_ALLOCATION
def test_inputs_project_prefs_all_nonempty(
    student_names, project_names, supervisor_names, capacities, seed
):
    """ Test that each project has a non-empty preference list. If not, check
    that a warning is caught and the project has been removed from the game. """

    _, _, _, game = make_game(
        student_names, project_names, supervisor_names, capacities, seed
    )

    with warnings.catch_warnings(record=True) as w:
        game._check_project_prefs_all_nonempty()

        assert not w
        assert game.projects == game._all_projects

    project = game.projects[0]
    project.prefs = []
    with warnings.catch_warnings(record=True) as w:
        game._check_project_prefs_all_nonempty()

        message = w[-1].message
        assert isinstance(message, PlayerExcludedWarning)
        assert project.name in str(message)
        assert project not in game.projects


@STUDENT_ALLOCATION
def test_inputs_supervisor_prefs_all_reciprocate(
    student_names, project_names, supervisor_names, capacities, seed
):
    """ Test that each supervisor has ranked only those students that have
    ranked at least one of its projects. If not, check that a warning is caught
    and the supervisor has forgotten any such players. """

    _, _, _, game = make_game(
        student_names, project_names, supervisor_names, capacities, seed
    )

    with warnings.catch_warnings(record=True) as w:
        game._check_supervisor_prefs_all_reciprocated()

        assert not w
        assert game.supervisors == game._all_supervisors

    supervisor = game.supervisors[0]
    student = supervisor.prefs[0]
    for project in student.prefs:
        if project.supervisor == supervisor:
            student.forget(project)
            project.prefs.remove(student)

    with warnings.catch_warnings(record=True) as w:

        game._check_supervisor_prefs_all_reciprocated()

        message = w[-1].message
        assert isinstance(message, InvalidPreferencesWarning)
        assert supervisor.name in str(message)
        assert student.name in str(message)
        assert student not in supervisor.prefs


@STUDENT_ALLOCATION
def test_inputs_supervisor_reciprocates_all_prefs(
    student_names, project_names, supervisor_names, capacities, seed
):
    """ Test that each supervisor has ranked all those students that have ranked
    at least one of its projects. If not, check that a warning is caught and any
    such student has forgotten all projects belonging to that supervisor. """

    _, _, _, game = make_game(
        student_names, project_names, supervisor_names, capacities, seed
    )

    with warnings.catch_warnings(record=True) as w:
        game._check_supervisor_reciprocates_all_prefs()

        assert not w
        assert game.supervisors == game._all_supervisors

    supervisor = game.supervisors[0]
    student = supervisor.prefs[0]
    supervisor.prefs.remove(student)
    with warnings.catch_warnings(record=True) as ws:
        game._check_supervisor_reciprocates_all_prefs()

        w, *ws = ws
        message = w.message
        assert isinstance(message, InvalidPreferencesWarning)
        assert supervisor.name in str(message)
        assert student.name in str(message)
        assert supervisor not in student.prefs

        messages = " ".join((str(w.message) for w in ws))
        for project in supervisor.projects:
            if project in student._original_prefs:
                assert project not in student.prefs
                assert project.name in messages


@STUDENT_ALLOCATION
def test_inputs_supervisor_prefs_all_nonempty(
    student_names, project_names, supervisor_names, capacities, seed
):
    """ Test that each supervisor has a non-empty preference list. If not, check
    that a warning is caught and the supervisor, along with its projects, have
    been removed from the game. """

    _, _, _, game = make_game(
        student_names, project_names, supervisor_names, capacities, seed
    )

    with warnings.catch_warnings(record=True) as w:
        game._check_supervisor_prefs_all_nonempty()

        assert not w
        assert game.supervisors == game._all_supervisors

    supervisor = game.supervisors[0]
    supervisor.prefs = []
    with warnings.catch_warnings(record=True) as ws:
        game._check_supervisor_prefs_all_nonempty()

        w, *ws = ws
        message = w.message
        assert isinstance(message, PlayerExcludedWarning)
        assert supervisor.name in str(message)
        assert supervisor not in game.supervisors

        messages = " ".join((str(w.message) for w in ws))
        for project in supervisor.projects:
            assert project not in game.projects
            assert project.name in messages


@STUDENT_ALLOCATION
def test_inputs_project_capacities_positive(
    student_names, project_names, supervisor_names, capacities, seed
):
    """ Test that each project has a positive capacity. If not, check that the
    correct warnings are caught and that they are removed. """

    _, _, _, game = make_game(
        student_names, project_names, supervisor_names, capacities, seed
    )

    with warnings.catch_warnings(record=True) as w:
        game._check_init_project_capacities_positive()

        assert not w
        assert game.projects == game._all_projects

    project = game.projects[0]
    project.capacity = 0
    with warnings.catch_warnings(record=True) as w:
        game._check_init_project_capacities_positive()

        message = w[-1].message
        assert isinstance(message, PlayerExcludedWarning)
        assert project.name in str(message)
        assert project not in game.projects


@STUDENT_ALLOCATION
def test_inputs_supervisor_capacities_positive(
    student_names, project_names, supervisor_names, capacities, seed
):
    """ Test that each supervisor has a positive capacity. If not, check that a
    warning is caught and that they are removed. """

    _, _, _, game = make_game(
        student_names, project_names, supervisor_names, capacities, seed
    )

    with warnings.catch_warnings(record=True) as w:
        game._check_init_supervisor_capacities_positive()

        assert not w
        assert game.supervisors == game._all_supervisors

    supervisor = game.supervisors[0]
    supervisor.capacity = 0
    with warnings.catch_warnings(record=True) as ws:

        game._check_init_supervisor_capacities_positive()

        w, *ws = ws
        message = w.message
        assert isinstance(message, PlayerExcludedWarning)
        assert supervisor.name in str(message)
        assert supervisor not in game.supervisors

        messages = " ".join((str(w.message) for w in ws))
        for project in supervisor.projects:
            assert project not in game.projects
            assert project.name in messages


@STUDENT_ALLOCATION
def test_inputs_supervisor_capacities_sufficient(
    student_names, project_names, supervisor_names, capacities, seed
):
    """ Test that each project has a capacity no larger than its supervisor. If
    not, check that a warning is caught and that their capacity is updated to
    their supervisor's. """

    _, _, _, game = make_game(
        student_names, project_names, supervisor_names, capacities, seed
    )

    with warnings.catch_warnings(record=True) as w:
        game._check_init_supervisor_capacities_sufficient()

        assert not w
        assert game.projects == game._all_projects

    project = game.projects[0]
    supervisor_capacity = project.supervisor.capacity
    project.capacity = supervisor_capacity + 1
    with warnings.catch_warnings(record=True) as w:
        game._check_init_supervisor_capacities_sufficient()

        message = w[-1].message
        assert isinstance(message, InvalidCapacityWarning)
        assert project.name in str(message)
        assert str(supervisor_capacity) in str(message)
        assert project.capacity == supervisor_capacity


@STUDENT_ALLOCATION
def test_inputs_supervisor_capacities_necessary(
    student_names, project_names, supervisor_names, capacities, seed
):
    """ Test that each project does not have a higher capacity than the sum of
    its projects. If not, check that a warning is caught and that their capacity
    is updated to the sum of its projects. """

    _, _, _, game = make_game(
        student_names, project_names, supervisor_names, capacities, seed
    )

    with warnings.catch_warnings(record=True) as w:
        game._check_init_supervisor_capacities_necessary()

        assert not w
        assert game.supervisors == game._all_supervisors

    supervisor = game.supervisors[0]
    total_project_capacity = sum(p.capacity for p in supervisor.projects)
    supervisor.capacity = total_project_capacity + 1
    with warnings.catch_warnings(record=True) as w:
        game._check_init_supervisor_capacities_necessary()

        message = w[-1].message
        assert isinstance(message, InvalidCapacityWarning)
        assert supervisor.name in str(message)
        assert str(total_project_capacity) in str(message)
        assert supervisor.capacity == total_project_capacity


@STUDENT_ALLOCATION
def test_solve(
    student_names, project_names, supervisor_names, capacities, seed
):
    """ Test that StudentAllocation can solve games correctly when passed a set
    of players. """

    for optimal in ["student", "supervisor"]:
        students, projects, _, game = make_game(
            student_names, project_names, supervisor_names, capacities, seed
        )

        matching = game.solve(optimal)
        assert isinstance(matching, Matching)

        projects = sorted(projects, key=lambda p: p.name)
        matching_keys = sorted(matching.keys(), key=lambda k: k.name)
        for game_project, project in zip(matching_keys, projects):
            assert game_project.name == project.name
            assert game_project.pref_names == project.pref_names
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
    student_names, project_names, supervisor_names, capacities, seed
):
    """ Test that StudentAllocation finds a valid matching when the game is
    solved. """

    _, _, _, game = make_game(
        student_names, project_names, supervisor_names, capacities, seed
    )

    game.solve()
    assert game.check_validity()


@STUDENT_ALLOCATION
def test_check_student_matching(
    student_names, project_names, supervisor_names, capacities, seed
):
    """ Test that StudentAllocation recognises a valid matching requires a
    student to have a preference of their match, if they have one. """

    _, _, _, game = make_game(
        student_names, project_names, supervisor_names, capacities, seed
    )

    game.solve()
    assert game._check_student_matching()

    student = game.students[0]
    student.matching = Project(name="foo", capacity=0)
    with pytest.raises(Exception):
        game._check_student_matching()


@STUDENT_ALLOCATION
def test_check_project_matching(
    student_names, project_names, supervisor_names, capacities, seed
):
    """ Test that StudentAllocation recognises a valid matching requires a
    project to have a preference of each of their matches, if they have any. """

    _, _, _, game = make_game(
        student_names, project_names, supervisor_names, capacities, seed
    )

    game.solve()
    assert game._check_project_matching()

    project = game.projects[0]
    project.matching.append(Student(name="foo"))
    with pytest.raises(Exception):
        game._check_project_matching()


@STUDENT_ALLOCATION
def test_check_supervisor_matching(
    student_names, project_names, supervisor_names, capacities, seed
):
    """ Test that StudentAllocation recognises a valid matching requires each
    supervisor to have a preference of each of their matches, if they have
    any. """

    _, _, _, game = make_game(
        student_names, project_names, supervisor_names, capacities, seed
    )

    game.solve()
    assert game._check_supervisor_matching()

    supervisor = game.supervisors[0]
    supervisor.matching.append(Student(name="foo"))
    with pytest.raises(Exception):
        game._check_supervisor_matching()


@STUDENT_ALLOCATION
def test_check_project_capacity(
    student_names, project_names, supervisor_names, capacities, seed
):
    """ Test that StudentAllocation recognises a valid matching requires all
    projects to not be over-subscribed. """

    _, _, _, game = make_game(
        student_names, project_names, supervisor_names, capacities, seed
    )

    game.solve()
    assert game._check_project_capacity()

    project = game.projects[0]
    project.matching = range(project.capacity + 1)
    with pytest.raises(Exception):
        game._check_project_capacity()


@STUDENT_ALLOCATION
def test_check_supervisor_capacity(
    student_names, project_names, supervisor_names, capacities, seed
):
    """ Test that StudentAllocation recognises a valid matching requires all
    supervisors to not be over-subscribed. """

    _, _, _, game = make_game(
        student_names, project_names, supervisor_names, capacities, seed
    )

    game.solve()
    assert game._check_supervisor_capacity()

    supervisor = game.supervisors[0]
    supervisor.matching = range(supervisor.capacity + 1)
    with pytest.raises(Exception):
        game._check_supervisor_capacity()


def test_check_stability():
    """ Test that StudentAllocation can recognise whether a matching is stable
    or not. """

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
