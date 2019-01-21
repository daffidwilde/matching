""" The Hospital-Resident Assignment Problem solver and core algorithm. """

from matching import BaseSolver, Matching

from .util import delete_pair, match_pair, unmatch_pair


class HospitalResident(BaseSolver):
    """ A class for solving instances of the Hospital-Resident Assignment
    Problem (HR) using an adapted Gale-Shapley algorithm.

    Parameters
    ==========
    suitors : `list` of `Player` instances
        The suitors (residents) in the matching game. Each suitor must rank a
        subset of the names in `reviewers`.
    reviewers : `list` of `Player` instances
        The reviewers (hospitals) in the matching game. Each reviewer must rank
        all of (and only) the names of the suitors which rank it.

    Attributes
    ==========
    matching : `Matching` (`dict`-like)
        Once the game is solved, a matching is available as a `Matching` object.
        This resembles and behaves much like a standard Python dictionary that
        uses the reviewers as keys and their suitor matches as values.
        Initialises as `None`.
    blocking_pairs : `list` of (`suitor`, `reviewer`)-tuples
        The suitor-reviewer pairs that satisfy the following conditions:
            - They are present in each other's preference lists;
            - either the suitor is unmatched, or they prefer the reviewer to
              their current match;
            - either the reviewer is under-subscribed, or they prefer the suitor
              to at least one of their current matches.
        Such pairs are said to 'block' the matching. Initialises as `None`.
    """

    def __init__(self, suitors, reviewers):

        for suitor in suitors:
            suitor.matching = None
        for reviewer in reviewers:
            reviewer.matching = []

        self.suitors = suitors
        self.reviewers = reviewers

        self._check_inputs()

        super().__init__(suitors, reviewers)

    def solve(self, optimal="resident"):
        """ Solve the instance of HR using either the resident- (suitor-) or
        hospital- (reviewer-) oriented algorithm. Return the matching. """

        self._matching = Matching(
            hospital_resident(self.suitors, self.reviewers, optimal)
        )
        return self.matching

    def check_stability(self):
        """ Check for the existence of any blocking pairs in the current
        matching, thus determining the stability of the matching. """

        blocking_pairs = []
        for suitor in self.suitors:
            for reviewer in self.reviewers:
                if (
                    _check_mutual_preference(suitor, reviewer)
                    and _check_suitor_unhappy(suitor, reviewer)
                    and _check_reviewer_unhappy(suitor, reviewer)
                ):
                    blocking_pairs.append((suitor, reviewer))

        self.blocking_pairs = blocking_pairs
        return not any(blocking_pairs)

    def check_validity(self):
        """ Check whether the current matching is valid. """

        errors = []
        for reviewer in self.reviewers:
            if len(reviewer.matching) > reviewer.capacity:
                errors.append(
                    ValueError(
                        f"{reviewer} is over their capacity of "
                        f"{reviewer.capacity}."
                    )
                )

        if errors:
            raise Exception(errors)

        return True

    def _check_inputs(self):
        """ Raise an error if any of the conditions of the game have been
        broken. """

        self._check_suitor_prefs()
        self._check_reviewer_prefs()

    def _check_suitor_prefs(self):
        """ Make sure that the suitors' preferences are all subsets of the
        available reviewer names. Otherwise, raise an error. """

        errors = []
        reviewer_names = [r.name for r in self.reviewers]
        for suitor in self.suitors:
            if not set(suitor.pref_names).issubset(set(reviewer_names)):
                errors.append(
                    ValueError(
                        f"{suitor} has ranked a non-reviewer: "
                        f"{set(suitor.pref_names)} != {set(reviewer_names)}"
                    )
                )

        if errors:
            raise Exception(errors)

        return True

    def _check_reviewer_prefs(self):
        """ Make sure that every reviewer ranks all and only those suitors that
        have ranked it. Otherwise, raise an error. """

        errors = []
        for reviewer in self.reviewers:
            suitors_that_ranked_names = [
                s.name for s in self.suitors if reviewer.name in s.pref_names
            ]
            if set(reviewer.pref_names) != set(suitors_that_ranked_names):
                errors.append(
                    ValueError(
                        f"{reviewer} has not ranked all the suitors that ranked"
                        f" it: {set(reviewer.pref_names)} != "
                        f"{set(suitors_that_ranked_names)}."
                    )
                )

        if errors:
            raise Exception(errors)

        return True


