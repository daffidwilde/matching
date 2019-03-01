""" The Hospital-Resident Assignment Problem solver and core algorithm. """

from matching import Game, Matching

from .util import delete_pair, match_pair, unmatch_pair


class HospitalResident(Game):
    """ A class for solving instances of the Hospital-Resident Assignment
    Problem (HR) using an adapted Gale-Shapley algorithm.

    Parameters
    ==========
    residents : `list` of `Player` instances
        The residents (residents) in the matching game. Each resident must rank
        a subset of the names in `hospitals`.
    hospitals : `list` of `Player` instances
        The hospitals (hospitals) in the matching game. Each hospital must rank
        all of (and only) the names of the residents which rank it.

    Attributes
    ==========
    matching : `Matching` (`dict`-like)
        Once the game is solved, a matching is available as a `Matching` object.
        This resembles and behaves much like a standard Python dictionary that
        uses the hospitals as keys and their resident matches as values.
        Initialises as `None`.
    blocking_pairs : `list` of (`resident`, `hospital`)-tuples
        The resident-hospital pairs that satisfy the following conditions:
            - They are present in each other's preference lists;
            - either the resident is unmatched, or they prefer the hospital to
              their current match;
            - either the hospital is under-subscribed, or they prefer the
              resident to at least one of their current matches.
        Such pairs are said to 'block' the matching. Initialises as `None`.
    """

    def __init__(self, residents, hospitals):

        for resident in residents:
            resident.matching = None
        for hospital in hospitals:
            hospital.matching = []

        self.residents = residents
        self.hospitals = hospitals

        self._check_inputs()

        super().__init__()

    def solve(self, optimal="resident"):
        """ Solve the instance of HR using either the resident- (resident-) or
        hospital- (hospital-) oriented algorithm. Return the matching. """

        self._matching = Matching(
            hospital_resident(self.residents, self.hospitals, optimal)
        )
        return self.matching

    def check_stability(self):
        """ Check for the existence of any blocking pairs in the current
        matching, thus determining the stability of the matching. """

        blocking_pairs = []
        for resident in self.residents:
            for hospital in self.hospitals:
                if (
                    _check_mutual_preference(resident, hospital)
                    and _check_resident_unhappy(resident, hospital)
                    and _check_hospital_unhappy(resident, hospital)
                ):
                    blocking_pairs.append((resident, hospital))

        self.blocking_pairs = blocking_pairs
        return not any(blocking_pairs)

    def check_validity(self):
        """ Check whether the current matching is valid. """

        self._check_resident_matching()
        self._check_hospital_capacity()
        self._check_hospital_matching()

        return True

    def _check_resident_matching(self):
        """ Check that no resident is matched to an unacceptable hospital. """

        errors = []
        for resident in self.residents:
            if (
                resident.matching
                and resident.matching.name not in resident.pref_names
            ):
                errors.append(
                    ValueError(
                        f"{resident} is matched to {resident.matching} but "
                        "they do not appear in their preference list: "
                        f"{resident.pref_names}."
                    )
                )

        if errors:
            raise Exception(*errors)

        return True

    def _check_hospital_capacity(self):
        """ Check that no hospital is over-subscribed. """

        errors = []
        for hospital in self.hospitals:
            if len(hospital.matching) > hospital.capacity:
                errors.append(
                    ValueError(
                        f"{hospital} is matched to {hospital.matching} which "
                        f"is over their capacity of {hospital.capacity}."
                    )
                )

        if errors:
            raise Exception(*errors)

        return True

    def _check_hospital_matching(self):
        """ Check that no hospital is matched to an unacceptable resident. """

        errors = []
        for hospital in self.hospitals:
            for resident in hospital.matching:
                if resident.name not in hospital.pref_names:
                    errors.append(
                        ValueError(
                            f"{hospital} has {resident} in their matching but "
                            "they do not appear in their preference list: "
                            f"{hospital.pref_names}."
                        )
                    )

        if errors:
            raise Exception(*errors)

        return True

    def _check_inputs(self):
        """ Raise an error if any of the conditions of the game have been
        broken. """

        self._check_resident_prefs()
        self._check_hospital_prefs()

    def _check_resident_prefs(self):
        """ Make sure that the residents' preferences are all subsets of the
        available hospital names. Otherwise, raise an error. """

        errors = []
        hospital_names = [r.name for r in self.hospitals]
        for resident in self.residents:
            if not set(resident.pref_names).issubset(set(hospital_names)):
                errors.append(
                    ValueError(
                        f"{resident} has ranked a non-hospital: "
                        f"{set(resident.pref_names)} != {set(hospital_names)}"
                    )
                )

        if errors:
            raise Exception(*errors)

        return True

    def _check_hospital_prefs(self):
        """ Make sure that every hospital ranks all and only those residents
        that have ranked it. Otherwise, raise an error. """

        errors = []
        for hospital in self.hospitals:
            residents_that_ranked_names = [
                s.name for s in self.residents if hospital.name in s.pref_names
            ]
            if set(hospital.pref_names) != set(residents_that_ranked_names):
                errors.append(
                    ValueError(
                        f"{hospital} has not ranked all the residents that "
                        f"ranked it: {set(hospital.pref_names)} != "
                        f"{set(residents_that_ranked_names)}."
                    )
                )

        if errors:
            raise Exception(*errors)

        return True


