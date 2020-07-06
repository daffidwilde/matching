""" Warnings for game input checks. """


class InvalidPreferencesWarning(UserWarning):
    """ A warning for when the preferences of a player are invalid. """


class InvalidCapacityWarning(UserWarning):
    """ A warning for when the capacity of a player is invalid. """


class PlayerExcludedWarning(UserWarning):
    """ A warning for when a player is to be excluded from a game. """
