""" Unit tests for the HR solver. """
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
    """Test that an instance of HospitalResident is created correctly when
    passed a set of players."""

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
    """Test that HospitalResident is created correctly when passed a set of
    dictionaries for each party."""

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
    """ Test that inputs to an instance of HR can be verified. """

    with warnings.catch_warnings(record=True) as w:
        game.check_inputs()

        assert not w
        assert game.residents == game._all_residents
        assert game.hospitals == game._all_hospitals


@given(game=games())
def test_check_inputs_resident_prefs_all_hospitals(game):
    """Test that every resident has only hospitals in its preference list. If
    not, check that a warning is caught and the player's preferences are
    changed."""

    resident = game.residents[0]
    resident.prefs = [Resident("foo")]
    with warnings.catch_warnings(record=True) as w:
        game._check_inputs_player_prefs_all_in_party("residents", "hospitals")

        message = w[-1].message
        assert isinstance(message, PreferencesChangedWarning)
        assert resident.name in str(message)
        assert "foo" in str(message)
        if game.clean:
            assert resident.prefs == []


@given(game=games())
def test_check_inputs_hospital_prefs_all_residents(game):
    """Test that every hospital has only residents in its preference list. If
    not, check that a warning is caught and the player's preferences are
    changed."""

    hospital = game.hospitals[0]
    hospital.prefs = [Resident("foo")]
    with warnings.catch_warnings(record=True) as w:
        game._check_inputs_player_prefs_all_in_party("hospitals", "residents")

        message = w[-1].message
        assert isinstance(message, PreferencesChangedWarning)
        assert hospital.name in str(message)
        assert "foo" in str(message)
        if game.clean:
            assert hospital.prefs == []


@given(game=games())
def test_check_inputs_hospital_prefs_all_reciprocated(game):
    """Test that each hospital has ranked only those residents that have ranked
    it. If not, check that a warning is caught and the hospital has forgotten
    any such players."""

    hospital = game.hospitals[0]
    resident = hospital.prefs[0]
    resident.forget(hospital)
    with warnings.catch_warnings(record=True) as w:
        game._check_inputs_player_prefs_all_reciprocated("hospitals")

        message = w[-1].message
        assert isinstance(message, PreferencesChangedWarning)
        assert hospital.name in str(message)
        assert resident.name in str(message)
        if game.clean:
            assert resident not in hospital.prefs


@given(game=games())
def test_check_inputs_hospital_reciprocated_all_prefs(game):
    """Test that each hospital has ranked all those residents that have ranked
    it. If not, check that a warning is caught and any such resident has
    forgotten the hospital."""

    hospital = game.hospitals[0]
    resident = hospital.prefs[0]
    hospital.forget(resident)
    with warnings.catch_warnings(record=True) as w:
        game._check_inputs_player_reciprocated_all_prefs(
            "hospitals", "residents"
        )

        message = w[-1].message
        assert isinstance(message, PreferencesChangedWarning)
        assert hospital.name in str(message)
        assert resident.name in str(message)
        if game.clean:
            assert hospital not in resident.prefs


@given(game=games())
def test_check_inputs_resident_prefs_all_nonempty(game):
    """Test that every resident has a non-empty preference list. If not, check
    that a warning is caught and the player has been removed from the game."""

    resident = game.residents[0]
    resident.prefs = []
    with warnings.catch_warnings(record=True) as w:
        game._check_inputs_player_prefs_nonempty("residents", "hospitals")

        message = w[-1].message
        assert isinstance(message, PlayerExcludedWarning)
        assert resident.name in str(message)
        if game.clean:
            assert resident not in game.residents


@given(game=games())
def test_check_inputs_hospital_prefs_all_nonempty(game):
    """Test that every hospital has a non-empty preference list. If not, check
    that a warning is caught and the player has been removed from the game."""

    hospital = game.hospitals[0]
    hospital.prefs = []
    with warnings.catch_warnings(record=True) as w:
        game._check_inputs_player_prefs_nonempty("hospitals", "residents")

        message = w[-1].message
        assert isinstance(message, PlayerExcludedWarning)
        assert hospital.name in str(message)
        if game.clean:
            assert hospital not in game.hospitals


@given(game=games())
def test_check_inputs_hospital_capacity(game):
    """Test that each hospital has enough space to accommodate their largest
    project, but does not offer a surplus of spaces from their projects.
    Otherwise, raise an Exception."""

    hospital = game.hospitals[0]
    capacity = hospital.capacity
    hospital.capacity = 0
    assert hospital._original_capacity == capacity
    with warnings.catch_warnings(record=True) as w:
        game._check_inputs_player_capacity("hospitals", "residents")

        message = w[-1].message
        assert isinstance(message, PlayerExcludedWarning)
        assert hospital.name in str(message)
        if game.clean:
            assert hospital not in game.hospitals


@given(game=games(), optimal=sampled_from(["resident", "hospital"]))
def test_solve(game, optimal):
    """ Test that HospitalResident can solve games correctly. """

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
    """Test that HospitalResident finds a valid matching when the game is
    solved."""

    game.solve()
    assert game.check_validity()


@given(game=games())
def test_check_for_unacceptable_matches_residents(game):
    """Test that HospitalResident recognises a valid matching requires each
    resident to have a preference of their match, if they have one."""

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
    """Test that HospitalResident recognises a valid matching requires each
    hospital to have a preference of each of its matches, if any."""

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
    """Test that HospitalResident recognises a valid matching requires all
    hospitals to not be oversubscribed."""

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
    """Test that HospitalResident can recognise whether a matching is stable or
    not."""

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
