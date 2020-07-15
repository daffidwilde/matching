""" A collection of dictionary-like objects for storing matchings. """

from matching.players import Player
from matching import BaseMatching


class SingleMatching(BaseMatching):
    """ A dictionary-like object for storing and updating a matching with
    singular matches such as those in an instance of SM or SR.

    Parameters
    ----------
    dictionary
        The dictionary of matches. Made up of :code:`Player, Optional[Player]`
        key, value pairs.
    """

    def __init__(self, dictionary):

        super().__init__(dictionary)

    def __setitem__(self, player, new):

        self._check_player_in_keys(player)
        self._check_new_valid_type(new, (type(None), Player))

        player.matching = new
        if isinstance(new, Player):
            new.matching = player

        self._data[player] = new


class MultipleMatching(BaseMatching):
    """ A dictionary-like object for storing and updating a matching with
    multiple matches such as those in an instance of HR or SA.

    Parameters
    ----------
    dictionary
        The dictionary of matches. Made up of :code:`Hospital, List[Player]`
        key, value pairs.
    """

    def __init__(self, dictionary):

        super().__init__(dictionary)

    def __setitem__(self, player, new):

        self._check_player_in_keys(player)
        self._check_new_valid_type(new, (list, tuple))
        for other in new:
            self._check_new_valid_type(other, Player)

        player.matching = new
        for other in new:
            other.matching = player

        self._data[player] = new
