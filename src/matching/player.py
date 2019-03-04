""" Player classes for various types of player. """


class Player:
    """ A class to represent a player within the matching game.

    Parameters
    ==========
    name : `object`
        An identifier. This should be unique and descriptive.

    Attributes
    ==========
    prefs : `list`
        A list of `Player` instances in order of the player's preferences.
        Defaults to `None` and is updated using the `set_prefs` method.
    pref_names : `list`
        A list the names in `prefs`. Updates with `prefs`.
    matching : `Player` or `None`
        The current match of the player. `None` if not currently matched.
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

    def get_successors(self):
        """ Get all the successors to the current match of the player. """

        idx = self.prefs.index(self.matching)
        return self.prefs[idx + 1 :]

    def prefers(self, player, other):
        """ Determines whether the player prefers a player over some other
        player. """

        prefs = self.pref_names
        return prefs.index(player.name) < prefs.index(other.name)


class Hospital(Player):
    """ A class to represent a hospital in an instance of HR.

    Parameters
    ==========
    name : `object`
        An identifier. This should be unique and descriptive.
    capacity : `int`
        The maximum number of matches the hospital can have.

    Attributes
    ==========
    prefs : `list`
        A list of `Player` instances in order of the hospital's preferences.
        Defaults to `None` and is updated using the `set_prefs` method.
    pref_names : `list`
        A list the names in `prefs`. Updates with `prefs`.
    matching : `list`
        The current matches of the hospital. An empty list if currently
        unsubscribed.
    """

    def __init__(self, name, capacity):

        self.name = name
        self.capacity = capacity
        self.prefs = None
        self.pref_names = None
        self.matching = []

    def get_favourite(self):
        """ Get the favourite player who is not currently in the player's
        matching. """

        for player in self.prefs:
            if player not in self.matching:
                return player

        return None

    def match(self, other):
        """ Add another player to the player's matching, and then sort it. """

        self.matching.append(other)
        self.matching.sort(key=self.prefs.index)

    def unmatch(self, other):
        """ Remove another player from the player's matching. """

        matching = list(self.matching)
        matching.remove(other)
        self.matching = matching

    def get_worst_match(self):
        """ Get the player's worst current match. Assumes that the matching is
        in order of preference. """

        return self.matching[-1]

    def get_successors(self):
        """ Get the successors to the player's worst current match. """

        idx = self.prefs.index(self.get_worst_match())
        return self.prefs[idx + 1 :]
