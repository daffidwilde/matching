"""Classes for handling multiple match matchings."""

from matching.base import BaseMatching
from matching.players import Player


class MultipleMatching(BaseMatching):
    """Matching class for games with multiple matches like HR or SA.

    Parameters
    ----------
    dictionary
        A dictionary comprised of ``Hospital, List[Player]`` pairs.
    """

    def __init__(self, dictionary):
        super().__init__(dictionary)

    def __setitem__(self, player, new):
        """Set a player's match and match each of them to the player.

        First check if the player is present, and that the new match is
        a valid collection of players.
        """

        self._check_player_in_keys(player)
        self._check_new_valid_type(new, (list, tuple))
        for other in new:
            self._check_new_valid_type(other, Player)

        player.matching = new
        for other in new:
            other.matching = player

        self._data[player] = new
