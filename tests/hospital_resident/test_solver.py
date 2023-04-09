"""Unit tests for the HR solver."""

import warnings

import pytest
from hypothesis import given
from hypothesis.strategies import booleans, sampled_from

from matching import MultipleMatching
from matching import Player as Resident
from matching.exceptions import (
    MatchingError,
    PlayerExcludedWarning,
    PreferencesChangedWarning,
)
from matching.games import HospitalResident
from matching.players import Hospital

from .util import connections, games, players


@given(players=players(), clean=booleans())
def test_init(players, clean):
    """Test for correct instantiation given a set of players."""

    residents, hospitals = players

    game = HospitalResident(residents, hospitals, clean)

    for resident, game_resident in zip(residents, game.residents):
        assert resident.name == game_resident.name
        assert resident._pref_names == game_resident._pref_names

    for hospital, game_hospital in zip(hospitals, game.hospitals):
        assert hospital.name == game_hospital.name
        assert hospital._pref_names == game_hospital._pref_names
        assert hospital.capacity == game_hospital.capacity

    assert all([resident.matching is None for resident in game.residents])
    assert all([hospital.matching == [] for hospital in game.hospitals])
    assert game.matching is None


@given(connections=connections(), clean=booleans())
def test_create_from_dictionaries(connections, clean):
    """Test for correct instantiation given a set of dictionaries."""

    resident_prefs, hospital_prefs, capacities = connections

    game = HospitalResident.create_from_dictionaries(
        resident_prefs, hospital_prefs, capacities, clean
    )

    for resident in game.residents:
        assert resident._pref_names == resident_prefs[resident.name]
        assert resident.matching is None

    for hospital in game.hospitals:
        assert hospital._pref_names == hospital_prefs[hospital.name]
        assert hospital.capacity == capacities[hospital.name]
        assert hospital.matching == []

    assert game.matching is None
    assert game.clean is clean


@given(game=games())
def test_check_inputs(game):
    """Test that inputs to an instance of HR can be verified."""

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        game.check_inputs()

    assert game.residents == game._all_residents
    assert game.hospitals == game._all_hospitals


@given(game=games())
def test_check_inputs_resident_prefs_all_hospitals(game):
    """Test each resident has only hospitals in its preference list.

    If not, check that a warning is caught and the resident's
    preferences are changed.
    """

    resident = game.residents[0]
    resident.prefs = [Resident("foo")]

    with pytest.warns(PreferencesChangedWarning) as record:
        game._check_inputs_player_prefs_all_in_party("residents", "hospitals")

    assert len(record) == 1

    message = str(record[0].message)

    assert resident.name in message
    assert "foo" in message

    if game.clean:
        assert resident.prefs == []


@given(game=games())
def test_check_inputs_hospital_prefs_all_residents(game):
    """Test each hospital has only residents in its preference list.

    If not, check that a warning is caught and the hospitals's
    preferences are changed.
    """

    hospital = game.hospitals[0]
    hospital.prefs = [Resident("foo")]

    with pytest.warns(PreferencesChangedWarning) as record:
        game._check_inputs_player_prefs_all_in_party("hospitals", "residents")

    assert len(record) == 1

    message = str(record[0].message)

    assert hospital.name in message
    assert "foo" in message

    if game.clean:
        assert hospital.prefs == []


@given(game=games())
def test_check_inputs_hospital_prefs_all_reciprocated(game):
    """Test each hospital has ranked only residents that have ranked it.

    If not, check that a warning is caught and the hospital has
    forgotten any such residents.
    """

    hospital = game.hospitals[0]
    resident = hospital.prefs[0]
    resident._forget(hospital)

    with pytest.warns(PreferencesChangedWarning) as record:
        game._check_inputs_player_prefs_all_reciprocated("hospitals")

    assert len(record) == 1

    message = str(record[0].message)

    assert hospital.name in message
    assert resident.name in message

    if game.clean:
        assert resident not in hospital.prefs


@given(game=games())
def test_check_inputs_hospital_reciprocated_all_prefs(game):
    """Test each hospital has ranked all residents that have ranked it.

    If not, check that a warning is caught and any such resident has
    forgotten the hospital.
    """

    hospital = game.hospitals[0]
    resident = hospital.prefs[0]
    hospital._forget(resident)

    with pytest.warns(PreferencesChangedWarning) as record:
        game._check_inputs_player_reciprocated_all_prefs(
            "hospitals", "residents"
        )

    assert len(record) == 1

    message = str(record[0].message)

    assert hospital.name in message
    assert resident.name in message

    if game.clean:
        assert hospital not in resident.prefs


@given(game=games())
def test_check_inputs_resident_prefs_all_nonempty(game):
    """Test that each resident has a non-empty preference list.

    If not, check that a warning is caught and the resident has been
    removed from the game.
    """

    resident = game.residents[0]
    resident.prefs = []

    with pytest.warns(PlayerExcludedWarning) as record:
        game._check_inputs_player_prefs_nonempty("residents", "hospitals")

    assert len(record) == 1
    assert resident.name in str(record[0].message)

    if game.clean:
        assert resident not in game.residents


