"""The SM game class and supporting functions."""

import warnings

import numpy as np

from matching import convert
from matching.matchings import SingleMatching


class StableMarriage:
    """
    Solver for the stable marriage problem (SM).

    Parameters
    ----------
    suitor_ranks : np.ndarray
        The rank matrix of all reviewers by the suitors.
    reviewer_ranks : np.ndarray
        The rank matrix of all suitors by the reviewers.

    Attributes
    ----------
    num_suitors : int
        Number of suitors.
    num_reviewers : int
        Number of reviewers.
    matching : SingleMatching or None
        Once the game is solved, a matching is available. This uses the
        indices of the reviewer and suitor rank matrices as keys and
        values, respectively, in a `SingleMatching` object.
        Initialises as `None`.
    """

    def __init__(self, suitor_ranks, reviewer_ranks):
        self.suitor_ranks = suitor_ranks.copy()
        self.reviewer_ranks = reviewer_ranks.copy()

        self.num_suitors = len(suitor_ranks)
        self.num_reviewers = len(reviewer_ranks)
        self.matching = None
        self._preference_lookup = None

        self.check_input_validity()

    @classmethod
    def from_utilities(cls, suitor_utils, reviewer_utils):
        """
        Create an instance of SM from utility matrices.

        Higher utilities indicate higher preferences. If there are any
        ties, they are broken in order of appearance.

        Parameters
        ----------
        suitor_utils : np.ndarray
            Suitor utility matrix.
        reviewer_utils : np.ndarray
            Reviewer utility matrix.

        Returns
        -------
        game : StableMarriage
            An instance of SM with utilities resolved as rank matrices.
        """

        suitor_ranks = convert.utility_to_rank(suitor_utils)
        reviewer_ranks = convert.utility_to_rank(reviewer_utils)

        return cls(suitor_ranks, reviewer_ranks)

    @classmethod
    def from_preferences(cls, suitor_prefs, reviewer_prefs):
        """
        Create an instance of SM from preference list dictionaries.

        Each dictionary contains a strict ordering of the other side by
        each player. The ranking is taken by the order of the preference
        list.

        Parameters
        ----------
        suitor_prefs : dict
            Suitor preference lists.
        reviewer_prefs : dict
            Reviewer preference lists.

        Returns
        -------
        game : StableMarriage
            An instance of SM with preference lists resolved as rank
            matrices.
        """

        suitors, reviewers = sorted(suitor_prefs), sorted(reviewer_prefs)

        suitor_ranks = convert.preference_to_rank(suitor_prefs, reviewers)
        reviewer_ranks = convert.preference_to_rank(reviewer_prefs, suitors)

        game = cls(suitor_ranks, reviewer_ranks)
        game._preference_lookup = {"suitors": suitors, "reviewers": reviewers}

        return game

    def _check_number_of_players(self):
        """
        Check whether the player sets are the same size.

        Warns
        -----
        UserWarning
            If the sizes of the player sets do not match.
        """

        ns, nr = self.num_suitors, self.num_reviewers
        if ns != nr:
            warnings.warn(
                f"Number of suitors ({ns}) and reviewers ({nr}) "
                "do not match. Your matching will not be truly stable.",
                UserWarning,
            )

    def _check_player_ranks(self, player, ranks, side):
        """
        Check that a player has made a strict ranking of the other side.

        Parameters
        ----------
        player : int
            Player to check.
        ranks : np.ndarray
            The player's ranking.
        side : str
            Name of the side to which the player belongs.

        Warns
        -----
        UserWarning
            If the player has not made a strict and unique ranking of
            the other side in the game.
        """

        others = "suitors" if side == "reviewer" else "reviewers"
        num_others = getattr(self, f"num_{others}")
        if not np.array_equal(np.sort(ranks), np.arange(num_others)):
            warnings.warn(
                f"{side.title()} {player} has not strictly ranked "
                f"all {num_others} {others}: {ranks}. "
                "You may not be able to find a stable matching.",
                UserWarning,
            )

    def check_input_validity(self):
        """
        Determine whether this game instance is valid or not.

        Invalid games can still be solved, but the matching will not be
        truly stable in the absence of blocking pairs.

        Warns
        -----
        UserWarning
            If (a) the player sets are not the same size; or (b) any
            player has not made a strict, exhaustive, and unique ranking
            of the players on the other side of the matching.
        """

        self._check_number_of_players()

        for suitor, ranks in enumerate(self.suitor_ranks):
            self._check_player_ranks(suitor, ranks, "suitor")

        for reviewer, ranks in enumerate(self.reviewer_ranks):
            self._check_player_ranks(reviewer, ranks, "reviewer")

    def _invert_player_sets(self):
        """
        Invert the attributes associated with each set of players.

        That is, `suitor_ranks` and `reviewer_ranks` switch. As do
        `num_suitors` and `num_reviewers`.
        """

        self.suitor_ranks, self.reviewer_ranks = (
            self.reviewer_ranks,
            self.suitor_ranks,
        )
        self.num_suitors, self.num_reviewers = (
            self.num_reviewers,
            self.num_suitors,
        )

    def _stable_marriage(self):
        """
        Execute the algorithm for SM given some rankings.

        Returns
        -------
        matching : dict
            Solution to the game instance.
        """

        matching = {}
        suitor_ranks, reviewer_ranks = self.suitor_ranks, self.reviewer_ranks
        free_suitors = list(range(self.num_suitors))

        while free_suitors:
            suitor = free_suitors.pop()
            reviewer = suitor_ranks[suitor].argmin()
            reviewer_rank = reviewer_ranks[reviewer]

            if (match := matching.get(reviewer)) is not None:
                suitor_ranks[match, reviewer] = self.num_reviewers
                if (suitor_ranks[match] < self.num_reviewers).any():
                    free_suitors.append(match)

            matching[reviewer] = suitor

            successors = np.where(reviewer_rank > reviewer_rank[suitor])
            suitor_ranks[successors, reviewer] = self.num_reviewers
            reviewer_rank[successors] = self.num_reviewers

        return matching

    def _convert_matching_to_preferences(self):
        """
        Replace the rank indices with preference terms in a matching.

        This internal function is included for users who wish to create
        a matching from a set of preference list dictionaries.

        Attributes
        ----------
        matching : SingleMatching
            The converted matching instance.
        """

        converted = {}
        suitors, reviewers = self._preference_lookup.values()
        for reviewer, suitor in self.matching.items():
            converted[reviewers[reviewer]] = suitors[suitor]

        self.matching = SingleMatching(
            converted, valid=self.matching.valid, stable=self.matching.stable
        )

    def solve(self, optimal="suitor"):
        """
        Solve the instance of SM.

        This method uses an extended version of the Gale-Shapley
        algorithm that makes use of the inherent structures of SM
        instances. The algorithm finds a unique, stable and optimal
        matching is found for any valid set of suitors and reviewers.

        The optimality of the matching is with respect to one party and
        is subsequently the worst stable matching for the other party.

        Parameters
        ----------
        optimal : {"suitor", "reviewer"}, default "suitor"
            Party for whom to optimise the matching. Must be one of
            `"suitor"` or `"reviewer"`. Default is `"suitor"`.

        Raises
        ------
        ValueError
            If `optimal` is anything other than the permitted values.

        Returns
        -------
        matching : SingleMatching
            A dictionary-like object containing the matching. The keys
            correspond to the reviewers in the instance, while the
            values are the suitors.
        """

        if optimal not in ("suitor", "reviewer"):
            raise ValueError(
                "Invalid choice for `optimal`. "
                f'Must be "suitor" or "reviewer", not "{optimal}".'
            )

        keys, values = "reviewers", "suitors"

        if optimal == "reviewer":
            self._invert_player_sets()
            keys, values = values, keys

        matching = SingleMatching(
            self._stable_marriage(), keys=keys, values=values
        )

        if optimal == "reviewer":
            matching = matching.invert()
            self._invert_player_sets()

        self.matching = matching
        if self._preference_lookup:
            self._convert_matching_to_preferences()

        return self.matching
