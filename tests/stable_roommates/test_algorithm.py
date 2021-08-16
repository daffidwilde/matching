""" Integration and unit tests for the SR algorithm. """
import warnings

from hypothesis import assume, given

from matching.algorithms.stable_roommates import (
    first_phase,
    get_pairs_to_delete,
    locate_all_or_nothing_cycle,
    second_phase,
    stable_roommates,
)
from matching.exceptions import NoStableMatchingWarning

from .util import players


@given(players=players())
def test_first_phase(players):
    """Verify that the first phase of the algorithm produces a valid set of
    reduced preference players."""

    players = first_phase(players)

    player_matched = {player: player.matching is not None for player in players}
    assert sum(player_matched.values()) >= len(players) - 1

    for player in players:
        if player.matching is None:
            assert player.prefs == []
        else:
            assert player.matching in player.prefs

        assert {p.name for p in player.prefs}.issubset(player._pref_names)


@given(players=players())
def test_locate_all_or_nothing_cycle(players):
    """Verify that a cycle of (least-preferred, second-choice) players can be
    identified from a set of players."""

    player = players[-1]
    cycle = locate_all_or_nothing_cycle(player)

    assert isinstance(cycle, list)
    for last, second in cycle:
        assert second.prefs.index(last) == len(second.prefs) - 1


@given(players=players())
def test_get_pairs_to_delete(players):
    """Verify that all necessary pairs are identified to remove a cycle from the
    game."""

    assert get_pairs_to_delete([]) == []

    players = first_phase(players)
    assume(any(len(p.prefs) > 1 for p in players))

    player = next(p for p in players if len(p.prefs) > 1)
    cycle = locate_all_or_nothing_cycle(player)

    pairs = get_pairs_to_delete(cycle)

    for pair in cycle:
        assert pair in pairs or pair[::-1] in pairs

    for i, (_, right) in enumerate(cycle):
        left = cycle[(i - 1) % len(cycle)][0]
        others = right.prefs[right.prefs.index(left) + 1 :]
        for other in others:
            assert (right, other) in pairs or (other, right) in pairs


@given(players=players())
def test_second_phase(players):
    """Verify that the second phase of the algorithm produces a valid set of
    players with appropriate matches."""

    players = first_phase(players)
    assume(any(len(p.prefs) > 1 for p in players))

    with warnings.catch_warnings(record=True) as w:
        players = second_phase(players)

    for player in players:
        if player.prefs:
            assert player.prefs[0] == player.matching
        else:
            message = w[-1].message

            assert isinstance(message, NoStableMatchingWarning)
            assert str(player.name) in str(message)
            assert player.matching is None


@given(players=players())
def test_stable_roommates(players):
    """Verify that the algorithm can terminate with a valid matching."""

    with warnings.catch_warnings(record=True) as w:
        matching = stable_roommates(players)

    assert isinstance(matching, dict)

    for player, match in matching.items():
        if match is None:
            message = w[-1].message
            assert str(player) in str(message)
            assert not player.prefs
        else:
            assert match == player.prefs[0]
