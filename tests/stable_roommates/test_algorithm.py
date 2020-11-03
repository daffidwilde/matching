""" Integration and unit tests for the SR algorithm. """
from hypothesis import assume

from matching.algorithms.stable_roommates import (
    first_phase,
    get_pairs_to_delete,
    locate_all_or_nothing_cycle,
    second_phase,
    stable_roommates,
)

from .params import STABLE_ROOMMATES, make_players


@STABLE_ROOMMATES
def test_first_phase(player_names, seed):
    """Verify that the first phase of the algorithm produces a valid set of
    reduced preference players."""

    players = make_players(player_names, seed)
    players = first_phase(players)

    for player in players:
        if player.matching is None:
            assert player.prefs == []
        else:
            assert player.matching in player.prefs

        assert {p.name for p in player.prefs}.issubset(player.pref_names)


@STABLE_ROOMMATES
def test_locate_all_or_nothing_cycle(player_names, seed):
    """Verify that a cycle of (least-preferred, second-choice) players can be
    identified from a set of players."""

    players = make_players(player_names, seed)
    player = players[-1]
    cycle = locate_all_or_nothing_cycle(player)

    assert isinstance(cycle, list)
    for last, second in cycle:
        assert second.prefs.index(last) == len(second.prefs) - 1

def status(players):
    for player in players:
        print(f"{player.name:>5}", f"{str(player.prefs):>30}", f"{str(player.matching):>5}")


@STABLE_ROOMMATES
def test_get_pairs_to_delete(player_names, seed):
    """Verify that all necessary pairs are identified to remove a cycle from the
    game."""

    assert get_pairs_to_delete([]) == []

    players = make_players(player_names, seed)

    players = first_phase(players)
    assume(any(len(p.prefs) > 1 for p in players))

    player = next(p for p in players if len(p.prefs) > 1)
    cycle = locate_all_or_nothing_cycle(player)

    pairs = get_pairs_to_delete(cycle)

    for pair in cycle:
        assert pair in pairs or pair[::-1] in pairs

    for i, (_, right) in enumerate(cycle):
        left = cycle[(i - 1) % len(cycle)][0]
        others = right.prefs[right.prefs.index(left) + 1:]
        for other in others:
            assert (right, other) in pairs or (other, right) in pairs


@STABLE_ROOMMATES
def test_second_phase(player_names, seed):
    """Verify that the second phase of the algorithm produces a valid set of
    players with appropriate matches."""

    players = make_players(player_names, seed)
    players = first_phase(players)
    assume(any(len(p.prefs) > 1 for p in players))

    players = second_phase(players)

    for player in players:
        if player.prefs:
            assert player.prefs == [player.matching]
        else:
            assert player.matching is None


@STABLE_ROOMMATES
def test_stable_roommates(player_names, seed):
    """ Verify that the algorithm can terminate with a valid matching. """

    players = make_players(player_names, seed)
    matching = stable_roommates(players)

    if None in matching.values():
        assert all(val is None for val in matching.values())

    else:
        for player, other in matching.items():
            assert player.prefs == [other]
            assert other.matching == player
