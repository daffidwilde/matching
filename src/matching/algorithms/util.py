""" Useful functions for the running of the various core algorithms. """


def unmatch_pair(suitor, reviewer):
    """ Unmatch the players given by `suitor` and `reviewer`. """

    suitor.match = None

    try:
        reviewer.match.remove(suitor)
    except AttributeError:
        reviewer.match = None


def match_pair(suitor, reviewer):
    """ Match the players given by `suitor` and `reviewer`. """

    suitor.match = reviewer

    try:
        reviewer.match.append(suitor)
    except AttributeError:
        reviewer.match = suitor


def delete_pair(successor, reviewer):
    """ Make the players `successor` and `reviewer` forget one another,
    effectively 'deleting' the pair from the game. """

    successor.forget(reviewer)
    reviewer.forget(successor)
