""" The SR game class and supporting functions. """

import copy

from matching import BaseGame, Matching, Player
from matching.algorithms import stable_roommates
from matching.exceptions import MatchingError


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
        self.check_inputs()

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

    def check_validity(self):
        """ Check whether the current matching is valid. Raise `MatchingError`
        detailing the issues if not. """

        issues = []
        for player in self.players:
            issue = player.check_if_match_is_unacceptable(unmatched_okay=False)
            if issue:
                issues.append(issue)

        if issues:
            raise MatchingError(unmatched_players=issues)

        return True

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

    def check_inputs(self):
        """ Check that all players have ranked all other players. """

        for player in self.players:
            others = {p for p in self.players if p != player}
            if set(player.prefs) != others:
                raise ValueError(
                    "Every player must rank all other players. "
                    f"{player}: {player.prefs} is not a permutation of {others}"
                )

        return True


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
