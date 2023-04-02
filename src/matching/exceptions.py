""" Exceptions for game solver checks. """


class MatchingError(Exception):
    """A generic error for when something is wrong with an internal object."""

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            self.__setattr__(key, val)

        self.message = kwargs
        super().__init__(self.message)


class NoStableMatchingWarning(UserWarning):
    """A warning for when a game does not have a complete stable matching."""


class PreferencesChangedWarning(UserWarning):
    """A warning for when the preferences of a player are invalid."""


class CapacityChangedWarning(UserWarning):
    """A warning for when the capacity of a player is invalid."""


class PlayerExcludedWarning(UserWarning):
    """A warning for when a player is to be excluded from a game."""
