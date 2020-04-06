""" The SM solver and algorithm. """

import copy

from matching import BaseGame, Matching, Player

from .util import delete_pair, match_pair


class StableMarriage(BaseGame):
    """ A class for solving instances of the stable marriage problem (SM).

    Parameters
    ----------
    suitors : list of Player
        The suitors in the game. Each suitor must rank all elements in
        ``reviewers``.
    reviewers : list of Player
        The reviewers in the game. Each reviewer must rank all elements in
        ``suitors``.

    Attributes
    ----------
    matching : Matching or None
        Once the game is solved, a matching is available. This uses the suitors
        and reviewers as keys and values, respectively, in a ``Matching``
        object. Initialises as `None`.
    blocking_pairs : list of (Player, Player)
        The suitor-reviewer pairs that both prefer one another to their current
        match. Initialises as ``None``.
    """

    def __init__(self, suitors, reviewers):

        suitors, reviewers = copy.deepcopy([suitors, reviewers])
        self.suitors = suitors
        self.reviewers = reviewers

        super().__init__()
        self._check_inputs()

    @classmethod
    def create_from_dictionaries(cls, suitor_prefs, reviewer_prefs):
        """ Create an instance of SM from two preference dictionaries. """

        suitors, reviewers = _make_players(suitor_prefs, reviewer_prefs)
        game = cls(suitors, reviewers)

        return game

    def solve(self, optimal="suitor"):
        """ Solve the instance of SM using either the suitor- or
        reviewer-oriented Gale-Shapley algorithm. Return the matching. """

        self.matching = Matching(
            stable_marriage(self.suitors, self.reviewers, optimal)
        )
        return self.matching

    def check_stability(self):
        """ Check for the existence of any blocking pairs in the current
        matching, thus determining the stability of the matching. """

        blocking_pairs = []
        for suitor in self.suitors:
            for reviewer in self.reviewers:
                if suitor.prefers(
                    reviewer, suitor.matching
                ) and reviewer.prefers(suitor, reviewer.matching):
                    blocking_pairs.append((suitor, reviewer))

        self.blocking_pairs = blocking_pairs
        return not any(blocking_pairs)

    def check_validity(self):
        """ Check whether the current matching is valid. """

        self._check_all_matched()
        self._check_matching_consistent()
        return True

    def _check_all_matched(self):
        """ Check everyone has a match. """

        errors = []
        for player in self.suitors + self.reviewers:
            if player.matching is None:
                errors.append(ValueError(f"{player} is unmatched."))
            if player not in list(self.matching.keys()) + list(
                self.matching.values()
            ):
                errors.append(
                    ValueError(f"{player} does not appear in matching.")
                )

        if errors:
            raise Exception(*errors)

        return True

    def _check_matching_consistent(self):
        """ Check that the game matching is consistent with the players. """

        errors = []
        matching = self.matching
        for suitor in self.suitors:
            if suitor.matching != matching[suitor]:
                errors.append(
                    ValueError(
                        f"{suitor} is matched to {suitor.matching} but matching"
                        f" says {matching[suitor]}."
                    )
                )

        for reviewer in self.reviewers:
            suitor = [s for s in matching if matching[s] == reviewer][0]
            if reviewer.matching != suitor:
                errors.append(
                    ValueError(
                        f"{reviewer} is matched to {reviewer.matching} but "
                        f"matching says {suitor}."
                    )
                )

        if errors:
            raise Exception(*errors)

        return True

    def _check_inputs(self):
        """ Raise an error if any of the conditions of the game have been
        broken. """

        self._check_num_players()
        for suitor in self.suitors:
            self._check_player_ranks(suitor)
        for reviewer in self.reviewers:
            self._check_player_ranks(reviewer)

    def _check_num_players(self):
        """ Check that the number of suitors and reviewers are equal. """

        if len(self.suitors) != len(self.reviewers):
            raise ValueError(
                "There must be an equal number of suitors and reviewers."
            )

        return True

    def _check_player_ranks(self, player):
        """ Check that a player has ranked all of the other group. """

        others = self.reviewers if player in self.suitors else self.suitors
        if set(player.prefs) != set(others):
            raise ValueError(
                "Every player must rank each name from the other group. "
                f"{player}: {player.prefs} != {others}"
            )

        return True


def unmatch_pair(suitor, reviewer):
    """ Unmatch a (suitor, reviewer) pair. """

    suitor.unmatch()
    reviewer.unmatch()


def stable_marriage(suitors, reviewers, optimal="suitor"):
    """ An extended version of the original Gale-Shapley algorithm which makes
    use of the inherent structures of SM instances. A unique, stable and optimal
    matching is found for any valid set of suitors and reviewers. The optimality
    of the matching is with respect to one party and is subsequently the worst
    stable matching for the other.

    Parameters
    ----------
    suitors : list of Player
        The suitors in the game. Each must rank all of those in ``reviewers``.
    reviewers : list of Player
        The reviewers in the game. Each must rank all of those in ``suitors``.
    optimal : str, optional
        Which party the matching should be optimised for. Must be one of
        ``"suitor"`` and ``"reviewer"``. Defaults to the former.

    Returns
    -------
    matching : Matching
        A dictionary-like object where the keys are given by the members of
        ``suitors``, and the values are their match in ``reviewers``.
    """

    if optimal.lower() == "reviewer":
        suitors, reviewers = reviewers, suitors

    free_suitors = [s for s in suitors if not s.matching]
    while free_suitors:

        suitor = free_suitors.pop()
        reviewer = suitor.get_favourite()

        if reviewer.matching:
            curr_match = reviewer.matching
            unmatch_pair(curr_match, reviewer)
            free_suitors.append(curr_match)

        match_pair(suitor, reviewer)

        successors = reviewer.get_successors()
        for successor in successors:
            delete_pair(successor, reviewer)

    if optimal.lower() == "reviewer":
        suitors, reviewers = reviewers, suitors

    return {s: s.matching for s in suitors}


def _make_players(suitor_prefs, reviewer_prefs):
    """ Make a set of ``Player`` instances each for suitors and reviewers from
    the dictionaries given. Add their preferences. """

    suitor_dict, reviewer_dict = _make_instances(suitor_prefs, reviewer_prefs)

    for suitor_name, suitor in suitor_dict.items():
        prefs = [reviewer_dict[name] for name in suitor_prefs[suitor_name]]
        suitor.set_prefs(prefs)

    for reviewer_name, reviewer in reviewer_dict.items():
        prefs = [suitor_dict[name] for name in reviewer_prefs[reviewer_name]]
        reviewer.set_prefs(prefs)

    suitors = list(suitor_dict.values())
    reviewers = list(reviewer_dict.values())

    return suitors, reviewers


def _make_instances(suitor_prefs, reviewer_prefs):
    """ Create ``Player`` instances for the names in each dictionary. """

    suitor_dict, reviewer_dict = {}, {}
    for suitor_name in suitor_prefs:
        suitor = Player(name=suitor_name)
        suitor_dict[suitor_name] = suitor
    for reviewer_name in reviewer_prefs:
        reviewer = Player(name=reviewer_name)
        reviewer_dict[reviewer_name] = reviewer

    return suitor_dict, reviewer_dict
