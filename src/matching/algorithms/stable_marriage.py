"""Functions for the SM algorithms."""

from .util import _delete_pair, _match_pair


def _unmatch_pair(suitor, reviewer):
    """Unmatch a (suitor, reviewer) pair."""

    suitor._unmatch()
    reviewer._unmatch()


def stable_marriage(suitors, reviewers, optimal="suitor"):
    """An extended version of the original Gale-Shapley algorithm.

    This version makes use of the inherent structures of SM instances. A
    unique, stable and optimal matching is found for any valid set of
    suitors and reviewers. The optimality of the matching is with
    respect to one party and is subsequently the worst stable matching
    for the other.

    Parameters
    ----------
    suitors : list of Player
        The suitors in the game. Each must rank all of those in
        ``reviewers``.
    reviewers : list of Player
        The reviewers in the game. Each must rank all of those in
        ``suitors``.
    optimal : str, optional
        Which party the matching should be optimised for. Must be one of
        ``"suitor"`` and ``"reviewer"``. Defaults to the former.

    Returns
    -------
    matching : Matching
        A dictionary-like object where the keys are given by the members of
        ``suitors``, and the values are their match in ``reviewers``.
    """

    if optimal.lower() == "reviewer":
        suitors, reviewers = reviewers, suitors

    free_suitors = suitors[:]
    while free_suitors:
        suitor = free_suitors.pop()
        reviewer = suitor.get_favourite()

        if reviewer.matching:
            current_match = reviewer.matching
            _unmatch_pair(current_match, reviewer)
            free_suitors.append(current_match)

        _match_pair(suitor, reviewer)

        successors = reviewer.get_successors()
        for successor in successors:
            _delete_pair(successor, reviewer)

    if optimal.lower() == "reviewer":
        suitors, reviewers = reviewers, suitors

    return {s: s.matching for s in suitors}
