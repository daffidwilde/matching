""" The SR solver and algorithm. """

import copy

from matching import BaseGame, Matching, Player

from .util import delete_pair, match_pair


class StableRoommates(BaseGame):
    """ A class for solving instances of the stable roommates problem (SR).

    Parameters
    ----------
    players : list of Player
        The players in the game. Each must rank all other players.

    Attributes
    ----------
    matching : Matching or None
        Once the game is solved, a matching is available. This uses the players
        as keys and values in a ``Matching`` object. Initialises as ``None``.
    """

    def __init__(self, players):

        players = copy.deepcopy(players)
        self.players = players

        super().__init__()
        self._check_inputs()

    @classmethod
    def create_from_dictionary(cls, player_prefs):
        """ Create an instance of SR from a preference dictionary. """

        players = _make_players(player_prefs)
        game = cls(players)

        return game

    def solve(self):
        """ Solve the instance of SR using Irving's algorithm. Return the
        matching. """

        self.matching = Matching(stable_roommates(self.players))
        return self.matching

    def check_stability(self):
        """ Check for the existence of any blocking pairs in the current
        matching. Then the stability of the matching holds when there are no
        blocking pairs and all players have been matched. """

        if None in self.matching.values():
            return False

        blocking_pairs = []
        for player in self.players:
            others = [p for p in self.players if p != player]
            for other in others:
                if (other, player) not in blocking_pairs:
                    both_matched = player.matching and other.matching
                    prefer_each_other = player.prefers(
                        other, player.matching
                    ) and other.prefers(player, other.matching)
                    if both_matched and prefer_each_other:
                        blocking_pairs.append((player, other))

        self.blocking_pairs = blocking_pairs
        return not any(blocking_pairs)

    def check_validity(self):
        """ Check whether the current matching is valid. """

        errors = []
        matching = self.matching
        for player in self.players:
            if player.matching is None:
                errors.append(ValueError(f"{player} is unmatched."))
        if errors:
            raise Exception(*errors)

        return True

    def _check_inputs(self):
        """ Check that all players have ranked all other players. """

        for player in self.players:
            others = {p for p in self.players if p != player}
            if set(player.prefs) != others:
                raise ValueError(
                    "Every player must rank all other players. "
                    f"{player}: {player.prefs} not permutation of {others}"
                )

        return True


def forget_pair(player, other):
    """ Remove a (player, other) pair from the game. """

    player.forget(other)
    other.forget(player)


def forget_successors(players):
    """ Make each player forget those players that they like less than their
    current proposal. """

    for player in players:
        if player.matching:
            successors = player.get_successors()
            player.unmatch()
            for successor in successors:
                forget_pair(player, successor)

    return players


def first_phase(players):
    """ Conduct the first phase of the algorithm where one-way proposals are
    made, and unpreferable pairs are forgotten. This phase terminates when
    either all players have been proposed to, or if one player has been rejected
    by everyone leaving their preference list empty. """

    proposed_to = set()
    for player in players:
        proposer = player
        while True:
            fave = proposer.get_favourite()
            if not fave.matching:
                fave.match(proposer)
            else:
                current = fave.matching
                if fave.prefers(proposer, current):
                    fave.match(proposer)
                    forget_pair(fave, current)

                    proposer = current
                else:
                    forget_pair(fave, proposer)

            if fave not in proposed_to or not proposer.prefs:
                break

        proposed_to.add(fave)

    players = forget_successors(players)
    return players


def locate_all_or_nothing_cycle(player):
    """ Locate a cycle of (least-preferable, second-choice) pairs to be removed
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
    """ Conduct the second phase of the algorithm where all or nothing cycles
    (rotations) are located and removed from the game. These reduced preference
    lists form a matching. """

    player_with_second_preference = next(p for p in players if len(p.prefs) > 1)
    while True:
        cycle = locate_all_or_nothing_cycle(player_with_second_preference)
        for player, other in cycle:
            player.forget(other)
            other.forget(player)

        try:
            player_with_second_preference = next(
                p for p in players if len(p.prefs) > 1
            )
        except StopIteration:
            break

    for player in players:
        if player.prefs:
            player.match(player.get_favourite())

    return players


def stable_roommates(players):
    """ Irving's algorithm :cite:`Irv85` that finds stable solutions to
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


def _make_players(player_prefs):
    """ Make a set of ``Player`` instances from the dictionary given. Add their
    preferences. """

    player_dict = {}
    for player_name in player_prefs:
        player = Player(name=player_name)
        player_dict[player_name] = player

    for player_name, player in player_dict.items():
        prefs = [player_dict[name] for name in player_prefs[player_name]]
        player.set_prefs(prefs)

    players = list(player_dict.values())

    return players
