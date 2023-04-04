"""Useful functions for base class tests."""

from hypothesis.strategies import composite, integers, text

from matching import BasePlayer


@composite
def player_others(
    draw,
    player_name_from=text(),
    other_names_from=text(),
    min_size=1,
    max_size=10,
):
    """A custom strategy for creating a set of players.

    Returns a single player and the other players, all of whom are
    `BasePlayer` instances.
    """

    size = draw(integers(min_value=min_size, max_value=max_size))
    player = BasePlayer(draw(player_name_from))
    others = [BasePlayer(draw(other_names_from)) for _ in range(size)]

    return player, others
