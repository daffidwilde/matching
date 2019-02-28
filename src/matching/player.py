""" A player class with methods for finding and forgetting other players. """


class Player:
    """ A class to represent a player within the matching game.

    Parameters
    ==========
    name : `object`
        An identifier. This should be unique and descriptive.
    pref_names : `list` or `tuple`
        A list, or tuple, ranking the elements of the other set by
        their names.
    capacity : `int`, optional
        The maximum number of matches the player can have at once. If not
        specified, defaults to 1.

    Attributes
    ==========
    matching : `Player` or `list` of `Player` instances
        The current match(es) to the player. This is initialised as `None` and
        will remain that way at least until the player is introduced to a game.
    """

    def __init__(self, name, pref_names, capacity=1):

        self.name = name
        self.pref_names = list(pref_names)
        self._pref_names = pref_names
        self.capacity = capacity
        self.matching = None

    def __repr__(self):

        return str(self.name)

    def get_favourite_name(self):
        """ Get the player's favourite name. """

        try:
            for name in self.pref_names:
                if name not in (match.name for match in self.matching):
                    return name

        except TypeError:
            return self.pref_names[0]

        return None

    def get_favourite(self, others):
        """ Get the player's favourite member of the other party. """

        fave_name = self.get_favourite_name()

        try:
            for other in others:
                if other.name == fave_name and other not in self.matching:
                    return other

        except TypeError:
            for other in others:
                if other.name == fave_name:
                    return other

        return None

    def match(self, other):
        """ Assign other to be matched to the player. """

        try:
            self.matching.append(other)
            self.matching.sort(key=lambda m: self.pref_names.index(m.name))

        except AttributeError:
            self.matching = other

    def unmatch(self, other):
        """ Remove other from the player's current matching. """

        try:
            self.matching.remove(other)

        except AttributeError:
            self.matching = None

    def get_worst_match_idx(self):
        """ Get the preference list index of the player's worst current match.
        """

        try:
            return self.pref_names.index(self.matching[-1].name)

        except TypeError:
            return self.pref_names.index(self.matching.name)

    def get_worst_match(self):
        """ Get the worst current match to a player. """

        try:
            return self.matching[-1]

        except TypeError:
            return self.matching

    def forget(self, other):
        """ Forget another player by removing their name from the player's
        preference list. """

        self.pref_names.remove(other.name)

    def get_successors(self, others):
        """ Get all the successors to the worst current match of a player. """

        idx = self.get_worst_match_idx()
        return [
            other
            for other in others
            if other.name in self.pref_names[idx + 1 :]
        ]

    def prefers(self, player, other):
        """ Determines whether the player prefers a player over some other
        player. """

        prefs = self._pref_names
        return prefs.index(player.name) < prefs.index(other.name)
