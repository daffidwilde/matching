"""The HR game class and supporting functions."""

import warnings

import numpy as np

from matching import convert, matchings


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
        HospitalResident
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
        HospitalResident
            An instance of HR with preference lists resolved as rank
            matrices.
        """
        residents, hospitals = sorted(resident_prefs), sorted(hospital_prefs)

        resident_ranks = convert.preference_to_rank(resident_prefs, hospitals)
        hospital_ranks = convert.preference_to_rank(hospital_prefs, residents)
        capacity_array = np.array([capacities.get(h, -1) for h in hospitals])

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

        Warns
        -----
        UserWarning
            If (a) any player has not made a strict, exhaustive ranking
            of the players who ranked them, or (b) any hospital has an
            invalid capacity.
        """
        for hospital, ranks in enumerate(self.hospital_ranks):
            self._check_player_ranks(hospital, ranks, self.resident_ranks, "hospital")

        for resident, ranks in enumerate(self.resident_ranks):
            self._check_player_ranks(resident, ranks, self.hospital_ranks, "resident")

        self._check_capacities()

    @staticmethod
    def _check_player_ranks(player, player_ranks, other_ranks, side):
        """
        Check whether a player has made a valid ranking.

        Parameters
        ----------
        player : int
            Player for whom to check the ranks.
        player_ranks : np.ndarray
            Ranking by the player.
        other_ranks : np.ndarray
            Rankings of the players on the other side.
        side : {"resident", "hospital"}
            Side of the matching for the player.

        Warns
        -----
        UserWarning
            If the player has not made a strict, exhaustive ranking of
            the all the players who ranked them.
        """
        ranked_player = [other for other, ranks in enumerate(other_ranks) if player in ranks]
        same_size = len(ranked_player) == len(player_ranks)
        same_elements = set(ranked_player) == set(player_ranks)
        if not same_size or not same_elements:
            warnings.warn(
                f"{side.title()} {player} has not made a strict, exhaustive ranking of "
                f"the players who ranked them.",
                UserWarning,
            )

    def _check_capacities(self):
        """
        Check whether the hospital capacities are valid.

        Warns
        -----
        UserWarning
            If any hospital has an invalid capacity.
        """
        for hospital, capacity in enumerate(self.capacities):
            if capacity <= 0:
                warnings.warn(
                    f"Hospital {hospital} has a capacity of {capacity}.",
                    UserWarning,
                )

    def solve(self, optimal="resident"):
        """
        Solve the instance of HR.

        This method uses the adapted Gale-Shapley algorithms introduced
        by Alvin Roth in 1984 (https://doi.org/10.1086/261272). The
        algorithms find a unique, stable and party-optimal matching for
        any valid set of residents and hospitals.

        The optimality of the matching is with respect to one party and
        is subsequently the worst stable matching for the other party.

        Parameters
        ----------
        optimal : {"resident", "hospital"}, default="resident"
            Party for whom to optimise the matching.

        Raises
        ------
        ValueError
            If `optimal` is anything other than the permitted values.

        Returns
        -------
        HRMatching
            A dictionary-like object containing the matching. The keys
            correspond to the hospitals in the instance, while the
            values are lists of the residents matched to them.
        """
        if optimal == "resident":
            matching = self._resident_optimal()
        elif optimal == "hospital":
            matching = self._hospital_optimal()
        else:
            raise ValueError(
                f'Invalid choice for `optimal`. Must be "resident" or "hospital", not "{optimal}".'
            )

        self.matching = matchings.HRMatching(matching, keys="hospitals", values="residents")
        if self._preference_lookup:
            self._convert_matching_to_preferences()

        return self.matching

    def _resident_optimal(self):
        """
        Execute the resident-optimal algorithm given some rankings.

        Returns
        -------
        dict
            Solution mapping hospitals to their matched residents.
        """
        resident_ranks = self.resident_ranks
        hospital_ranks = self.hospital_ranks
        capacities = self.capacities

        matching = {h: [] for h in range(self.num_hospitals)}
        free_residents = set(range(self.num_residents))

        while free_residents:
            resident = free_residents.pop()
            resident_rank = resident_ranks[resident]
            if np.min(resident_rank) == self.num_hospitals:
                continue

            hospital = resident_rank.argmin()
            hospital_rank = hospital_ranks[hospital]
            hospital_matches = matching[hospital]
            capacity = capacities[hospital]

            if len(hospital_matches) == capacity:
                idx = hospital_rank[hospital_matches].argmax()
                worst = hospital_matches[idx]
                del hospital_matches[idx]
                free_residents.add(worst)

            hospital_matches.append(resident)

            if len(hospital_matches) == capacity:
                worst = hospital_matches[hospital_rank[hospital_matches].argmax()]
                successors = np.where(hospital_rank > hospital_rank[worst])
                resident_ranks[successors, hospital] = self.num_hospitals
                hospital_rank[successors] = self.num_residents

        return matching

    def _hospital_optimal(self):
        """
        Execute the hospital-optimal algorithm given some rankings.

        Returns
        -------
        dict
            Solution mapping hospitals to their matched residents.
        """

        def _get_current_match(resident, matching):
            """
            Get the current match for a resident (and its index) if any.

            Parameters
            ----------
            resident : int
                Resident for whom to search.
            matching : dict
                Mapping of hospitals to their matched residents.

            Returns
            -------
            tuple[int, int] | None
                Currently matched hospital and its position in the
                resident's ranking or `None` if the resident is free.
            """
            for hospital, residents in matching.items():
                for idx, res in enumerate(residents):
                    if res == resident:
                        return hospital, idx

            return None, None

        resident_ranks = self.resident_ranks.copy()
        hospital_ranks = self.hospital_ranks.copy()
        capacities = self.capacities

        matching = {h: [] for h in range(self.num_hospitals)}
        free_hospitals = set(range(self.num_hospitals))

        while free_hospitals:
            hospital = free_hospitals.pop()
            hospital_rank = hospital_ranks[hospital]
            hospital_matches = matching.get(hospital)
            options = [
                res if i not in hospital_matches else self.num_residents
                for i, res in enumerate(hospital_rank)
            ]

            is_at_capacity = len(hospital_matches) == capacities[hospital]
            has_no_options = np.min(options) == self.num_residents
            has_no_ranking = np.min(hospital_rank) == self.num_residents
            if is_at_capacity or has_no_options or has_no_ranking:
                continue

            resident = np.argmin(options)
            resident_rank = resident_ranks[resident]

            current_match, idx = _get_current_match(resident, matching)
            if current_match is not None:
                current_match_matches = matching[current_match]
                del current_match_matches[idx]
                free_hospitals.add(current_match)

            hospital_matches.append(resident)
            free_hospitals.add(hospital)

            successors = np.where(resident_rank > resident_rank[hospital])
            hospital_ranks[successors, resident] = self.num_residents
            resident_rank[successors] = self.num_hospitals

        return matching

    def _convert_matching_to_preferences(self):
        """
        Replace the rank indices with preference terms in a matching.

        This internal function is included for users who wish to create
        a matching from a set of preference list dictionaries.

        Attributes
        ----------
        HRMatching
            The converted matching instance.
        """
        converted = {}
        residents, hospitals = self._preference_lookup.values()
        for hospital, resident_matches in self.matching.items():
            converted[hospitals[hospital]] = [residents[resident] for resident in resident_matches]

        self.matching = matchings.HRMatching(converted, keys="hospitals", values="residents")
