"""The SM game class and supporting functions."""

import copy

from matching import BaseGame, Player, SingleMatching
from matching.algorithms import stable_marriage
from matching.exceptions import MatchingError


class StableMarriage(BaseGame):
    """Solver for the stable marriage problem (SM).

    Parameters
    ----------
    suitors : list of Player
        The suitors in the game. Each suitor must rank all elements in
        ``reviewers``.
    reviewers : list of Player
        The reviewers in the game. Each reviewer must rank all elements
        in ``suitors``.

    Attributes
    ----------
    matching : SingleMatching or None
        Once the game is solved, a matching is available. This uses the
        suitors and reviewers as keys and values, respectively, in a
        ``SingleMatching`` object. Initialises as ``None``.
    blocking_pairs : list of (Player, Player)
        The suitor-reviewer pairs that both prefer one another to their
        current match. Initialises as ``None``.
    """

    def __init__(self, suitors, reviewers):
        suitors, reviewers = copy.deepcopy([suitors, reviewers])
        self.suitors = suitors
        self.reviewers = reviewers

        super().__init__()
        self.check_inputs()

    @classmethod
    def create_from_dictionaries(cls, suitor_prefs, reviewer_prefs):
        """Create an instance of SM from two preference dictionaries."""

        suitors, reviewers = _make_players(suitor_prefs, reviewer_prefs)
        game = cls(suitors, reviewers)

        return game

    def solve(self, optimal="suitor"):
        """Solve the instance of SM. Return the matching.

        The party optimality can be controlled using the ``optimal``
        parameter.
        """

        self.matching = SingleMatching(
            stable_marriage(self.suitors, self.reviewers, optimal)
        )
        return self.matching

    def check_validity(self):
        """Check whether the current matching is valid."""

        unmatched_issues = self._check_for_unmatched_players()
        not_in_matching_issues = self._check_for_players_not_in_matching()
        inconsistency_issues = self._check_for_inconsistent_matches()

        if unmatched_issues or not_in_matching_issues or inconsistency_issues:
            raise MatchingError(
                unmatched_players=unmatched_issues,
                players_not_in_matching=not_in_matching_issues,
                inconsistent_matches=inconsistency_issues,
            )

        return True

    def check_stability(self):
        """Check for the existence of any blocking pairs."""

        blocking_pairs = []
        for suitor in self.suitors:
            for reviewer in self.reviewers:
                if suitor.prefers(
                    reviewer, suitor.matching
                ) and reviewer.prefers(suitor, reviewer.matching):
                    blocking_pairs.append((suitor, reviewer))

        self.blocking_pairs = blocking_pairs
        return not any(blocking_pairs)

    def _check_for_unmatched_players(self):
        """Check everyone has a match."""

        issues = []
        for player in self.suitors + self.reviewers:
            issue = player.check_if_match_is_unacceptable(unmatched_okay=False)
            if issue:
                issues.append(issue)

        return issues

    def _check_for_players_not_in_matching(self):
        """Check that everyone appears in the matching."""

        players_in_matching = set(self.matching.keys()) | set(
            self.matching.values()
        )

        issues = []
        for player in self.suitors + self.reviewers:
            if player not in players_in_matching:
                issues.append(f"{player} does not appear in matching.")

        return issues

    def _check_for_inconsistent_matches(self):
        """Check the matching is consistent with the players'."""

        issues = []
        for suitor, reviewer in self.matching.items():
            if suitor.matching != reviewer:
                issues.append(
                    f"{suitor} is matched to {suitor.matching} but the "
                    f"matching says they should be matched to {reviewer}."
                )

        return issues

    def check_inputs(self):
        """Raise an error if any of the game's rules do not hold."""

        self._check_num_players()
        for suitor in self.suitors:
            self._check_player_ranks(suitor)
        for reviewer in self.reviewers:
            self._check_player_ranks(reviewer)

    def _check_num_players(self):
        """Check that the number of suitors and reviewers are equal."""

        if len(self.suitors) != len(self.reviewers):
            raise ValueError(
                "There must be an equal number of suitors and reviewers."
            )

        return True

    def _check_player_ranks(self, player):
        """Check that a player has ranked all of the other group."""

        others = self.reviewers if player in self.suitors else self.suitors
        if set(player.prefs) != set(others):
            raise ValueError(
                "Every player must rank each name from the other group. "
                f"{player}: {player.prefs} != {others}"
            )

        return True


def _make_players(suitor_prefs, reviewer_prefs):
    """Make a set of suitors and reviewers from two dictionaries."""

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
    """Create ``Player`` instances for the names in each dictionary."""

    suitor_dict, reviewer_dict = {}, {}
    for suitor_name in suitor_prefs:
        suitor = Player(name=suitor_name)
        suitor_dict[suitor_name] = suitor
    for reviewer_name in reviewer_prefs:
        reviewer = Player(name=reviewer_name)
        reviewer_dict[reviewer_name] = reviewer

    return suitor_dict, reviewer_dict
