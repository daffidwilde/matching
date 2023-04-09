"""The Hospital class for use in instances of HR."""

from matching import BasePlayer


class Hospital(BasePlayer):
    """Hospital player class for instances of HR.

    A hospital can take multiple simultaneous matches and has a
    capacity. The classes for projects and supervisors in SA inherit
    from this class.

    Parameters
    ----------
    name : object
        An identifier. This should be unique and descriptive.
    capacity : int
        The maximum number of matches the hospital can have.

    Attributes
    ----------
    prefs : list of Player
        The hospital's preferences. Defaults to ``None`` and is updated
        using the ``set_prefs`` method.
    pref_names : list
        A list of the names in ``prefs``. Updates with ``prefs`` via the
        ``set_prefs`` method.
    matching : list of Player
        The current matches of the hospital. An empty list if currently
        unsubscribed.
    _original_capacity : int
        A record of the player's original capacity in case it is altered
        when passed to a game.
    _original_prefs : list of Player
        A record of the player's original preferences.
    """

    def __init__(self, name, capacity):
        super().__init__(name)
        self.capacity = capacity
        self._original_capacity = capacity
        self.matching = []

    def _match(self, resident):
        """Add resident to the hospital's matching, and then sort it."""

        self.matching.append(resident)
        self.matching.sort(key=self.prefs.index)

    def _unmatch(self, resident):
        """Remove resident from the hospital's matching."""

        matching = self.matching[:]
        matching.remove(resident)
        self.matching = matching

    def oversubscribed_message(self):
        """Message to say the hospital has too many matches."""

        return (
            f"{self} is matched to {self.matching} which is over their "
            f"capacity of {self.capacity}."
        )

    def get_favourite(self):
        """Get the hospital's favourite resident outside their matching.

        If no such resident exists, return ``None``.
        """

        for player in self.prefs:
            if player not in self.matching:
                return player

        return None

    def get_worst_match(self):
        """Get the player's worst current match.

        This method assumes that the hospital's matching is in order of
        their preference list.
        """

        return self.matching[-1]

    def get_successors(self):
        """Get the successors to the player's worst current match."""

        idx = self.prefs.index(self.get_worst_match())
        return self.prefs[idx + 1 :]

    def check_if_match_is_unacceptable(self, **kwargs):
        """Check the acceptability of the current matches."""

        issues = []
        for other in self.matching:
            if other not in self.prefs:
                issues.append(self.not_in_preferences_message(other))

        return issues

    def check_if_oversubscribed(self):
        """Check whether the player has too many matches."""

        if len(self.matching) > self.capacity:
            return self.oversubscribed_message()

        return False
