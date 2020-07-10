""" Unit tests for the HR solver. """
import warnings

import pytest

from matching import Matching
from matching import Player as Resident
from matching.exceptions import MatchingError, PlayerExcludedWarning, PreferencesChangedWarning
from matching.games import HospitalResident
from matching.players import Hospital

from .params import HOSPITAL_RESIDENT, make_game, make_prefs


@HOSPITAL_RESIDENT
def test_init(resident_names, hospital_names, capacities, seed):
    """ Test that an instance of HospitalResident is created correctly when
    passed a set of players. """

    residents, hospitals, game = make_game(
        resident_names, hospital_names, capacities, seed
    )

    for resident, game_resident in zip(residents, game.residents):
        assert resident.name == game_resident.name
        assert resident.pref_names == game_resident.pref_names

    for hospital, game_hospital in zip(hospitals, game.hospitals):
        assert hospital.name == game_hospital.name
        assert hospital.pref_names == game_hospital.pref_names
        assert hospital.capacity == game_hospital.capacity

    assert all([resident.matching is None for resident in game.residents])
    assert all([hospital.matching == [] for hospital in game.hospitals])
    assert game.matching is None


@HOSPITAL_RESIDENT
def test_create_from_dictionaries(
    resident_names, hospital_names, capacities, seed
):
    """ Test that HospitalResident is created correctly when passed a set of
    dictionaries for each party. """

    resident_prefs, hospital_prefs = make_prefs(
        resident_names, hospital_names, seed
    )

    capacities_ = dict(zip(hospital_names, capacities))
    game = HospitalResident.create_from_dictionaries(
        resident_prefs, hospital_prefs, capacities_
    )

    for resident in game.residents:
        assert resident.pref_names == resident_prefs[resident.name]
        assert resident.matching is None

    for hospital in game.hospitals:
        assert hospital.pref_names == hospital_prefs[hospital.name]
        assert hospital.capacity == capacities_[hospital.name]
        assert hospital.matching == []

    assert game.matching is None


@HOSPITAL_RESIDENT
def test_inputs_resident_prefs_all_hospitals(
    resident_names, hospital_names, capacities, seed
):
    """ Test that every resident has only hospitals in its preference list. If
    not, check that a warning is caught and the player's preferences are
    changed. """

    _, _, game = make_game(resident_names, hospital_names, capacities, seed)

    with warnings.catch_warnings(record=True) as w:
        game._check_resident_prefs_all_hospitals()

        assert not w
        assert game.residents == game._all_residents

    resident = game.residents[0]
    resident.prefs = [Resident("foo")]
    with warnings.catch_warnings(record=True) as w:
        game._check_resident_prefs_all_hospitals()

        message = w[-1].message
        assert isinstance(message, PreferencesChangedWarning)
        assert resident.name in str(message)
        assert "foo" in str(message)
        assert resident.prefs == []


@HOSPITAL_RESIDENT
def test_inputs_resident_prefs_all_nonempty(
    resident_names, hospital_names, capacities, seed
):
    """ Test that every resident has a non-empty preference list. If not, check
    that a warning is caught and the player has been removed from the game. """

    _, _, game = make_game(resident_names, hospital_names, capacities, seed)

    with warnings.catch_warnings(record=True) as w:
        game._check_resident_prefs_all_nonempty()

        assert not w
        assert game.residents == game._all_residents

    resident = game.residents[0]
    resident.prefs = []
    with warnings.catch_warnings(record=True) as w:
        game._check_resident_prefs_all_nonempty()

        message = w[-1].message
        assert isinstance(message, PlayerExcludedWarning)
        assert resident.name in str(message)
        assert resident not in game.residents


@HOSPITAL_RESIDENT
def test_inputs_hospital_prefs_all_reciprocate(
    resident_names, hospital_names, capacities, seed
):
    """ Test that each hospital has ranked only those residents that have ranked
    it. If not, check that a warning is caught and the hospital has forgotten
    any such players. """

    _, _, game = make_game(resident_names, hospital_names, capacities, seed)

    with warnings.catch_warnings(record=True) as w:
        game._check_hospital_prefs_all_reciprocated()

        assert not w
        assert game.hospitals == game._all_hospitals

    hospital = game.hospitals[0]
    resident = hospital.prefs[0]
    resident.forget(hospital)
    with warnings.catch_warnings(record=True) as w:
        game._check_hospital_prefs_all_reciprocated()

        message = w[-1].message
        assert isinstance(message, PreferencesChangedWarning)
        assert hospital.name in str(message)
        assert resident.name in str(message)
        assert resident not in hospital.prefs


@HOSPITAL_RESIDENT
def test_inputs_hospital_reciprocates_all_prefs(
    resident_names, hospital_names, capacities, seed
):
    """ Test that each hospital has ranked all those residents that have ranked
    it. If not, check that a warning is caught and any such resident has
    forgotten the hospital. """

    _, _, game = make_game(resident_names, hospital_names, capacities, seed)

    with warnings.catch_warnings(record=True) as w:
        game._check_hospital_reciprocates_all_prefs()

        assert not w
        assert game.hospitals == game._all_hospitals

    hospital = game.hospitals[0]
    resident = hospital.prefs[0]
    hospital.forget(resident)
    with warnings.catch_warnings(record=True) as w:
        game._check_hospital_reciprocates_all_prefs()

        message = w[-1].message
        assert isinstance(message, PreferencesChangedWarning)
        assert hospital.name in str(message)
        assert resident.name in str(message)
        assert hospital not in resident.prefs


