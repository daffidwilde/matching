""" The Faculty class for instances of SA. """

from .hospital import Hospital


class Faculty(Hospital):
    """ A class to represent a faculty member in an instance of SA.

    Parameters
    ==========
    name : `object`
        An identifier. This should be unique and descriptive.
    capacity : `int`
        The maximum number of matches the faculty member can have.

    Attributes
    ==========
    projects : `list`
        The projects that the faculty member runs. Defaults to `None`.
    prefs : `list`
        A list of `Player` instances in the order of preference.
    pref_names : `list`
        A list of the names in `prefs`. Updates with `prefs`.
    matching : `list`
        The current matches of the faculty member. An empty list if currently
        unsubscribed, and updated through its project matching updates.
    """

    def __init__(self, name, capacity):

        super().__init__(name, capacity)
        self.projects = None
