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
        In the case of hospital-resident assignment problems, a hospital should
        have an integer capacity. If not specified, defaults to 1.

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
        self.capacity = capacity
        self.match = None
        if self.capacity > 1:
            self.match = []

    def __repr__(self):

        return str(self.name)

    def get_favourite(self, others):
        """ Get the player's favourite member of the other party. """

        preferred_name = self.pref_names[0]
        preferred = [other for other in others if other.name == preferred_name]

        return preferred[0]

    def get_worst_match_idx(self):
        """ Get the preference list index of the player's worst current match.
        """

        return max((self.pref_names.index(other.name) for other in self.match))

    def forget(self, other):
        """ Forget another player by removing them from the player's preference
        list. """

        self.pref_names.remove(other.name)

    def get_successors(self, others, idx=None):
        """ Get all the successors either to the current match (for simple
        games) or the worst current match (for capacitated games). This match is
        at position `idx` in the player's preference list. """

        if not idx:
            idx = self.pref_names.index(self.match.name)
            return (
                other
                for other in others
                if other.name in self.pref_names[idx + 1 :]
            )

        return (p for p in others if p.name in self.pref_names[idx + 1 :])
