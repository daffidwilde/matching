"""The HR game class and supporting functions."""

import numpy as np

from matching import convert


class HospitalResident:
    """
    Solver for the hospital-resident assignment problem (HR).

    Parameters
    ----------
    resident_ranks : np.ndarray
        The rank matrix of all hospitals by the residents.
    hospital_ranks : np.ndarray
        The rank matrix of all residents by the hospitals.
    capacities : np.ndarray
        Capacity matrix for the hospitals.

    Attributes
    ----------
    num_residents : int
        Number of residents.
    num_hospitals : int
        Number of hospitals.
    matching : MultipleMatching or None
        Once the game is solved, a matching is available. This uses the
        indices of the hospital and resident rank matrices as keys and
        values, respectively, in a `MultipleMatching` object.
        Initialises as `None`.
    """

    def __init__(self, resident_ranks, hospital_ranks, capacities):
        self.resident_ranks = resident_ranks.copy()
        self.hospital_ranks = hospital_ranks.copy()
        self.capacities = capacities.copy()

        self.num_residents = len(resident_ranks)
        self.num_hospitals = len(hospital_ranks)
        self.matching = None
        self._preference_lookup = None

        self.check_input_validity()

    @classmethod
    def from_utilities(cls, resident_utils, hospital_utils, capacities):
        """
        Create an instance of HR from utility matrices.

        Higher utilities indicate higher preferences. If there are any
        ties, they are broken in order of appearance.

        Parameters
        ----------
        resident_utils : np.ndarray
            Resident utility matrix.
        hospital_utils : np.ndarray
            Hospital utility matrix.
        capacities : np.ndarray
            Hospital capacity vector.

        Returns
        -------
        game : HospitalResident
            An instance of HR with utilities resolved as rank matrices.
        """
        resident_ranks = convert.utility_to_rank(resident_utils)
        hospital_ranks = convert.utility_to_rank(hospital_utils)

        return cls(resident_ranks, hospital_ranks, capacities)

    @classmethod
    def from_preferences(cls, resident_prefs, hospital_prefs, capacities):
        """
        Create an instance of HR from preference list dictionaries.

        Each dictionary should contain a strict ordering of the other
        side by each player. The ranking is taken by the order of the
        preference list.

        Parameters
        ----------
        resident_prefs : dict
            Resident preference lists.
        hospital_prefs : dict
            Hospital preference lists.
        capacities : dict
            Hospital capacities.

        Returns
        -------
        game : HospitalResident
            An instance of HR with preference lists resolved as rank
            matrices.
        """
        residents, hospitals = sorted(resident_prefs), sorted(hospital_prefs)

        resident_ranks = convert.preference_to_rank(resident_prefs, hospitals)
        hospital_ranks = convert.preference_to_rank(hospital_prefs, residents)
        capacity_array = np.array([capacities.get(h) for h in hospitals])

        game = cls(resident_ranks, hospital_ranks, capacity_array)
        game._preference_lookup = {
            "residents": residents,
            "hospitals": hospitals,
        }

        return game

    def check_input_validity(self):
        """
        Determine whether this game instance is valid or not.

        Invalid games can still be solved, but the matching will not be
        truly stable in the absence of blocking pairs.
        """
