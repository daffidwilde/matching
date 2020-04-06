""" The base game class for facilitating and solving matching games. """

import abc

class BaseGame(metaclass=abc.ABCMeta):
    """ An abstract base class for facilitating various matching games.

    Attributes
    ----------
    _matching : None
        Initialised to be :code:`None`. After solving the game,
        a :code:`Matching` object is found here. Not used -- instead, use the
        :code:`Game.matching` property.
    blocking_pairs : None
        Initialised to be :code:`None`. After solving and checking the stability
        of the game instance, a list of any pairs that block the stability of
        the matching.
    """

    def __init__(self):

        self._matching = None
        self.blocking_pairs = None

    @property
    def matching(self):
        """ Property method to stop direct write access. """

        return self._matching

    @matching.getter
    def matching(self):
        """ Property method to stop direct write access. """

        return self._matching

    @abc.abstractmethod
    def solve(self):
        """ Placeholder for solving the given matching game. """

    @abc.abstractmethod
    def check_stability(self):
        """ Placeholder for checking the stability of the current matching. """

    @abc.abstractmethod
    def check_validity(self):
        """ Placeholder for checking the validity of the current matching. """
