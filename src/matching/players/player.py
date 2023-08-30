""" The base Player class for use in various games. """

from matching import BasePlayer


class Player(BasePlayer):
    """Generic single-match player class for instances of SM or SR.

    This class is also used for residents in HR and students in SA.

    Parameters
    ----------
    name : object
        An identifier. This should be unique and descriptive.

    Attributes
    ----------
    prefs : list of Player
        The player's preferences. Defaults to ``None`` and is updated
        using the ``set_prefs`` method.
    pref_names : list
        A list of the names in ``prefs``. Updates with ``prefs`` via
        ``set_prefs`` method.
    matching : Player or None
        The current match of the player. ``None`` if not currently
        matched.
    _original_prefs : list of Player
        The original set of player preferences.
    """

    def __init__(self, name):
        super().__init__(name)

    def _match(self, other):
        """Assign the player to be matched to some other player."""

        self.matching = other

    def _unmatch(self):
        """Set the player to be unmatched."""

        self.matching = None

    def get_favourite(self):
        """Get the player's favourite player."""

        return self.prefs[0]

    def get_successors(self):
        """Get all the successors to the current match of the player."""

        idx = self.prefs.index(self.matching)
        return self.prefs[idx + 1 :]

    def check_if_match_is_unacceptable(self, unmatched_okay=False):
        """Check the acceptability of the current match.

        In some games, a player being unmatched does not invalidate the
        game. The ``unmatched_okay`` parameter controls this behaviour.
        """

        other = self.matching

        if other is None and unmatched_okay is False:
            return self.unmatched_message()

        elif other is not None and other not in self.prefs:
            return self.not_in_preferences_message(other)
