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
                if (
                    suitor.prefers(reviewer, suitor.matching)
                    and reviewer.prefers(suitor, reviewer.matching)
                ):
                    blocking_pairs.append((suitor, reviewer))

        self.blocking_pairs = blocking_pairs
        return not any(blocking_pairs)


def stable_marriage(suitors, reviewers, optimal="suitor", verbose=False):
    """ An extended version of the original Gale-Shapley algorithm which makes
    use of the inherent structures of matching games. A unique, stable and
    optimal matching is found for any valid set of suitors and reviewers. The
    optimality of the matching is with respect to one party and is subsequently
    the worst stable matching for the other.

    Parameters
    ==========
    suitors : `list` of `Player` instances
        The suitors (applicants) in the game. Each suitor must be a valid
        instance of the `Player` class that ranks elements of `reviewers`.
    reviewers : `list` of `Player` instances
        The reviewers in the game. Each reviewer should be a valid instance of
        the `Player` class that ranks elements of `suitors`.
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
