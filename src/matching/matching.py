""" A dictionary-like object for matchings. """

from .player import Player


class Matching(dict):
    """ A class to store, and allow for the easy updating of, matchings found by
    a game solver.

    Attributes
    ----------
    dictionary : dict or None
        If not ``None``, a dictionary mapping a ``Player`` to one of: ``None``,
        a single ``Player`` or a list of ``Player`` instances.
    """

    def __init__(self, dictionary=None):

        self.__data = {}
        if dictionary is not None:
            self.__data.update(dictionary)

        super().__init__(self.__data)

    def __repr__(self):

        return repr(self.__data)

    def __getitem__(self, player):

        return self.__data[player]

    def __setitem__(self, player, new_match):

        if player not in self.__data.keys():
            raise ValueError(f"{player} is not a key in this matching.")

        if isinstance(new_match, Player):
            new_match.matching = player
            player.matching = new_match

        elif new_match is None:
            player.matching = new_match

        elif isinstance(new_match, (list, tuple)) and all(
            [isinstance(new, Player) for new in new_match]
        ):
            player.matching = new_match
            for new in new_match:
                new.matching = player

        else:
            raise ValueError(f"{new_match} is not a valid match.")

        self.__data[player] = new_match

    def keys(self):

        return self.__data.keys()

    def values(self):

        return self.__data.values()