def _check_mutual_preference(suitor, reviewer):
    """ Determine whether two players each have a preference of the other. """

    return (
        suitor.name in reviewer.pref_names
        and reviewer.name in suitor.pref_names
    )


def _check_suitor_unhappy(suitor, reviewer):
    """ Determine whether a suitor is unhappy because they are unmatched, or
    they prefer the reviewer to their current match. """

    return suitor.matching is None or suitor.prefers(reviewer, suitor.matching)


def _check_reviewer_unhappy(suitor, reviewer):
    """ Determine whether a reviewer is unhappy because they are
    under-subscribed, or they prefer the suitor to at least one of their current
    matches. """

    return len(reviewer.matching) < reviewer.capacity or any(
        [reviewer.prefers(suitor, match) for match in reviewer.matching]
    )


def hospital_resident(suitors, reviewers, optimal="suitor", verbose=False):
    """ Solve an instance of HR matching game by treating it as a stable
    marriage game with reviewer capacities. A unique, stable and optimal
    matching is found for the given set of suitors (residents) and reviewers
    (hospitals). The optimality of the matching is found with respect to one
    party and is subsequently the worst stable matching for the other.

    Parameters
    ==========
    suitors : `list` of `Player` instances
        The suitors (residents) in the game. Each suitor must rank the names of
        a subset of the elements of `reviewers`.
    reviewers : `list` of `Player` instances
        The reviewers (hospitals) in the game. Each reviewer must all the names
        of those elements of `reviewers` that rank them.
    optimal : `str`, optional
        Which party the matching should be optimised for. Must be one of
        `"suitor"` and `"reviewer"` (or `"resident"` and `"hospital"`
        respectively). Defaults to `"suitor"`.
    verbose : `bool`, optional
        Whether or not to log the progress of the algorithm. Default is to not.

    Returns
    =======
    matching : `Matching` (`dict`-like)
        A dictionary-like object of `Player` instances. The keys are the members
        of `reviewers`, and the values are their matches ranked by preference.
    """

    if optimal in ["suitor", "resident"]:
        return resident_optimal(suitors, reviewers, verbose)
    if optimal in ["reviewer", "hospital"]:
        return hospital_optimal(suitors, reviewers, verbose)


def resident_optimal(suitors, reviewers, verbose):
    """ Solve the instance of HR to be suitor- (resident-) optimal. The
    algorithm (set out in `DubinsFreedman1981`_) is as follows:

        0. Set all residents to be unmatched, and all hospitals to be totally
        unsubscribed.

        1. Take any unmatched resident with a non-empty preference list,
        :math:`r`, and consider their most preferred hospital, :math:`h`. Match
        them to one another.

        2. If, as a result of this new matching, :math:`h` is now
        over-subscribed, find the worst res)dent currently assigned to
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

        if len(reviewer.matching) > reviewer.capacity:
            idx = reviewer.get_worst_match_idx()
            worst = [s for s in suitors if s.name == reviewer.pref_names[idx]][
                0
            ]
            unmatch_pair(worst, reviewer)

        if len(reviewer.matching) == reviewer.capacity:
            idx = reviewer.get_worst_match_idx()
            successors = reviewer.get_successors(suitors, idx)
            for successor in successors:
                delete_pair(reviewer, successor)

        free_suitors = [s for s in suitors if not s.matching and s.pref_names]

    return {r: r.matching for r in reviewers}


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

        if suitor.matching:
            curr_match = suitor.matching
            unmatch_pair(suitor, curr_match)

        match_pair(suitor, reviewer)

        successors = suitor.get_successors(reviewers)
        for successor in successors:
            delete_pair(suitor, successor)

        free_reviewers = [
            r
            for r in reviewers
            if len(r.matching) < r.capacity
            and [
                s for s in r.pref_names if s not in [m.name for m in r.matching]
            ]
        ]

    return {r: r.matching for r in reviewers}
