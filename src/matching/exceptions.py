"""Exceptions for game solver checks."""


class MatchingError(Exception):
    """A generic exception for erroneous ``matching`` objects."""

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            self.__setattr__(key, val)

        self.message = kwargs
        super().__init__(self.message)


class NoStableMatchingWarning(UserWarning):
    """For when a game does not have a complete stable matching."""


class PreferencesChangedWarning(UserWarning):
    """For when a player has an invalid preference list."""


class CapacityChangedWarning(UserWarning):
    """For when a player has an invalid capacity."""


class PlayerExcludedWarning(UserWarning):
    """For when a player should be excluded from a game."""
