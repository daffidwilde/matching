""" The core algorithm for solving simple matching games. """

from .util import delete_pair, match_pair, unmatch_pair


def galeshapley(suitors, reviewers, optimal="suitor", verbose=False):
    """ An extended version of the original Gale-Shapley algorithm which makes
    use of the inherent structures of matching games. A unique, stable and
    optimal matching is found for any set of suitors and reviewers. The
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

    free_suitors = [s for s in suitors if not s.match]
    while free_suitors:

        suitor = free_suitors.pop()
        reviewer = suitor.get_favourite(reviewers)

        if reviewer.match:
            curr_match = reviewer.match
            unmatch_pair(curr_match, reviewer)
            free_suitors.append(curr_match)

        match_pair(suitor, reviewer)

        successors = reviewer.get_successors(suitors)
        for successor in successors:
            delete_pair(successor, reviewer)

    if optimal.lower() == "reviewer":
        suitors, reviewers = reviewers, suitors

    return {s: s.match for s in suitors}
