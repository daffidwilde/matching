"""Functions for the HR algorithms."""

from .util import _delete_pair, _match_pair


def _unmatch_pair(resident, hospital):
    """Unmatch a (resident, hospital)-pair."""

    resident._unmatch()
    hospital._unmatch(resident)


def _check_available(hospital):
    """Check if a hospital is willing and able to take an applicant."""

    return len(hospital.matching) < hospital.capacity and set(
        hospital.prefs
    ).difference(hospital.matching)


def hospital_resident(residents, hospitals, optimal="resident"):
    """Solve an instance of HR using an adapted Gale-Shapley algorithm
    :cite:`Rot84`. A unique, stable and optimal matching is found for
    the given set of residents and hospitals. The optimality of the
    matching is found with respect to one party and is subsequently the
    worst stable matching for the other.

    Parameters
    ----------
    residents : list of Player
        The residents in the game. Each resident must rank a non-empty
        subset of the elements of ``hospitals``.
    hospitals : list of Hospital
        The hospitals in the game. Each hospital must rank all the
        residents that have ranked them.
    optimal : str, optional
        Which party the matching should be optimised for. Must be one of
        ``"resident"`` and ``"hospital"``. Defaults to the former.

    Returns
    -------
    matching : Matching
        A dictionary-like object where the keys are the members of
        ``hospitals``, and the values are their matches ranked by
        preference.
    """

    if optimal == "resident":
        return resident_optimal(residents, hospitals)
    if optimal == "hospital":
        return hospital_optimal(hospitals)


def resident_optimal(residents, hospitals):
    """Solve the instance of HR to be resident-optimal.

    The resident-optimal algorithm is as follows:

        0. Set all residents to be unmatched, and all hospitals to be
           totally unsubscribed.

        1. Take any unmatched resident with a non-empty preference list,
           :math:`r`, and consider their most preferred hospital,
           :math:`h`. Match them to one another.

        2. If, as a result of this new matching, :math:`h` is now
           over-subscribed, find the worst resident currently assigned
           to :math:`h`, :math:`r'`. Set :math:`r'` to be unmatched and
           remove them from :math:`h`'s matching. Otherwise, go to 3.

        3. If :math:`h` is at capacity (fully subscribed) then find
           their worst current match :math:`r'`. Then, for each
           successor, :math:`s`, to :math:`r'` in the preference list of
           :math:`h`, delete the pair :math:`(s, h)` from the game.
           Otherwise, go to 4.

        4. Go to 1 until there are no such residents left, then end.
    """

    free_residents = residents[:]
    while free_residents:
        resident = free_residents.pop()
        hospital = resident.get_favourite()

        if len(hospital.matching) == hospital.capacity:
            worst = hospital.get_worst_match()
            _unmatch_pair(worst, hospital)
            free_residents.append(worst)

        _match_pair(resident, hospital)

        if len(hospital.matching) == hospital.capacity:
            successors = hospital.get_successors()
            for successor in successors:
                _delete_pair(hospital, successor)
                if not successor.prefs and successor in free_residents:
                    free_residents.remove(successor)

    return {r: r.matching for r in hospitals}


def hospital_optimal(hospitals):
    """Solve the instance of HR to be hospital-optimal.

    The hospital-optimal algorithm is as follows:

        0. Set all residents to be unmatched, and all hospitals to be
           totally unsubscribed.

        1. Take any hospital, :math:`h`, that is under-subscribed and
           whose preference list contains any resident they are not
           currently assigned to, and consider their most preferred such
           resident, :math:`r`.

        2. If :math:`r` is currently matched, say to :math:`h'`, then
           unmatch them from one another. In any case, match :math:`r`
           to :math:`h` and go to 3.

        3. For each successor, :math:`s`, to :math:`h` in the preference
           list of :math:`r`, delete the pair :math:`(r, s)` from the
           game.

        4. Go to 1 until there are no such hospitals left, then end.
    """

    free_hospitals = hospitals[:]
    while free_hospitals:
        hospital = free_hospitals.pop()
        resident = hospital.get_favourite()

        if resident.matching:
            current_match = resident.matching
            _unmatch_pair(resident, current_match)
            if current_match not in free_hospitals:
                free_hospitals.append(current_match)

        _match_pair(resident, hospital)
        if _check_available(hospital):
            free_hospitals.append(hospital)

        successors = resident.get_successors()
        for successor in successors:
            _delete_pair(resident, successor)
            if not _check_available(successor) and successor in free_hospitals:
                free_hospitals.remove(successor)

    return {r: r.matching for r in hospitals}
