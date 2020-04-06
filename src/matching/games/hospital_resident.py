""" The HR solver and algorithm. """

import copy

from matching import BaseGame, Matching
from matching import Player as Resident
from matching.players import Hospital

from .util import delete_pair, match_pair


class HospitalResident(BaseGame):
    """ A class for solving instances of the hospital-resident assignment
    problem (HR).

    In this case, a blocking pair is any resident-hospital pair that satisfies
    **all** of the following:

        - They are present in each other's preference lists;
        - either the resident is unmatched, or they prefer the hospital to their
          current match;
        - either the hospital is under-subscribed, or they prefer the resident
          to at least one of their current matches.

    Parameters
    ----------
    residents : list of Player
        The residents in the matching game. Each resident must rank a subset of
        those in :code:`hospitals`.
    hospitals : list of Hospital
        The hospitals in the matching game. Each hospital must rank all of (and
        only) the residents which rank it.

    Attributes
    ----------
    matching : Matching or None
        Once the game is solved, a matching is available as a :code:`Matching`
        object with the hospitals as keys and their resident matches as values.
        Initialises as :code:`None`.
    blocking_pairs : list of (Player, Hospital) or None
        Initialises as `None`. Otherwise, a list of the resident-hospital
        blocking pairs.
    """

    def __init__(self, residents, hospitals):

        residents, hospitals = copy.deepcopy([residents, hospitals])
        self.residents = residents
        self.hospitals = hospitals

        super().__init__()
        self._check_inputs()

    @classmethod
    def create_from_dictionaries(
        cls, resident_prefs, hospital_prefs, capacities
    ):
        """ Create an instance of :code:`HospitalResident` from two preference
        dictionaries and capacities. """

        residents, hospitals = _make_players(
            resident_prefs, hospital_prefs, capacities
        )
        game = cls(residents, hospitals)

        return game

    def solve(self, optimal="resident"):
        """ Solve the instance of HR using either the resident- or
        hospital-oriented algorithm. Return the matching. """

        self.matching = Matching(
            hospital_resident(self.residents, self.hospitals, optimal)
        )
        return self.matching

    def check_validity(self):
        """ Check whether the current matching is valid. """

        self._check_resident_matching()
        self._check_hospital_capacity()
        self._check_hospital_matching()

        return True

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

    def _check_resident_matching(self):
        """ Check that no resident is matched to an unacceptable hospital. """

        errors = []
        for resident in self.residents:
            if (
                resident.matching is not None
                and resident.matching not in resident.prefs
            ):
                errors.append(
                    ValueError(
                        f"{resident} is matched to {resident.matching} but "
                        "they do not appear in their preference list: "
                        f"{resident.prefs}."
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
                if resident not in hospital.prefs:
                    errors.append(
                        ValueError(
                            f"{hospital} has {resident} in their matching but "
                            "they do not appear in their preference list: "
                            f"{hospital.prefs}."
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
        for resident in self.residents:
            if not set(resident.prefs).issubset(set(self.hospitals)):
                errors.append(
                    ValueError(
                        f"{resident} has ranked a non-hospital: "
                        f"{set(resident.prefs)} != {set(self.hospitals)}"
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
            residents_that_ranked = [
                res for res in self.residents if hospital in res.prefs
            ]
            if set(hospital.prefs) != set(residents_that_ranked):
                errors.append(
                    ValueError(
                        f"{hospital} has not ranked all the residents that "
                        f"ranked it: {set(hospital.prefs)} != "
                        f"{set(residents_that_ranked)}."
                    )
                )

        if errors:
            raise Exception(*errors)

        return True


def _check_mutual_preference(resident, hospital):
    """ Determine whether two players each have a preference of the other. """

    return resident in hospital.prefs and hospital in resident.prefs


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


def unmatch_pair(resident, hospital):
    """ Unmatch a (resident, hospital)-pair. """

    resident.unmatch()
    hospital.unmatch(resident)


def hospital_resident(residents, hospitals, optimal="resident"):
    """ Solve an instance of HR using an adapted Gale-Shapley algorithm
    :cite:`Rot84`. A unique, stable and optimal matching is found for the given
    set of residents and hospitals. The optimality of the matching is found with
    respect to one party and is subsequently the worst stable matching for the
    other.

    Parameters
    ----------
    residents : list of Player
        The residents in the game. Each resident must rank a non-empty subset
        of the elements of ``hospitals``.
    hospitals : list of Hospital
        The hospitals in the game. Each hospital must rank all the residents
        that have ranked them.
    optimal : str, optional
        Which party the matching should be optimised for. Must be one of
        ``"resident"`` and ``"hospital"``. Defaults to the former.

    Returns
    -------
    matching : Matching
        A dictionary-like object where the keys are the members of
        ``hospitals``, and the values are their matches ranked by preference.
    """

    if optimal == "resident":
        return resident_optimal(residents, hospitals)
    if optimal == "hospital":
        return hospital_optimal(hospitals)


def resident_optimal(residents, hospitals):
    """ Solve the instance of HR to be resident-optimal. The algorithm is as
    follows:

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

    free_residents = residents[:]
    while free_residents:

        resident = free_residents.pop()
        hospital = resident.get_favourite()

        match_pair(resident, hospital)

        if len(hospital.matching) > hospital.capacity:
            worst = hospital.get_worst_match()
            unmatch_pair(worst, hospital)
            free_residents.append(worst)

        if len(hospital.matching) == hospital.capacity:
            successors = hospital.get_successors()
            for successor in successors:
                delete_pair(hospital, successor)
                if not successor.prefs:
                    free_residents.remove(successor)

    return {r: r.matching for r in hospitals}


def hospital_optimal(hospitals):
    """ Solve the instance of HR to be hospital-optimal. The algorithm is as
    follows:

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
        resident = hospital.get_favourite()

        if resident.matching:
            curr_match = resident.matching
            unmatch_pair(resident, curr_match)
            if curr_match not in free_hospitals:
                free_hospitals.append(curr_match)

        match_pair(resident, hospital)
        if len(hospital.matching) < hospital.capacity and [
            res for res in hospital.prefs if res not in hospital.matching
        ]:
            free_hospitals.append(hospital)

        successors = resident.get_successors()
        for successor in successors:
            delete_pair(resident, successor)
            if (
                not [
                    res
                    for res in successor.prefs
                    if res not in successor.matching
                ]
                and successor in free_hospitals
            ):
                free_hospitals.remove(successor)

    return {r: r.matching for r in hospitals}


def _make_players(resident_prefs, hospital_prefs, capacities):
    """ Make a set of residents and hospitals from the dictionaries given, and
    add their preferences. """

    resident_dict, hospital_dict = _make_instances(
        resident_prefs, hospital_prefs, capacities
    )

    for resident_name, resident in resident_dict.items():
        prefs = [hospital_dict[name] for name in resident_prefs[resident_name]]
        resident.set_prefs(prefs)

    for hospital_name, hospital in hospital_dict.items():
        prefs = [resident_dict[name] for name in hospital_prefs[hospital_name]]
        hospital.set_prefs(prefs)

    residents = list(resident_dict.values())
    hospitals = list(hospital_dict.values())

    return residents, hospitals


def _make_instances(resident_prefs, hospital_prefs, capacities):
    """ Create ``Player`` (resident) and ``Hospital`` instances for the names in
    each dictionary. """

    resident_dict, hospital_dict = {}, {}
    for resident_name in resident_prefs:
        resident = Resident(name=resident_name)
        resident_dict[resident_name] = resident
    for hospital_name in hospital_prefs:
        capacity = capacities[hospital_name]
        hospital = Hospital(name=hospital_name, capacity=capacity)
        hospital_dict[hospital_name] = hospital

    return resident_dict, hospital_dict
