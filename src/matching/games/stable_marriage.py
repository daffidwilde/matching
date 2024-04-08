"""The SM game class and supporting functions."""

import warnings

import numpy as np

from matching import convert


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

        suitors = tuple(suitor_prefs.keys())
        reviewers = tuple(reviewer_prefs.keys())

        suitor_ranks = convert.preference_to_rank(suitor_prefs, reviewers)
        reviewer_ranks = convert.preference_to_rank(reviewer_prefs, suitors)

        return cls(suitor_ranks, reviewer_ranks)

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
