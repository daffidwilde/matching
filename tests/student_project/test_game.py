"""Unit tests for the StudentProject class."""

import warnings
from unittest import mock

import numpy as np
import pytest
from hypothesis import given

from matching.games.student_project import StudentProject

from ..common import mocked_game
from .util import st_ranks_capacities, st_preferences_capacities, st_utilities_capacities


def _check_game_attributes(game, stud_ranks, sup_ranks, affils, proj_caps, sup_caps):
    """Check the essential attributes of a game are set properly."""
    assert isinstance(game, StudentProject)
    assert (game.student_ranks == stud_ranks).all()
    assert (game.supervisor_ranks == sup_ranks).all()
    assert (game.project_supervisors == affils).all()
    assert (game.project_capacities == proj_caps).all()
    assert (game.supervisor_capacities == sup_caps).all()

    assert game.num_students == len(stud_ranks)
    assert game.num_projects == len(affils)
    assert game.num_supervisors == len(sup_ranks)
    assert game.matching is None


@given(st_ranks_capacities())
def test_init(params):
    """Check instantiation with ranks, affiliations and capacities."""
    game = mocked_game(StudentProject, *params)

    _check_game_attributes(game, *params)
    assert game._preference_lookup is None


@given(st_utilities_capacities())
def test_from_utilities(params):
    """Check instantiation from utility matrices."""
    *utilities, affiliations, project_caps, supervisor_caps = params
    student_utility, supervisor_utility = utilities

    with (
        mock.patch("matching.games.StudentProject.check_input_validity") as validator,
        mock.patch("matching.convert.utility_to_rank") as ranker,
    ):
        effects = (student_utility.argsort(), supervisor_utility.argsort())
        ranker.side_effect = list(effects)
        game = StudentProject.from_utilities(student_utility, supervisor_utility, affiliations, project_caps, supervisor_caps)

    _check_game_attributes(game, *effects, affiliations, project_caps, supervisor_caps)
    assert game._preference_lookup is None

    assert ranker.call_count == 2
    for call, utility in zip(ranker.call_args_list, utilities):
        arg, *_ = call.args
        assert np.array_equal(arg, utility)

    validator.assert_called_once_with()


@given(st_preferences_capacities())
def test_from_preferences(params):
    """Check instantiation from preference list dictionaries."""
    *preferences, affiliations, project_caps, supervisor_caps = params
    student_prefs, supervisor_prefs = preferences

    with (
        mock.patch("matching.games.StudentProject.check_input_validity") as validator,
        mock.patch("matching.convert.preference_to_rank") as ranker,
    ):
        effects = (
            np.array(list(student_prefs.values())),
            np.array(list(supervisor_prefs.values())),
        )
        ranker.side_effect = list(effects)
        game = StudentProject.from_preferences(
            student_prefs, supervisor_prefs, affiliations, project_caps, supervisor_caps
        )

    affiliation_array = [int(sup[1:]) for _, sup in affiliations.items()]
    _check_game_attributes(game, *effects, affiliation_array, list(project_caps.values()), list(supervisor_caps.values()))

    assert isinstance(game._preference_lookup, dict)
    assert game._preference_lookup == {
        "students": sorted(student_prefs),
        "projects": sorted(project_caps),
        "supervisors": sorted(supervisor_prefs),
    }

    _check_capacities(game.project_capacities, project_caps, len(affiliations), game._preference_lookup["projects"])
    _check_capacities(game.supervisor_capacities, supervisor_caps, len(supervisor_prefs), game._preference_lookup["supervisors"])

    assert ranker.call_count == 2
    for call, preference, others in zip(
        ranker.call_args_list,
        preferences,
        (supervisor_prefs, student_prefs),
    ):
        assert call.args == (preference, sorted(others))

    validator.assert_called_once_with()


def _check_capacities(capacity_array, capacity_dict, size, party_lookup):
    """Check the capacity array matches the input dictionary."""
    assert isinstance(capacity_array, np.ndarray)
    assert capacity_array.shape == (size,)
    for cap, player in zip(capacity_array, party_lookup):
        assert cap == capacity_dict.get(player)
