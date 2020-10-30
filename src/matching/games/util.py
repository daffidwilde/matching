""" Useful functions for the running of the various core algorithms. """


def _delete_pair(player, other):
    """Make a player forget another (and vice versa), deleting the pair from
    further consideration in the game."""

    player._forget(other)
    other._forget(player)


def _match_pair(player, other):
    """Match the players given by `player` and `other`."""

    player._match(other)
    other._match(player)
