"""Module for the matching object classes."""

import collections


class _BaseMatching(dict):
    """
    Dictionary-like object for holding game solutions. For inheritance.

    Parameters
    ----------
    dictionary : dict
        Dictionary of matched up pairs.
    keys : str
        Name of the key-side party. Renamed `keys_`.
    values : str
        Name of the value-side party. Renamed `values_`.
    """

    KEYS = "keys"
    VALUES = "values"

    def __init__(self, dictionary=None, *, keys=None, values=None):
        super().__init__(dictionary or {})

        self.keys_ = keys or self.KEYS
        self.values_ = values or self.VALUES

    def __repr__(self):
        name = self.__class__.__name__
        return f'{name}({super().__repr__()}, keys="{self.keys_}", values="{self.values_}")'

    def __eq__(self, other):
        if isinstance(other, _BaseMatching):
            return super().__eq__(other) and vars(self) == vars(other)
        if isinstance(other, dict):
            return super().__eq__(other)


class _SingleMatching(_BaseMatching):
    """
    Dictionary-like object for solutions to games with singular matches.

    Parameters
    ----------
    dictionary : dict
        Dictionary of matched up pairs.
    keys : str
        Name of the key-side party. Renamed `keys_`.
    values : str
        Name of the value-side party. Renamed `values_`.
    """

    def invert(self):
        """
        Invert the keys and values in the dictionary.

        Returns
        -------
        inverted : SingleMatching
            An inverted matching.
        """
        inverted = {val: key for key, val in self.items()}

        return self.__class__(inverted, keys=self.values_, values=self.keys_)


class _MultipleMatching(_BaseMatching):
    """
    Dictionary-like object for solutions to games with multiple matches.

    Parameters
    ----------
    dictionary : dict
        Dictionary mapping players to their matches.
    keys : str
        Name of the key-side party. Renamed `keys_`.
    values : str
        Name of the value-side party. Renamed `values_`.
    """

    def invert(self):
        """
        Invert the keys and list values in the dictionary.

        Returns
        -------
        MultipleMatching
            An inverted matching.
        """
        inverted = collections.defaultdict(list)
        for key, values in self.items():
            for value in values:
                inverted[value].append(key)

        return self.__class__(dict(inverted), keys=self.values_, values=self.keys_)


class SMMatching(_SingleMatching):
    """Dictionary-like object for solutions to SM game instances."""

    KEYS = "reviewers"
    VALUES = "suitors"


class HRMatching(_MultipleMatching):
    """Dictionary-like object for solutions to HR game instances."""

    KEYS = "hospitals"
    VALUES = "residents"
