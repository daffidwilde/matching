"""Strategies for SR tests."""

from hypothesis.strategies import composite, integers, lists, permutations

from matching import Player
from matching.games import StableRoommates


@composite
def connections(draw, players_from=integers(), min_players=4, max_players=10):
    """A strategy for making a set of connections between players."""

    num_players = draw(integers(min_players, max_players))

    players = draw(
        lists(
            players_from,
            min_size=num_players,
            max_size=num_players,
            unique=True,
        )
    )

    preferences = {}
    for player in players:
        others = [p for p in players if p != player]
        prefs = draw(permutations(others))
        preferences[player] = prefs

    return preferences


@composite
def players(draw, **kwargs):
    """A strategy for making a set of players."""

    preferences = draw(connections(**kwargs))

    players_ = [Player(name) for name in preferences]
    for player in players_:
        names = preferences[player.name]
        prefs = []
        for name in names:
            for other in players_:
                if other.name == name:
                    prefs.append(other)
                    break

        player.set_prefs(prefs)

    return players_


@composite
def games(draw, **kwargs):
    """A strategy for making an instance of SR."""

    players_ = draw(players(**kwargs))
    return StableRoommates(players_)
