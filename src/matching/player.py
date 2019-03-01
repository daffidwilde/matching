""" Player classes for various types of player. """

class Player:
    """ A class to represent a player within the matching game.

    Parameters
    ==========
    name : `object`
        An identifier. This should be unique and descriptive.
    """

    def __init__(self, name):

        self.name = name
        self.prefs = None
        self.matching = None

    def __repr__(self):

        return str(self.name)

    def set_prefs(self, players):
        """ Set the player's preferences to be an ordered list of another set of
        `Player` instances. """

        self.prefs = players

    def get_favourite(self):
        """ Get the player's favourite member of another party. """

        return self.prefs[0]

    def match(self, other):
        """ Assign other to be matched to the player. """

        self.matching = other

    def unmatch(self):
        """ Set the player to be unmatched. """

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
