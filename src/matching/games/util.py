""" Useful functions for the running of the various core algorithms. """


def delete_pair(player, successor):
    """Make a player forget one its "successors", effectively deleting the pair
    from further further consideration in the game."""

    player._forget(successor)
    successor._forget(player)


def match_pair(suitor, reviewer):
    """ Match the players given by `suitor` and `reviewer`. """

    suitor._match(reviewer)
    reviewer._match(suitor)
