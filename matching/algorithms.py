""" 
This script contains both the standard and extended Gale-Shapley algorithms for 
solving matching games. 

A matching game is defined by two sets called suitors and reviewers. Each suitor
(and reviewer) has associated with it an ordered preference of the elements of
the corresponding set. A solution to a matching game is any mapping between the
set of suitors and reviewers.

"""

from copy import deepcopy
import numpy as np


def galeshapley(suitor_pref_dict, reviewer_pref_dict):
    """The Gale-Shapley algorithm. This is known to provide a unique, stable
    suitor-optimal matching. The algorithm is as follows:

    (1) Assign all suitors and reviewers to be unmatched.

    (2) Take any unmatched suitor, s, and their most preferred reviewer, r.
            - If r is unmatched, match s to r.
            - If r is matched, consider their current partner, r_partner.
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
            if reviewer_pref_dict[r].index(s) < 
            reviewer_pref_dict[r].index(r_partner):
                matching[r_partner] = None
                matching[s] = r
                suitors.append(r_partner)
            else:
                suitor_pref_dict[s].remove(r)
                suitors.append(s)

    return matching