@given(game=games())
def test_check_inputs_hospital_prefs_all_nonempty(game):
    """Test that each hospital has a non-empty preference list.

    If not, check that a warning is caught and the player has been
    removed from the game.
    """

    hospital = game.hospitals[0]
    hospital.prefs = []

    with pytest.warns(PlayerExcludedWarning) as record:
        game._check_inputs_player_prefs_nonempty("hospitals", "residents")

    assert len(record) == 1
    assert hospital.name in str(record[0].message)

    if game.clean:
        assert hospital not in game.hospitals


@given(game=games())
def test_check_inputs_hospital_capacity(game):
    """Test each hospital has a positive integer capacity.

    If not, raise an Exception detailing the hospital.
    """

    hospital = game.hospitals[0]
    capacity = hospital.capacity
    hospital.capacity = 0

    assert hospital._original_capacity == capacity

    with pytest.warns(PlayerExcludedWarning) as record:
        game._check_inputs_player_capacity("hospitals", "residents")

    assert len(record) == 1
    assert hospital.name in str(record[0].message)

    if game.clean:
        assert hospital not in game.hospitals


@given(game=games(), optimal=sampled_from(["resident", "hospital"]))
def test_solve(game, optimal):
    """Test for the correct solving of games."""

    matching = game.solve(optimal)
    assert isinstance(matching, MultipleMatching)

    hospitals = sorted(game.hospitals, key=lambda h: h.name)
    matching_keys = sorted(matching.keys(), key=lambda k: k.name)
    for game_hospital, hospital in zip(matching_keys, hospitals):
        assert game_hospital.name == hospital.name
        assert game_hospital._pref_names == hospital._pref_names
        assert game_hospital.capacity == hospital.capacity

    matched_residents = [
        resident for match in matching.values() for resident in match
    ]

    assert matched_residents != [] and set(matched_residents).issubset(
        set(game.residents)
    )

    for resident in set(game.residents) - set(matched_residents):
        assert resident.matching is None


@given(game=games())
def test_check_validity(game):
    """Test for a valid matching when the game is solved."""

    game.solve()
    assert game.check_validity()


@given(game=games())
def test_check_for_unacceptable_matches_residents(game):
    """Test that matched residents have a preference of their match."""

    resident = game.residents[0]
    hospital = Hospital(name="foo", capacity=1)
    resident.matching = hospital

    issues = game._check_for_unacceptable_matches("residents")
    assert len(issues) == 1

    issue = issues[0]
    assert issue.startswith(resident.name)
    assert issue.endswith(f"{resident.prefs}.")
    assert hospital.name in issue

    with pytest.raises(MatchingError) as e:
        game.check_validity()
        error = e.unacceptable_matches[0]
        assert issue == error


@given(game=games())
def test_check_for_unacceptable_matches_hospitals(game):
    """Test that each hospital has a preference of all its matches."""

    hospital = game.hospitals[0]
    resident = Resident(name="foo")
    hospital.matching.append(resident)

    issues = game._check_for_unacceptable_matches("hospitals")
    assert len(issues) == 1

    issue = issues[0]
    assert issue.startswith(hospital.name)
    assert issue.endswith(f"{hospital.prefs}.")
    assert resident.name in issue

    with pytest.raises(MatchingError) as e:
        game.check_validity()
        error = e.unacceptable_matches[0]
        assert issue == error


@given(game=games())
def test_check_for_oversubscribed_hospitals(game):
    """Test that no hospitals can be oversubscribed."""

    hospital = game.hospitals[0]
    hospital.matching = range(hospital.capacity + 1)

    issues = game._check_for_oversubscribed_players("hospitals")
    assert len(issues) == 1

    issue = issues[0]
    assert issue.startswith(hospital.name)
    assert issue.endswith(f"{hospital.capacity}.")
    assert str(hospital.matching) in issue

    with pytest.raises(MatchingError) as e:
        game.check_validity()
        error = e.oversubscribed_hospitals[0]
        assert issue == error


def test_check_stability():
    """Test checker for whether matching is stable or not."""

    residents = [Resident("A"), Resident("B"), Resident("C")]
    hospitals = [Hospital("X", 2), Hospital("Y", 2)]

    (a, b, c), (x, y) = residents, hospitals

    a.set_prefs([x, y])
    b.set_prefs([y])
    c.set_prefs([y, x])

    x.set_prefs([c, a])
    y.set_prefs([a, b, c])

    game = HospitalResident(residents, hospitals)

    matching = game.solve()
    assert game.check_stability()

    (a, b, c), (x, y) = game.residents, game.hospitals
    matching[x] = [c]
    matching[y] = [a, b]

    assert not game.check_stability()
