""" Functions for the SR algorithm. """

from .util import _delete_pair


def _forget_successors(players):
    """Make each player forget those players that they like less than their
    current proposal."""

    for player in players:
        if player.matching:
            successors = player.get_successors()
            for successor in successors:
                _delete_pair(player, successor)

    return players


def first_phase(players):
    """Conduct the first phase of the algorithm where one-way proposals are
    made, and unpreferable pairs are forgotten. This phase terminates when
    either all players have been proposed to, or if one player has been rejected
    by everyone leaving their preference list empty."""

    proposed_to = set()
    for player in players:
        proposer = player
        while True:
            fave = proposer.get_favourite()
            if not fave.matching:
                fave._match(proposer)
            else:
                current = fave.matching
                if fave.prefers(proposer, current):
                    fave._match(proposer)
                    _delete_pair(fave, current)

                    proposer = current
                else:
                    _delete_pair(fave, proposer)

            if fave not in proposed_to or not proposer.prefs:
                break

        proposed_to.add(fave)

    players = _forget_successors(players)
    return players


def locate_all_or_nothing_cycle(player):
    """Locate a cycle of (least-preferable, second-choice) pairs to be removed
    from the game."""

    lasts = [player]
    seconds = []
    while True:
        second_best = player.prefs[1]
        their_worst = second_best.prefs[-1]

        seconds.append(second_best)
        lasts.append(their_worst)

        player = their_worst

        if lasts.count(player) > 1:
            break

    idx = lasts.index(player)
    cycle = zip(lasts[idx + 1 :], seconds[idx:])

    return cycle


def second_phase(players):
    """Conduct the second phase of the algorithm where all or nothing cycles
    (rotations) are located and removed from the game. These reduced preference
    lists form a matching."""

    for player in players:
        player._unmatch()

    player_with_second_preference = next(p for p in players if len(p.prefs) > 1)
    while True:
        cycle = locate_all_or_nothing_cycle(player_with_second_preference)
        for player, other in cycle:
            player._forget(other)
            other._forget(player)

        try:
            player_with_second_preference = next(
                p for p in players if len(p.prefs) > 1
            )
        except StopIteration:
            break

    for player in players:
        if player.prefs:
            player._match(player.get_favourite())

    return players


def stable_roommates(players):
    """Irving's algorithm :cite:`Irv85` that finds stable solutions to
    instances of SR if one exists. Otherwise, an incomplete matching is found.

    Parameters
    ----------
    players : list of Player
        The players in the game. Each must rank all other players.

    Returns
    -------
    matching : dict
        A dictionary of matches where the keys and values are given by the
        members of ``players``.
    """

    players = first_phase(players)
    if any(len(p.prefs) > 1 for p in players):
        players = second_phase(players)

    return {player: player.matching for player in players}
