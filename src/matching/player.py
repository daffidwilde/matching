""" A player class with methods for finding and forgetting other players. """


class Player:
    """ A class to represent a player within the matching game.

    Parameters
    ==========
    name : `object`
        An identifier. This should be unique and descriptive.
    pref_names : `list`
        A list ranking the elements of the other set by their names.
    capacity : `int`, optional
        The maximum number of matches the player can have at once. If not
        specified, defaults to 1.

    Attributes
    ==========
    match : `Player` or `list` of `Player` instances
        The current match to the player. This is initialised as `None` or an
        empty list (depending on the type of game) and will remain that way
        until the player's game is solved.
    """

    def __init__(self, name, pref_names, capacity=1):

        self.name = name
        self.pref_names = pref_names
        self._pref_names = tuple(pref_names)
        self.capacity = capacity
        self.matching = None
        if self.capacity > 1:
            self.matching = []

    def __repr__(self):

        return str(self.name)

    def get_favourite_name(self):
        """ Get the player's favourite name. """

        if isinstance(self.matching, list):
            for name in self.pref_names:
                if name not in (match.name for match in self.matching):
                    return name

        if isinstance(self.matching, (Player, type(None))):
            return self.pref_names[0]

        return None

    def get_favourite(self, others):
        """ Get the player's favourite member of the other party. """

        fave_name = self.get_favourite_name()

        if not self.matching or isinstance(self.matching, Player):
            for other in others:
                if other.name == fave_name:
                    return other

        for other in others:
            if other.name == fave_name and other not in self.matching:
                return other

        return None

    def match(self, other):
        """ Assign other to be matched to the player. """

        if isinstance(self.matching, list):
            self.matching.append(other)
        else:
            self.matching = other

    def unmatch(self, other):
        """ Remove other from the player's current matching. """

        if isinstance(self.matching, list):
            self.matching.remove(other)
        else:
            self.matching = None

    def get_worst_match_idx(self):
        """ Get the preference list index of the player's worst current match.
        """

        if isinstance(self.matching, list):
            return max(
                (self.pref_names.index(other.name) for other in self.matching)
            )

        return self.pref_names.index(self.matching.name)

    def forget(self, other):
        """ Forget another player by removing their name from the player's
        preference list. """

        self.pref_names = [
            name for name in self.pref_names if name != other.name
        ]

    def get_successors(self, others, idx=None):
        """ Get all the successors either to the current match (for simple
        games) or the worst current match (for capacitated games). This match is
        at position `idx` in the player's preference list. """

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
