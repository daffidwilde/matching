""" All the core algorithms for solving matching game instances. """


def unmatch_pair(suitor, reviewer):
    """ Unmatch the players given by `suitor` and `reviewer`. """

    suitor.match = None

    try:
        reviewer.match.remove(suitor)
    except AttributeError:
        reviewer.match = None


def match_pair(suitor, reviewer):
    """ Match the players given by `suitor` and `reviewer`. """

    suitor.match = reviewer

    try:
        reviewer.match.append(suitor)
    except AttributeError:
        reviewer.match = suitor


def delete_pair(successor, reviewer):
    """ Make the players `successor` and `reviewer` forget one another,
    effectively 'deleting' the pair from the game. """

    successor.forget(reviewer)
    reviewer.forget(successor)


def galeshapley(suitors, reviewers, optimal="suitor", verbose=False):

    if optimal.lower() == "reviewer":
        suitors, reviewers = reviewers, suitors

    free_suitors = [s for s in suitors if not s.match]
    while free_suitors:

        suitor = free_suitors.pop()
        reviewer = suitor.get_favourite(reviewers)

        if reviewer.match:
            curr_match = reviewer.match
            unmatch_pair(curr_match, reviewer)
            free_suitors.append(curr_match)

        match_pair(suitor, reviewer)

        successors = reviewer.get_successors(suitors)
        for successor in successors:
            delete_pair(successor, reviewer)

    if optimal.lower() in ["r", "reviewer"]:
        suitors, reviewers = reviewers, suitors

    return {s: s.match for s in suitors}


def hospitalresident(suitors, reviewers, optimal="suitor", verbose=False):
    """ Solve a standard capacitated matching game, i.e. an instance of the
    hospital-resident assignment problem (HR). """

    if optimal == "suitor":
        return resident_optimal(suitors, reviewers, verbose)
    if optimal == "reviewer":
        return hospital_optimal(suitors, reviewers, verbose)


def get_matching(reviewers):
    """ Make a dictionary of reviewers and their final matches such that the
    matches are correctly ordered according to the reviewer's preferences. """

    return {
        r: tuple(
            sorted(
                r.match, key=lambda x: r.pref_names.index(x.name)
            )
        )
        for r in reviewers
    }


def resident_optimal(suitors, reviewers, verbose):
    """ Solve the instance of HR to be suitor- (resident-) optimal. """

    free_suitors = suitors[:]
    while free_suitors:

        suitor = free_suitors.pop()
        reviewer = suitor.get_favourite(reviewers)

        match_pair(suitor, reviewer)

        if len(reviewer.match) > reviewer.capacity:
            idx = reviewer.get_worst_match_idx()
            worst = [
                s for s in suitors
                if s.name == reviewer.pref_names[idx]
            ][0]
            unmatch_pair(worst, reviewer)

        if len(reviewer.match) == reviewer.capacity:
            idx = reviewer.get_worst_match_idx()
            successors = reviewer.get_successors(suitors, idx)
            for successor in successors:
                delete_pair(reviewer, successor)

        free_suitors = [
            s for s in suitors if not s.match and s.pref_names
        ]

    matching = get_matching(reviewers)

    return matching


def hospital_optimal(suitors, reviewers, verbose):
    """ Solve the instance of HR to be reviewer- (hospital-) optimal. """

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
            delete_pair(reviewer, successor)

        free_reviewers = [
            r for r in reviewers
            if len(r.match) < r.capacity
            and [s for s in r.pref_names if s not in r.match]
        ]

    matching = get_matching(reviewers)

    return matching
