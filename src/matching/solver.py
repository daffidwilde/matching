""" The base matchmaker class for facilitating and solving matching games. """

from .matching import Matching

class BaseSolver:
    """ A class to store information about, and facilitate the solving of, a
    matching game.

    This is a base class and is not intended for uses other than inheritance.

    Parameters
    ==========
    suitors : `list` of `Player` instances
        The suitors (applicants) in a matching game.
    reviewers : `list` of `Player` instances
        The reviewers in a matching game.

    Attributes
    ==========
    matching : `None`
        Initialised to be `None`. After solving the game instance, a dictionary
        storing the final matches is given here.
    blocking_pairs : `None`.
        Initialised to be `None`. After solving and checking the stability of
        the game instance, a list of any pairs that block the stability of the
        matching.
    """

    def __init__(self, suitors=None, reviewers=None):

        self.suitors = suitors
        self.reviewers = reviewers

        self._matching = None
        self.blocking_pairs = None

    @property
    def matching(self):
        """ Property method to stop direct write access. """

        return Matching(self._matching)

    @matching.getter
    def matching(self):
        """ Property getter. """

        return Matching(self._matching)

    def solve(self):
        """ Placeholder for solving the given matching game. """

        raise NotImplementedError()

    def check_stability(self):
        """ Placeholder for checking the stability of the current matching. """

        raise NotImplementedError()

    def check_validity(self):
        """ Placeholder for checking the validity of the current matching. """

        raise NotImplementedError()
