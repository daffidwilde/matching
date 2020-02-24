""" Hypothesis decorators for SR tests. """

import numpy as np
from hypothesis import given
from hypothesis.strategies import composite, integers, lists, sampled_from

from matching import Player


def make_players(player_names, seed):
    """ Given some names, make a valid set of players. """

    np.random.seed(seed)
    players = [Player(name) for name in player_names]

    for player in players:
        player.set_prefs(
            np.random.permutation([p for p in players if p != player]).tolist()
        )

    return players


def make_prefs(player_names, seed):
    """ Given some names, make a valid set of preferences for the players. """

    np.random.seed(seed)
    player_prefs = {
        name: np.random.permutation(
            [p for p in player_names if p != name]
        ).tolist()
        for name in player_names
    }

    return player_prefs


PLAYER_NAMES = lists(
    sampled_from(["A", "B", "C", "D"]), min_size=4, max_size=4, unique=True
)

STABLE_ROOMMATES = given(
    player_names=PLAYER_NAMES, seed=integers(min_value=0, max_value=2 ** 32 - 1)
)