def _check_mutual_preference(resident, hospital):
    """ Determine whether two players each have a preference of the other. """

    return (
        resident.name in hospital.pref_names
        and hospital.name in resident.pref_names
    )


def _check_resident_unhappy(resident, hospital):
    """ Determine whether a resident is unhappy because they are unmatched, or
    they prefer the hospital to their current match. """

    return resident.matching is None or resident.prefers(
        hospital, resident.matching
    )


def _check_hospital_unhappy(resident, hospital):
    """ Determine whether a hospital is unhappy because they are
    under-subscribed, or they prefer the resident to at least one of their 
    current matches. """

    return len(hospital.matching) < hospital.capacity or any(
        [hospital.prefers(resident, match) for match in hospital.matching]
    )


def hospital_resident(residents, hospitals, optimal="resident", verbose=False):
    """ Solve an instance of HR matching game by treating it as a stable
    marriage game with hospital capacities. A unique, stable and optimal
    matching is found for the given set of residents (residents) and hospitals
    (hospitals). The optimality of the matching is found with respect to one
    party and is subsequently the worst stable matching for the other.

    Parameters
    ==========
    residents : `list` of `Player` instances
        The residents in the game. Each resident must rank the names of a subset
        of the elements of `hospitals`.
    hospitals : `list` of `Player` instances
        The hospitals in the game. Each hospital must all the names of those
        elements of `hospitals` that rank them.
    optimal : `str`, optional
        Which party the matching should be optimised for. Must be one of
        `"resident"` and `"hospital"` (or `"resident"` and `"hospital"`
        respectively). Defaults to `"resident"`.
    verbose : `bool`, optional
        Whether or not to log the progress of the algorithm. Default is to not.

    Returns
    =======
    matching : `Matching` (`dict`-like)
        A dictionary-like object of `Player` instances. The keys are the members
        of `hospitals`, and the values are their matches ranked by preference.
    """

    if optimal in ["resident", "resident"]:
        return resident_optimal(residents, hospitals, verbose)
    if optimal in ["hospital", "hospital"]:
        return hospital_optimal(residents, hospitals, verbose)


def resident_optimal(residents, hospitals, verbose):
    """ Solve the instance of HR to be resident- (resident-) optimal. The
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

    free_residents = residents[:]
    while free_residents:

        resident = free_residents.pop()
        hospital = resident.get_favourite(hospitals)

        match_pair(resident, hospital)

        if len(reviewer.matching) > reviewer.capacity:
            worst = reviewer.get_worst_match()
            unmatch_pair(worst, reviewer)
            free_suitors.append(worst)

        if len(reviewer.matching) == reviewer.capacity:
            successors = reviewer.get_successors(suitors)
            for successor in successors:
                delete_pair(reviewer, successor)
                if not successor.pref_names:
                    free_suitors.remove(successor)

    return {r: r.matching for r in hospitals}


def hospital_optimal(residents, hospitals, verbose):
    """ Solve the instance of HR to be hospital- (hospital-) optimal. The
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

    free_hospitals = hospitals[:]
    while free_hospitals:

        hospital = free_hospitals.pop()
        resident = hospital.get_favourite(residents)

        if suitor.matching:
            curr_match = suitor.matching
            unmatch_pair(suitor, curr_match)
            if curr_match not in free_reviewers:
                free_reviewers.append(curr_match)

        match_pair(suitor, reviewer)
        reviewer_match_names = [m.name for m in reviewer.matching]
        if len(reviewer.matching) < reviewer.capacity and [
            name
            for name in reviewer.pref_names
            if name not in reviewer_match_names
        ]:
            free_reviewers.append(reviewer)

        successors = resident.get_successors(hospitals)
        for successor in successors:
            delete_pair(suitor, successor)
            successor_match_names = [m.name for m in successor.matching]
            if (
                not [
                    name
                    for name in successor.pref_names
                    if name not in successor_match_names
                ]
                and successor in free_reviewers
            ):
                free_reviewers.remove(successor)

    return {r: r.matching for r in hospitals}
