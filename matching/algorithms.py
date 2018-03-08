""" This script contains both the standard and extended Gale-Shapley algorithms
for solving matching games.

A matching game is defined by two sets called suitors and reviewers. Each suitor
(and reviewer) has associated with it an ordered preference of the elements of
the corresponding set. A solution to a matching game is any mapping between the
set of suitors and reviewers.
"""

import numpy as np


def galeshapley(suitor_pref_dict, reviewer_pref_dict):
    """ The Gale-Shapley algorithm. This is known to provide a unique, stable
    suitor-optimal matching. The algorithm is as follows:

    (1) Assign all suitors and reviewers to be unmatched.

    (2) Take any unmatched suitor, s, and their most preferred reviewer, r.
            - If r is unmatched, match s to r.
            - Else, if r is matched, consider their current partner, r_partner.
                - If r prefers s to r_partner, unmatch r_partner from r and 
                  match s to r.
                - Else, leave s unmatched and remove r from their preference
                  list.
    (3) Go to (2) until all suitors are matched, then end.

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
            if reviewer_pref_dict[r].index(s) \
               < reviewer_pref_dict[r].index(r_partner):
                matching[r_partner] = None
                matching[s] = r
                suitors.append(r_partner)
            else:
                suitor_pref_dict[s].remove(r)
                suitors.append(s)

    return matching


def extended_galeshapley(suitor_preferences, reviewer_preferences, capacities):
    """ The extended Gale-Shapley algorithm for solving a capacitated matching
    game. This implementation of the algorithm is based on that used by the NRMP
    to solve the hospital-resident assignment problem.

    The algorithm is as follows:

    (1) Assign all suitors and reviewers to be unmatched.

    (2) Take any unmatched suitor up for consideration, s.
            - If their preference list is empty, remove them from consideration 
              and go to (2).)
            - Otherwise, consider their most preferred reviewer, r.
            - If r currently has space for another suitor, match s to r.
            - Otherwise, if r has no space currently:
                - For each suitor currently matched to r, r_match:
                    - If r prefers s to r_match and s is not yet matched to r,
                      unmatch r_match from r and match r to s.
                    - Otherwise, remove r from s's preference list and leave s
                      unmatched.

    (3) Go to (2) until there are no unmatched candidates up for consideration,
        then end.
        
    NB: This implementation requires all reviewers to have ranked all suitors,
        but not the other way around. That is, some suitors may end up without
        any matches.

    Parameters
    ----------
    suitor_pref_dict : dict
        A dictionary with suitors as keys and their respective preference lists
        as values
    review_pref_dict : dict
        A dictionary with reviewers as keys and their respective preference
        lists as values
    capacities : dict
        A dictionary with reviewers as keys and their capacities as values

    Returns
    -------
    matching : dict
        A stable matching with reviewers as keys and lists of suitors as values
    """
    free_suitors = list(suitor_preferences.keys())
    suitor_matching = {s: None for s in suitor_preferences.keys()}
    reviewer_matching = {r: [] for r in reviewer_preferences.keys()}

    while free_suitors:
        s = free_suitors.pop(0)
        s_prefs = suitor_preferences[s]
        while (not suitor_matching[s]) & (s_prefs != []):
            if s not in reviewer_preferences[s_prefs[0]]:
                s_prefs.remove(s_prefs[0])
            if s_prefs != []:
                r = s_prefs[0]
                r_prefs = reviewer_preferences[r]
                r_matches = reviewer_matching[r]
                if len(r_matches) < capacities[r]:
                    suitor_matching[s] = r
                    reviewer_matching[r] += [s]
                else:
                    s_idx = r_prefs.index(s)
                    worst_idx = np.max([r_prefs.index(s_curr) \
                                        for s_curr in r_prefs \
                                        if s_curr in r_matches])
                    worst_match = r_prefs[worst_idx]
                    if s_idx < worst_idx:
                        suitor_matching[worst_match] = None
                        r_matches.remove(worst_match)
                        suitor_preferences[worst_match].remove(r)
                        free_suitors.append(worst_match)

                        suitor_matching[s] = r
                        r_matches += [s]
                    else:
                        r_prefs.remove(s)
                        s_prefs.remove(r)

    for reviewer, matches in reviewer_matching.items():
        reviewer_pref = reviewer_preferences[reviewer]
        sorted_matches = sorted(matches, key=lambda x: reviewer_pref.index(x))
        reviewer_matching[reviewer] = sorted_matches

    return suitor_matching, reviewer_matching
