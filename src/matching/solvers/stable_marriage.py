""" The Stable Marriage Problem solver and algorithm. """

from matching import BaseSolver

from .util import delete_pair, match_pair, unmatch_pair


class StableMarriage(BaseSolver):
    """ A class for solving instances of the Stable Marriage Problem (SM) using
    the extended Gale-Shapley algorithm.

    Parameters
    ==========
    suitors : `list` of `Player` instances
        The suitors in the matching game. Each suitor must rank the names of all
        elements in `reviewers`.
    reviewers : `list` of `Player` instances
        The reviewers in the matching game. Each reviewer must rank the names of
        all elements in `suitors`.

    Attributes
    ==========
    matching : `dict`
        Once the game is solved, a matching is available. This uses the suitors
        and reviewers as keys and values in a dictionary, respectively.
        Initialises as `None`.
    blocking_pairs : `list` of (`suitor`, `reviewer`)-tuples
        The suitor-reviewer pairs that both prefer one another to their current
        match. Initialises as `None`.
    """

    def __init__(self, suitors, reviewers):

        for player in suitors + reviewers:
            player.matching = None

        self.suitors = suitors
        self.reviewers = reviewers

        self.__check_inputs()

        super().__init__(suitors, reviewers)

    def solve(self, optimal="suitor"):
        """ Solve the instance of SM using either the suitor- or
        reviewer-oriented Gale-Shapley algorithm. Return the matching. """

        self._matching = stable_marriage(self.suitors, self.reviewers, optimal)
        return self.matching

    def check_stability(self):
        """ Check for the existence of any blocking pairs in the current
        matching, thus determining the stability of the matching. """

        blocking_pairs = []
        for suitor in self.suitors:
            for reviewer in self.reviewers:
                if suitor.prefers(
                    reviewer, suitor.matching
                ) and reviewer.prefers(suitor, reviewer.matching):
                    blocking_pairs.append((suitor, reviewer))

        self.blocking_pairs = blocking_pairs
        return not any(blocking_pairs)

    def check_validity(self):
        """ Check whether the current matching is valid. """

        self.__check_all_matched()
        self.__check_matching_consistent()

    def __check_all_matched(self):
        """ Check everyone has a match. """

        errors = []
        for player in self.suitors + self.reviewers:
            if player.matching is None:
                errors.append(ValueError(f"{player} is unmatched."))

        if errors:
            raise Exception(errors)

    def __check_matching_consistent(self):
        """ Check that the game matching is consistent with the players. """

        errors = []
        for suit, rev in self.matching.items():
            if suit.matching != rev:
                errors.append(
                    ValueError(
                        f"{suit} is matched to {suit.matching}, not {rev}."
                    )
                )
            if rev.matching != suit:
                errors.append(
                    ValueError(f"{rev} matched to {rev.matching}, not {suit}.")
                )

        if errors:
            raise Exception(errors)

    def __check_inputs(self):
        """ Raise an error if any of the conditions of the game have been
        broken. """

        self.__check_num_players()
        for suitor in self.suitors:
            self.__check_player_ranks(suitor)
        for reviewer in self.reviewers:
            self.__check_player_ranks(reviewer)

    def __check_num_players(self):
        """ Check that the number of suitors and reviewers are equal. """

        if len(self.suitors) != len(self.reviewers):
            raise ValueError(
                "There must be an equal number of suitors and reviewers."
            )

    def __check_player_ranks(self, player):
        """ Check that a player has ranked all of the other group. """

        others = self.reviewers if player in self.suitors else self.suitors
        names = set([other.name for other in others])
        prefs = set(player.pref_names)
        if prefs != names:
            raise ValueError(
                "Every player must rank each name from the other group. "
                f"{player}: {prefs} != {names}"
            )


def stable_marriage(suitors, reviewers, optimal="suitor", verbose=False):
    """ An extended version of the original Gale-Shapley algorithm which makes
    use of the inherent structures of matching games. A unique, stable and
    optimal matching is found for any valid set of suitors and reviewers. The
    optimality of the matching is with respect to one party and is subsequently
    the worst stable matching for the other.

    Parameters
    ==========
    suitors : `list` of `Player` instances
        The suitors in the game. Must rank all the names of those in
        `reviewers`.
    reviewers : `list` of `Player` instances
        The reviewers in the game. Must rank all the names of those in
        `suitors`.
    optimal : `str`, optional
        Which party the matching should be optimised for. Must be one of
        `"suitor"` and `"reviewer"`. Defaults to the former.
    verbose : `bool`, optional
        Whether or not to log the progress of the algorithm. Default is to not.

    Returns
    =======
    matching : `dict`
        A dictionary of `Player` instances. The keys are given by the members of
        `suitors`, and the values are their match in `reviewers`.
    """

    if optimal.lower() == "reviewer":
        suitors, reviewers = reviewers, suitors

    free_suitors = [s for s in suitors if not s.matching]
    while free_suitors:

        suitor = free_suitors.pop()
        reviewer = suitor.get_favourite(reviewers)

        if reviewer.matching:
            curr_match = reviewer.matching
            unmatch_pair(curr_match, reviewer)
            free_suitors.append(curr_match)

        match_pair(suitor, reviewer)

        successors = reviewer.get_successors(suitors)
        for successor in successors:
            delete_pair(successor, reviewer)

    if optimal.lower() == "reviewer":
        suitors, reviewers = reviewers, suitors

    return {s: s.matching for s in suitors}
