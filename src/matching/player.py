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
        self.pref_names = None
        self.matching = None

    def __repr__(self):

        return str(self.name)

    def set_prefs(self, players):
        """ Set the player's preferences to be a list of players. """

        self.prefs = players
        self.pref_names = [player.name for player in players]

    def get_favourite(self):
        """ Get the player's favourite player. """

        return self.prefs[0]

    def match(self, other):
        """ Assign the player to be matched to some other player. """

        self.matching = other

    def unmatch(self):
        """ Set the player to be unmatched. """

        self.matching = None

    def forget(self, other):
        """ Forget another player by removing them from the player's preference
        list. """

        prefs = list(self.prefs)
        prefs.remove(other)
        self.prefs = prefs

    def get_match_idx(self):
        """ Return the preference index of the player's current match. """

        return self.prefs.index(self.matching)

    def get_successors(self, others):
        """ Get all the successors to the current match of the player. """

        idx = self.get_match_idx()
        return [
            other
            for other in others
            if other in self.prefs[idx + 1 :]
        ]

    def prefers(self, player, other):
        """ Determines whether the player prefers a player over some other
        player. """

        prefs = self.pref_names
        return prefs.index(player.name) < prefs.index(other.name)
