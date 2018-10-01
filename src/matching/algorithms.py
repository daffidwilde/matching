""" .. This script contains both the standard and extended Gale-Shapley
.. algorithms for solving matching games.

.. A matching game is defined by two sets called suitors and reviewers. Each
.. suitor (and reviewer) has associated with it an ordered preference of the
.. elements of the corresponding set. A solution to a matching game is any
.. mapping between the set of suitors and reviewers.
"""

def stable_marriage(suitor_prefs, reviewer_prefs, optimal='suitor'):
    """ Set out in [Gale, Shapley 1962] and commonly known as the
    Extended Gale-Shapley algorithm, this algorithm is known to provide a
    unique, stable, suitor-optimal matching to any instance of the stable
    marriage problem. If a reviewer-optimal matching is required, then the roles
    of suitors and reviewers should be reversed. The algorithm is as follows:

        1. Assign all suitors and reviewers to be unmatched.

        2. Take any unmatched suitor, :math:`s`, and their most preferred
           reviewer, :math:`r`.

        3. If :math:`r` is matched to some suitor :math:`s^*`:

             - Assign :math:`s^*` to be unmatched.

        4. Assign :math:`s` to be matched to :math:`r`.

        5. For each successor, :math:`s'`, to :math:`s` in the preference list
           of :math:`r`:

             - Remove :math:`r` from the preference list of :math:`s'`, and
               vice versa.

        6. Go to 2 until all suitors are matched, then end.

    Parameters
    ----------
    suitor_prefs : dict
        A dictionary with suitors as keys and their respective preference lists
        as values.
    review_prefs : dict
        A dictionary with reviewers as keys and their respective preference
        lists as values.
    optimal : str
        An indicator for which party the matching should be optimal. Defaults to
        :code:`'suitor'` but can also be :code:`'reviewer'`.

    Returns
    -------
    matching : dict
        The stable matching with the optimal party members as keys and the
        players they are matched with as values.
    """
    if optimal == 'reviewer':
        suitor_prefs, reviewer_prefs = reviewer_prefs, suitor_prefs

    suitors = [s for s in suitor_prefs]
    matching = {s: None for s in suitors}

    while suitors:
        suitor = suitors.pop(0)
        reviewer = suitor_prefs[suitor][0]

        if reviewer in matching.values():
            idx = list(matching.values()).index(reviewer)
            current_partner = list(matching.keys())[idx]
            matching[current_partner] = None
            suitors.append(current_partner)

        matching[suitor] = reviewer

        idx = reviewer_prefs[reviewer].index(suitor)
        successors = reviewer_prefs[reviewer][idx + 1:]
        if successors:
            for successor in successors:
                reviewer_prefs[reviewer].remove(successor)
                suitor_prefs[successor].remove(reviewer)

    return matching


def _check_inputs(hospital_prefs, resident_prefs):
    """ Reduce as necessary the preference list of all residents and hospitals
    so that no player ranks another player that they are not also ranked by. """

    for resident in resident_prefs.keys():
        for hospital in resident_prefs[resident]:
            if resident not in hospital_prefs[hospital]:
                raise ValueError(
                    'Hospitals must rank all residents who rank them.'
                )


def _get_free_residents(resident_prefs, matching):
    """ Return a list of all residents who are currently unmatched but have a
    non-empty preference list. """

    return [
        resident
        for resident in resident_prefs
        if resident_prefs[resident]
        and not any([resident in match for match in matching.values()])
    ]


def _get_worst_idx(hospital, hospital_prefs, matching):
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
    HR using the algorithm set out in [Dubins, Freeman 1981]. The algorithm is
    as follows:

        1. Assign all hospitals and residents to be unmatched.

        2. Take some unmatched resident, :math:`r`, with a non-empty preference
           list, and consider their most preferred hospital, :math:`h`.

        3. Add :math:`r` to :math:`h`'s matching.

        4. If :math:`h` is over-subscribed:

            - Find :math:`h`'s worst currently matched resident, :math:`r^*`.
            - Remove :math:`r^*` from :math:`h`'s matching and assign them to be
              unmatched.

        5. If :math:`h` is now at capacity:

            - Find :math:`h`'s worst currently matched resident, :math:`r^*`.
            - For each successor, :math:`r'`, to :math:`r^*` in the preference
              list of :math:`h`:

                - Remove :math:`h` from the preference list of :math:`r'`, and
                  vice versa.

        6. Go to 2 until there are no residents left to be considered, then end.

    Parameters
    ----------
    hospital_prefs : dict
        A dictionary with hospitals as keys and their associated preference
        lists as values.
    resident_prefs : dict
        A dictionary with residents as keys and their associated preference
        lists as values.
    capacities : dict
        A dictionary of hospitals and their associated capacities.

    Returns
    -------
    matching : dict
        A stable, resident-optimal matching where each hospital's matches are
        ordered with respect to their preference lists.
    """

    _check_inputs(hospital_prefs, resident_prefs)

    matching = {hospital: [] for hospital in hospital_prefs}
    free_residents = _get_free_residents(resident_prefs, matching)
    while free_residents:
        resident = free_residents[0]
        hospital = resident_prefs[resident][0]
        matching[hospital].append(resident)

        if len(matching[hospital]) > capacities[hospital]:
            worst = _get_worst_idx(hospital, hospital_prefs, matching)
            resident = hospital_prefs[hospital][worst]
            matching[hospital].remove(resident)

        if len(matching[hospital]) == capacities[hospital]:
            worst = _get_worst_idx(hospital, hospital_prefs, matching)
            successors = hospital_prefs[hospital][worst + 1:]

            if successors:
                for resident in successors:
                    hospital_prefs[hospital].remove(resident)
                    if hospital in resident_prefs[resident]:
                        resident_prefs[resident].remove(hospital)

        free_residents = _get_free_residents(resident_prefs, matching)

    for hospital, matches in matching.items():
        sorted_matches = sorted(matches, key=hospital_prefs[hospital].index)
        matching[hospital] = sorted_matches

    return matching
