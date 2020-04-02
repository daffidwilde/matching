""" Integration and unit tests for the SR algorithm. """

from matching.games.stable_roommates import (
    first_phase,
    locate_all_or_nothing_cycle,
    second_phase,
    stable_roommates,
)

from .params import STABLE_ROOMMATES, make_players


@STABLE_ROOMMATES
def test_first_phase(player_names, seed):
    """ Verify that the first phase of the algorithm produces a valid set of
    reduced preference players. """

    players = make_players(player_names, seed)
    players = first_phase(players)

    for player in players:
        assert player.matching is None
        assert {p.name for p in player.prefs}.issubset(player.pref_names)


@STABLE_ROOMMATES
def test_locate_all_or_nothing_cycle(player_names, seed):
    """ Verify that a cycle of (least-preferred, second-choice) players can be
    identified from a set of players. """

    players = make_players(player_names, seed)
    player = players[-1]
    cycle = locate_all_or_nothing_cycle(player)

    for last, second in cycle:
        assert second.prefs.index(last) == len(second.prefs) - 1


@STABLE_ROOMMATES
def test_second_phase(player_names, seed):
    """ Verify that the second phase of the algorithm produces a valid set of
    players with appropriate matches. """

    players = make_players(player_names, seed)
    try:
        players = second_phase(players)

        for player in players:
            if player.prefs:
                assert player.prefs == [player.matching]
            else:
                assert player.matching is None
    except (IndexError, ValueError):
        pass


@STABLE_ROOMMATES
def test_stable_roommates(player_names, seed):
    """ Verify that the algorithm can terminate with a valid matching. """

    players = make_players(player_names, seed)
    matching = stable_roommates(players)

    for player, other in matching.items():
        if other is not None:
            assert player.prefs == [other]
            assert other.matching == player
