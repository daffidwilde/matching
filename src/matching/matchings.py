"""A collection of dictionary-like objects for storing matchings."""

from matching import BaseMatching
from matching.players import Player


class SingleMatching(BaseMatching):
    """Matching class for games with singular matches like SM or SR.

    Parameters
    ----------
    dictionary
        A dictionary comprised of ``Player, Optional[Player]`` pairs.
    """

    def __init__(self, dictionary):
        super().__init__(dictionary)

    def __setitem__(self, player, new):
        """Set a player's new match and match them to the player, too.

        First check if the player and match are valid and present.
        """

        self._check_player_in_keys(player)
        self._check_new_valid_type(new, (type(None), Player))

        player.matching = new
        if isinstance(new, Player):
            new.matching = player

        self._data[player] = new


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
