""" The core algorithm for solving capacitated matching games. """

from .util import delete_pair, match_pair, unmatch_pair


def hospitalresident(suitors, reviewers, optimal="suitor", verbose=False):
    """ Solve a capacitated matching game, i.e. an instance of the
    hospital-resident assignment problem (HR). A unique, stable and optimal
    matching is found for the given set of suitors (residents) and reviewers
    (hospitals). The optimality of the matching is with respect to one party is
    subsequently the worst stable matching for the other.

    Parameters
    ==========
    suitors : `list` of `Player` instances
        The suitors (residents) in the game. Each suitor must be a valid
        instance of the `Player` class that ranks elements of `reviewers`.
    reviewers : `list` of `Player` instances
        The reviewers (hospitals) in the game. Each reviewer must be a valid
        instance of the `Player` class that ranks elements of `reviewers`.
    optimal : `str`, optional
        Which party the matching should be optimised for. Must be one of
        `"suitor"` and `"reviewer"` (or `"resident"` and `"hospital"`
        respectively). Defaults to `"suitor"`.
    verbose : `bool`, optional
        Whether or not to log the progress of the algorithm. Default is to not.

    Returns
    =======
    matching : `dict`
        A dictionary of `Player` instances. The keys are the members of
        `reviewers`, and the values are their matches ranked by preference.
    """

    if optimal in ["suitor", "resident"]:
        return resident_optimal(suitors, reviewers, verbose)
    if optimal in ["reviewer", "hospital"]:
        return hospital_optimal(suitors, reviewers, verbose)


def get_matching(reviewers):
    """ Make a dictionary of reviewers and their final matches such that the
    matches are correctly ordered according to the reviewer's preferences. """

    return {
        r: tuple(sorted(r.match, key=lambda x: r.pref_names.index(x.name)))
        for r in reviewers
    }


def resident_optimal(suitors, reviewers, verbose):
    """ Solve the instance of HR to be suitor- (resident-) optimal. The
    algorithm (set out in `DubinsFreedman1981`_) is as follows:

        0. Set all residents to be unmatched, and all hospitals to be totally
        unsubscribed.

        1. Take any unmatched resident with a non-empty preference list,
        :math:`r`, and consider their most preferred hospital, :math:`h`. Match
        them to one another.

        2. If, as a result of this new matching, :math:`h` is now
        over-subscribed, find the worst resident currently assigned to
        :math:`h`, :math:`r'`. Set :math:`r'` to be unmatched and remove them
        from :math:`h`'s matching. Otherwise, go to 3.

        3. If :math:`h` is at capacity (fully subscribed) then find their worst
        current match :math:`r'`. Then, for each successor, :math:`s`, to
        :math:`r'` in the preference list of :math:`h`, delete the pair
        :math:`(s, h)` from the game. Otherwise, go to 4.

        4. Go to 1 until there are no such residents left, then end.
    """

    free_suitors = suitors[:]
    while free_suitors:

        suitor = free_suitors.pop()
        reviewer = suitor.get_favourite(reviewers)

        match_pair(suitor, reviewer)

        if len(reviewer.match) > reviewer.capacity:
            idx = reviewer.get_worst_match_idx()
            worst = [s for s in suitors if s.name == reviewer.pref_names[idx]][
                0
            ]
            unmatch_pair(worst, reviewer)

        if len(reviewer.match) == reviewer.capacity:
            idx = reviewer.get_worst_match_idx()
            successors = reviewer.get_successors(suitors, idx)
            for successor in successors:
                delete_pair(successor, reviewer)

        free_suitors = [s for s in suitors if not s.match and s.pref_names]

    matching = get_matching(reviewers)

    return matching


def hospital_optimal(suitors, reviewers, verbose):
    """ Solve the instance of HR to be reviewer- (hospital-) optimal. The
    algorithm (originally described in `Roth1984`_) is as follows:

        0. Set all residents to be unmatched, and all hospitals to be totally
        unsubscribed.

        1. Take any hospital, :math:`h`, that is under-subscribed and whose
        preference list contains any resident they are not currently assigned
        to, and consider their most preferred such resident, :math:`r`.

        2. If :math:`r` is currently matched, say to :math:`h'`, then unmatch
        them from one another. In any case, match :math:`r` to :math:`h` and go
        to 3.

        3. For each successor, :math:`s`, to :math:`h` in the preference list of
        :math:`r`, delete the pair :math:`(r, s)` from the game.

        4. Go to 1 until there are no such hospitals left, then end.
    """

    free_reviewers = reviewers[:]
    while free_reviewers:

        reviewer = free_reviewers.pop()
        suitor = reviewer.get_favourite(suitors)

        if suitor.match:
            curr_match = suitor.match
            unmatch_pair(curr_match, reviewer)

        match_pair(suitor, reviewer)

        successors = suitor.get_successors(reviewers)
        for successor in successors:
            delete_pair(successor, reviewer)

        free_reviewers = [
            r
            for r in reviewers
            if len(r.match) < r.capacity
            and [s for s in r.pref_names if s not in r.match]
        ]

    matching = get_matching(reviewers)

    return matching
