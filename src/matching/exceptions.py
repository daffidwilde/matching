""" Exceptions for game solver checks. """

class MatchingError(Exception):
    """ A generic error for when something is wrong with an internal object. """

    def __init__(self, unacceptables=[], oversubscribeds=[]):

        self.unacceptables = unacceptables
        self.oversubscribeds = oversubscribeds
        self.message = [*unacceptables, *oversubscribeds]

        super().__init__(self.message)

class PreferencesChangedWarning(UserWarning):
    """ A warning for when the preferences of a player are invalid. """


class CapacityChangedWarning(UserWarning):
    """ A warning for when the capacity of a player is invalid. """


class PlayerExcludedWarning(UserWarning):
    """ A warning for when a player is to be excluded from a game. """