@HOSPITAL_RESIDENT
def test_inputs_hospital_prefs_all_nonempty(
    resident_names, hospital_names, capacities, seed
):
    """ Test that every hospital has a non-empty preference list. If not, check
    that a warning is caught and the player has been removed from the game. """

    _, _, game = make_game(resident_names, hospital_names, capacities, seed)

    with warnings.catch_warnings(record=True) as w:
        game._check_hospital_prefs_all_nonempty()

        assert not w
        assert game.hospitals == game._all_hospitals

    hospital = game.hospitals[0]
    hospital.prefs = []
    with warnings.catch_warnings(record=True) as w:
        game._check_hospital_prefs_all_nonempty()

        message = w[-1].message
        assert isinstance(message, PlayerExcludedWarning)
        assert hospital.name in str(message)
        assert hospital not in game.hospitals


@HOSPITAL_RESIDENT
def test_inputs_hospital_capacities(
    resident_names, hospital_names, capacities, seed
):
    """ Test that each hospital has enough space to accommodate their largest
    project, but does not offer a surplus of spaces from their projects.
    Otherwise, raise an Exception. """

    _, _, game = make_game(resident_names, hospital_names, capacities, seed)

    with warnings.catch_warnings(record=True) as w:
        game._check_init_hospital_capacities()

        assert not w
        assert game.hospitals == game._all_hospitals

    hospital = game.hospitals[0]
    capacity = hospital.capacity
    hospital.capacity = 0
    assert hospital._original_capacity == capacity
    with warnings.catch_warnings(record=True) as w:
        game._check_init_hospital_capacities()

        message = w[-1].message
        assert isinstance(message, PlayerExcludedWarning)
        assert hospital.name in str(message)
        assert hospital not in game.hospitals


@HOSPITAL_RESIDENT
def test_solve(resident_names, hospital_names, capacities, seed):
    """ Test that HospitalResident can solve games correctly when passed
    players. """

    for optimal in ["resident", "hospital"]:
        residents, hospitals, game = make_game(
            resident_names, hospital_names, capacities, seed
        )

        matching = game.solve(optimal)
        assert isinstance(matching, Matching)

        hospitals = sorted(hospitals, key=lambda h: h.name)
        matching_keys = sorted(matching.keys(), key=lambda k: k.name)
        for game_hospital, hospital in zip(matching_keys, hospitals):
            assert game_hospital.name == hospital.name
            assert game_hospital.pref_names == hospital.pref_names
            assert game_hospital.capacity == hospital.capacity

        matched_residents = [
            resident for match in matching.values() for resident in match
        ]

        assert matched_residents != [] and set(matched_residents).issubset(
            set(game.residents)
        )

        for resident in set(game.residents) - set(matched_residents):
            assert resident.matching is None


@HOSPITAL_RESIDENT
def test_check_validity(resident_names, hospital_names, capacities, seed):
    """ Test that HospitalResident finds a valid matching when the game is
    solved. """

    _, _, game = make_game(resident_names, hospital_names, capacities, seed)

    game.solve()
    assert game.check_validity()


@HOSPITAL_RESIDENT
def test_check_for_unacceptable_matches_residents(resident_names, hospital_names, capacities, seed):
    """ Test that HospitalResident recognises a valid matching requires each
    resident to have a preference of their match, if they have one. """

    _, _, game = make_game(resident_names, hospital_names, capacities, seed)
    game.solve()

    resident = game.residents[0]
    hospital = Hospital(name="foo", capacity="bar")
    resident.matching = hospital

    with pytest.raises(MatchingError) as e:
        game.check_validity()
        unacceptable_match = e.unacceptable_matches[0]
        assert unacceptable_match.startswith(resident.name)
        assert unacceptable_match.endswith(hospital.name)
        assert str(resident.prefs)


@HOSPITAL_RESIDENT
def test_check_for_unacceptable_matches_hospitals(resident_names, hospital_names, capacities, seed):
    """ Test that HospitalResident recognises a valid matching requires each
    hospital to have a preference of each of its matches, if any. """

    _, _, game = make_game(resident_names, hospital_names, capacities, seed)
    game.solve()

    hospital = game.hospitals[0]
    resident = Resident(name="foo")
    hospital.matching.append(resident)

    with pytest.raises(MatchingError) as e:
        game.check_validity()
        unacceptable_match = e.unacceptable_matches[0]
        assert unacceptable_match.startswith(hospital.name)
        assert unacceptable_match.endswith(resident.name)
        assert str(hospital.prefs) in unacceptable_match


@HOSPITAL_RESIDENT
def test_check_for_oversubscribed_hospitals(resident_names, hospital_names, capacities, seed):
    """ Test that HospitalResident recognises a valid matching requires all
    hospitals to not be oversubscribed. """

    _, _, game = make_game(resident_names, hospital_names, capacities, seed)
    game.solve()
    
    hospital = game.hospitals[0]
    hospital.matching = range(hospital.capacity + 1)

    with pytest.raises(MatchingError) as e:
        game.check_validity()
        oversubscribed_hospital = e.oversubscribed_hospitals[0]
        assert oversubscribed_hospital.startswith(hospital.name)
        assert oversubscribed_hospital.endswith(str(hospital.capacity))
        assert str(hospital.matching) in oversubscribed_hospital


def test_check_stability():
    """ Test that HospitalResident can recognise whether a matching is stable or
    not. """

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
