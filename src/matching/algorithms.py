""" This script contains both the standard and extended Gale-Shapley algorithms
for solving matching games.

A matching game is defined by two sets called suitors and reviewers. Each suitor
(and reviewer) has associated with it an ordered preference of the elements of
the corresponding set. A solution to a matching game is any mapping between the
set of suitors and reviewers.
"""

from collections import Counter
from copy import deepcopy

import numpy as np


def galeshapley(suitor_pref_dict, reviewer_pref_dict):
    """ The Gale-Shapley algorithm as set out in [Gale, Shapley 1962]. This
    algorithm is known to provide a unique, stable suitor-optimal matching. If a
    reviewer-optimal matching is required, then their roles can be reversed. The
    algorithm is as follows:

    1. Assign all suitors and reviewers to be unmatched.

    2. Take any unmatched suitor, s, and their most preferred reviewer, r.
        - If r is unmatched, match s to r.
        - Else, if r is matched, consider their current partner, r_partner.
         - If r prefers s to r_partner, unmatch r_partner from r and match s to
           r.
         - Else, leave s unmatched and remove r from their preference list.

    3. Go to 2 until all suitors are matched, then end.

    Parameters
    ----------
    suitor_pref_dict : dict
        A dictionary with suitors as keys and their respective preference lists
        as values
    review_pref_dict : dict
        A dictionary with reviewers as keys and their respective preference
        lists as values

    Returns
    -------
    matching : dict
        The suitor-optimal (stable) matching with suitors as keys and the
        reviewer they are matched with as values
    """
    suitors = [s for s in suitor_pref_dict]
    matching = {s: None for s in suitors}

    while suitors != []:
        s = suitors.pop(0)
        r = suitor_pref_dict[s][0]
        if r not in matching.values():
            matching[s] = r
        else:
            for suitr, revwr in matching.items():
                if revwr == r:
                    r_partner = suitr
            if reviewer_pref_dict[r].index(s) < reviewer_pref_dict[r].index(
                r_partner
            ):
                matching[r_partner] = None
                matching[s] = r
                suitors.append(r_partner)
            else:
                suitor_pref_dict[s].remove(r)
                suitors.append(s)

    return matching


def check_inputs(hospital_prefs, resident_prefs):
    """ Reduce as necessary the preference list of all residents and hospitals
    so that no player ranks another player that they are not also ranked by. """

    for resident in resident_prefs.keys():
        for hospital in resident_prefs[resident]:
            if resident not in hospital_prefs[hospital]:
                raise ValueError(
                    'Hospitals must rank all residents who rank them.'
                )


def get_free_residents(resident_prefs, matching):
    """ Return a list of all residents who are currently unmatched but have a
    non-empty preference list. """

    return [
        resident
        for resident in resident_prefs
        if resident_prefs[resident]
        and not any([resident in match for match in matching.values()])
    ]


def get_worst_idx(hospital, hospital_prefs, matching):
    """ Find the index of the worst resident currently assigned to `hospital`
    according to their preferences. """

    return max(
        [
            hospital_prefs[hospital].index(resident)
            for resident in hospital_prefs[hospital]
            if resident in matching[hospital]
        ]
    )


def hospital_resident(hospital_prefs, resident_prefs, capacities):
    """ Provide a stable, resident-optimal matching for the given instance of
    HR using the algorithm set out in [Dubins, Freeman 1981]. """

    check_inputs(hospital_prefs, resident_prefs)

    matching = {hospital: [] for hospital in hospital_prefs}
    free_residents = get_free_residents(resident_prefs, matching)
    while free_residents:
        resident = free_residents[0]
        hospital = resident_prefs[resident][0]
        matching[hospital].append(resident)

        if len(matching[hospital]) > capacities[hospital]:
            worst = get_worst_idx(hospital, hospital_prefs, matching)
            resident = hospital_prefs[hospital][worst]
            matching[hospital].remove(resident)

        if len(matching[hospital]) == capacities[hospital]:
            worst = get_worst_idx(hospital, hospital_prefs, matching)
            successors = hospital_prefs[hospital][worst + 1:]

            if successors:
                for resident in successors:
                    hospital_prefs[hospital].remove(resident)
                    if hospital in resident_prefs[resident]:
                        resident_prefs[resident].remove(hospital)

        free_residents = get_free_residents(resident_prefs, matching)

    for hospital, matches in matching.items():
        sorted_matches = sorted(matches, key=hospital_prefs[hospital].index)
        matching[hospital] = sorted_matches

    return matching


def hrt_super_res(resident_prefs, hospital_prefs, capacities):
    """ Determine whether a super-stable, resident-optimal matching exists for
    the given instance of HR. If so, return the matching. """

    # ==================================
    # Needs adjusting for ties in prefs.
    # ==================================

    matching = {h: [] for h in hospital_prefs.keys()}
    fulls = {h: False for h in hospital_prefs.keys()}
    free_residents = [r for r in resident_prefs.keys()]
    while [r for r in free_residents if resident_prefs[r]]:

        r = free_residents.pop(0)
        r_prefs = resident_prefs[r]
        h_best = r_prefs[0]
        matching[h_best] += [r]

        if len(matching[h_best]) > capacities[h_best]:
            r_worst = hospital_prefs[h_best][-1]
            if r_worst in matching[h_best]:
                matching[h_best].remove(r_worst)
            resident_prefs[r_worst].remove(h_best)
            hospital_prefs[h_best].remove(r_worst)

        if len(matching[h_best]) == capacities[h_best]:
            fulls[h_best] = True
            worst_idx = np.max(
                [
                    hospital_prefs[h_best].index(resident)
                    for resident in hospital_prefs[h_best]
                    if resident in matching[h_best]
                ]
            )

            successors = hospital_prefs[h_best][worst_idx + 1 :]
            if successors:
                for resident in successors:
                    hospital_prefs[h_best].remove(resident)
                    resident_prefs[resident].remove(h_best)

    resident_match_counts = Counter([tuple(res) for res in matching.values()])
    if np.any(
        [count > 1 for count in resident_match_counts.values()]
    ) or np.any(fulls.values()):
        raise ValueError("No super-stable matching exists.")

    return matching
