""" Functions for the SR algorithm. """

from .util import _delete_pair


def first_phase(players):
    """Conduct the first phase of the algorithm where one-way proposals are
    made, and unpreferable pairs are forgotten."""

    free_players = players[:]
    while free_players:

        player = free_players.pop()
        favourite = player.get_favourite()

        current = favourite.matching
        if current is not None:
            favourite._unmatch()
            free_players.append(current)

        favourite._match(player)

        for successor in favourite.get_successors():
            _delete_pair(successor, favourite)
            if not successor.prefs and successor in free_players:
                free_players.remove(successor)

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
    cycle = list(zip(lasts[idx + 1 :], seconds[idx:]))

    return cycle


def get_pairs_to_delete(cycle):
    """Based on an all-or-nothing cycle :math:`(x_1, y_1), \\ldots, (x_n, y_n)`,
    for each :math:`i = 1, \\ldots, n`, delete from the game all pairs
    :math:`(y_i, z)` such that :math:`y_i` prefers :math:`x_{i-1}` to :math:`z`
    where subscripts are taken modulo :math:`n`.

    This is an important point that is omitted from the original paper, but may
    be found in:

        Gusfield and Irving. 'The Stable Marriage Problem: Structure and
        Algorithms'. Foundations of Computing, MIT Press (1989).

    The essential difference between the two statements of this algorithm is the
    removal of pairs identified by each all-or-nothing cycle, in addition to
    those contained in the cycle. Without doing so, tails of cycles can be
    removed rather than whole cycles, leaving some conflicting pairs in the
    game."""

    pairs = []
    for i, (_, right) in enumerate(cycle):

        left = cycle[(i - 1) % len(cycle)][0]
        successors = right.prefs[right.prefs.index(left) + 1 :]
        for successor in successors:
            if (right, successor) not in pairs and (
                successor,
                right,
            ) not in pairs:
                pairs.append((right, successor))

    return pairs


def second_phase(players):
    """Conduct the second phase of the algorithm where all-or-nothing cycles
    (rotations) are located and removed from the game."""

    player = next(p for p in players if len(p.prefs) > 1)
    while True:

        cycle = locate_all_or_nothing_cycle(player)
        pairs = get_pairs_to_delete(cycle)
        for player, other in pairs:
            _delete_pair(player, other)

        if any(p.prefs == [] for p in players):
            break

        try:
            player = next(p for p in players if len(p.prefs) > 1)
        except StopIteration:
            break

    for player in players:
        player._unmatch()
        if player.prefs:
            player._match(player.get_favourite())

    return players


def _second_phase(players):
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
