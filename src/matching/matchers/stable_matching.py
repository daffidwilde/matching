""" Stable Matching Problem matchers. """

from matching import Matcher
from matching.algorithms import stable_matching


class SMMatcher(Matcher):
    """ A class for solving instances of the Stable Matching Problem (SM) using
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
        Once the game is solved, a matching is available in the form of a
        dictionary. This uses the suitors and reviewers as its keys and values
        respectively. Initialises as `None`.
    blocking_pairs : `list` of (`suitor`, `reviewer`)-tuples
        The suitor-reviewer pairs that both prefer one another to their current
        match. Initialises as `None`.
    """

    def __init__(self, suitors, reviewers):

        for player in suitors + reviewers:
            player.match = None

        self.suitors = suitors
        self.reviewers = reviewers

        super().__init__(suitors, reviewers)

    def solve(self, optimal="suitor"):
        """ Solve the instance of SM using either the suitor- or
        reviewer-oriented Gale-Shapley algorithm. Return the matching. """

        self.matching = stable_matching(self.suitors, self.reviewers, optimal)
        return self.matching

    def check_stability(self):
        """ Check for the existence of any blocking pairs in the current
        matching, thus determining the stability of the matching. """

        blocking_pairs = []
        for suitor, reviewer in self.matching.items():
            idx = suitor.pref_names.index(reviewer.name)
            preferred = [
                r for r in self.reviewers if r.name in suitor.pref_names[:idx]
            ]
            for rev in preferred:
                partner = rev.match
                if rev.pref_names.index(suitor.name) > rev.pref_names.index(
                    partner.name
                ):
                    blocking_pairs.append((suitor, reviewer))

        self.blocking_pairs = blocking_pairs
        return any(blocking_pairs)
