""" The Stable Marriage Problem solver and algorithm. """

from matching import BaseSolver, Matching

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
    matching : `Matching` (`dict`-like)
        Once the game is solved, a matching is available. This uses the suitors
        and reviewers as keys and values, respectively, in a `Matching` object;
        something that closely resembles a standard Python dictionary.
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

        self._check_inputs()

        super().__init__(suitors, reviewers)

    def solve(self, optimal="suitor"):
        """ Solve the instance of SM using either the suitor- or
        reviewer-oriented Gale-Shapley algorithm. Return the matching. """

        self._matching = Matching(
            stable_marriage(self.suitors, self.reviewers, optimal)
        )
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

        self._check_all_matched()
        self._check_matching_consistent()
        return True

    def _check_all_matched(self):
        """ Check everyone has a match. """

        errors = []
        for player in self.suitors + self.reviewers:
            if player.matching is None:
                errors.append(ValueError(f"{player} is unmatched."))
            if player not in list(self.matching.keys()) + list(
                self.matching.values()
            ):
                errors.append(
                    ValueError(f"{player} does not appear in matching.")
                )

        if errors:
            raise Exception(*errors)

        return True

    def _check_matching_consistent(self):
        """ Check that the game matching is consistent with the players. """

        errors = []
        matching = self.matching
        for suitor in self.suitors:
            if suitor.matching != matching[suitor]:
                errors.append(
                    ValueError(
                        f"{suitor} is matched to {suitor.matching} but matching"
                        f" says {matching[suitor]}."
                    )
                )

        for reviewer in self.reviewers:
            suitor = [s for s in matching if matching[s] == reviewer][0]
            if reviewer.matching != suitor:
                errors.append(
                    ValueError(
                        f"{reviewer} is matched to {reviewer.matching} but "
                        f"matching says {suitor}."
                    )
                )

        if errors:
            raise Exception(*errors)

        return True

    def _check_inputs(self):
        """ Raise an error if any of the conditions of the game have been
        broken. """

        self._check_num_players()
        for suitor in self.suitors:
            self._check_player_ranks(suitor)
        for reviewer in self.reviewers:
            self._check_player_ranks(reviewer)

    def _check_num_players(self):
        """ Check that the number of suitors and reviewers are equal. """

        if len(self.suitors) != len(self.reviewers):
            raise ValueError(
                "There must be an equal number of suitors and reviewers."
            )

        return True

    def _check_player_ranks(self, player):
        """ Check that a player has ranked all of the other group. """

        others = self.reviewers if player in self.suitors else self.suitors
        names = set([other.name for other in others])
        prefs = set(player.pref_names)
        if prefs != names:
            raise ValueError(
                "Every player must rank each name from the other group. "
                f"{player}: {prefs} != {names}"
            )

        return True


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
    matching : `Matching` (`dict`-like)
        A dictionary-like object of `Player` instances. The keys are given by
        the members of `suitors`, and the values are their match in `reviewers`.
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
