""" A general matchmaker class for storing all the information about a matching
game, and for solving them. """

from matching.algorithms import galeshapley, hospitalresident


class Matcher:
    """ A class to store and facilitate the solving of a matching game instance.

    Parameters
    ==========
    suitors : `list` of `Player` instances
        The suitors (applicants) in a matching game. The elements of this list
        should be valid instances of the `Player` class that each rank elements
        from `reviewers`.
    reviewers : `list` of `Player` instances
        The reviewers in a matching game. The elements of this list should be
        valid instances of the `Player` class that each rank elements from
        `suitors`.
    capacitated : `bool`, optional
        An indicator as to whether the game is should be treated as a simple or
        capacitated matching game. This is an optional parameter as it can be
        inferred (sometimes) when a reviewer has capacity greater than one.

    Attributes
    ==========
    matching : `None` or  `dict`
        Initialised to be `None`. After solving the game instance, a dictionary
        storing the final matches is given here.
    """

    def __init__(self, suitors, reviewers, capacitated=None):

        self.suitors = suitors
        self.reviewers = reviewers
        self.capacitated = (
            any([r.capacity > 1 for r in reviewers]) or capacitated
        )
        self.matching = None

    def solve(self, optimal="suitor", verbose=False):
        """ Solve the game instance and give the final matching. The algorithm
        used is determined by the `capacitated` attribute and the `optimal`
        parameter indicates which party's matches should be optimised. """

        suitors, reviewers = self.suitors, self.reviewers

        if not self.matching:
            if self.capacitated:
                self.matching = hospitalresident(
                    suitors, reviewers, optimal, verbose
                )
            else:
                self.matching = galeshapley(
                    suitors, reviewers, optimal, verbose
                )

        return self.matching
