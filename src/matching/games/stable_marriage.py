"""The SM game class and supporting functions."""

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
