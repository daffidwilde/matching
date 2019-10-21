""" The Hospital class for use in instances of HR. """

from matching import Player


class Hospital(Player):
    """ A class to represent a hospital in an instance of HR. Also used as a
    parent class to ``Project`` and ``Supervisor``.

    Parameters
    ----------
    name : object
        An identifier. This should be unique and descriptive.
    capacity : int
        The maximum number of matches the hospital can have.

    Attributes
    ----------
    prefs : list of Player
        The hospital's preferences. Defaults to ``None`` and is updated using
        the ``set_prefs`` method.
    pref_names : list
        A list of the names in ``prefs``. Updates with ``prefs`` via the
        ``set_prefs`` method.
    matching : list of Player
        The current matches of the hospital. An empty list if currently
        unsubscribed.
    """

    def __init__(self, name, capacity):

        super().__init__(name)
        self.capacity = capacity
        self.matching = []

    def get_favourite(self):
        """ Get the hospital's favourite resident with whom they are not
        currently matched. If no such resident exists, return ``None``. """

        for player in self.prefs:
            if player not in self.matching:
                return player

        return None

    def match(self, resident):
        """ Add ``resident`` to the hospital's matching, and then sort it. """

        self.matching.append(resident)
        self.matching.sort(key=self.prefs.index)

    def unmatch(self, resident):
        """ Remove ``resident`` from the hospital's matching. """

        matching = self.matching[:]
        matching.remove(resident)
        self.matching = matching

    def get_worst_match(self):
        """ Get the player's worst current match. This assumes that the matching
        is in order of preference. """

        return self.matching[-1]

    def get_successors(self):
        """ Get the successors to the player's worst current match. """

        idx = self.prefs.index(self.get_worst_match())
        return self.prefs[idx + 1 :]
