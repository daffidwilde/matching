""" Useful functions for the running of the various core algorithms. """


def unmatch_pair(suitor, reviewer):
    """ Unmatch the players given by `suitor` and `reviewer`. """

    suitor.match = None

    if isinstance(reviewer.match, list):
        reviewer.match.remove(suitor)
    else:
        reviewer.match = None


def match_pair(suitor, reviewer):
    """ Match the players given by `suitor` and `reviewer`. """

    suitor.match = reviewer

    if isinstance(reviewer.match, list):
        reviewer.match.append(suitor)
    else:
        reviewer.match = suitor


def delete_pair(player, successor):
    """ Make a player forget one its "successors", effectively deleting the pair
    from further further consideration in the game. """

    player.forget(successor)
    successor.forget(player)
