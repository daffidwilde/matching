"""Classes for handling single match matchings."""


class SingleMatching(dict):
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
    valid : bool or None
        Validity of the matching. Initialises as `None`.
    stable : bool or None
        Stability of the matching. Initialises as `None`.
    """

    def __init__(
        self,
        dictionary=None,
        *,
        keys="reviewers",
        values="suitors",
        valid=None,
        stable=None,
    ):
        super().__init__(dictionary or {})

        self.keys_ = keys
        self.values_ = values
        self.valid = valid
        self.stable = stable

    def __repr__(self):
        return (
            f"SingleMatching({super().__repr__()}, "
            f'keys="{self.keys_}", values="{self.values_}")'
        )

    def __eq__(self, other):
        return super().__eq__(other) and vars(self) == vars(other)

    def invert(self):
        """
        Invert the keys and values in the dictionary.

        Creates a new matching instance with keys and values reversed,
        and passes over the validity and stability attributes.

        Returns
        -------
        inverted : SingleMatching
            An inverted matching.
        """
        return SingleMatching(
            {val: key for key, val in self.items()},
            keys=self.values_,
            values=self.keys_,
            valid=self.valid,
            stable=self.stable,
        )
