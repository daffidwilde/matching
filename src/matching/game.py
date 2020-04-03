""" The base game class for facilitating and solving matching games. """


class Game:
    """ A class to store information about, and facilitate the solving of, a
    matching game.

    **This is a base class and is not intended for use other than inheritance.**

    Attributes
    ----------
    matching : None
        Initialised to be :code:`None`. After solving the game,
        a :code:`Matching` object is found here.
    blocking_pairs : None
        Initialised to be :code:`None`. After solving and checking the stability
        of the game instance, a list of any pairs that block the stability of
        the matching.
    """

    def __init__(self):

        self.matching = None
        self.blocking_pairs = None

    def solve(self):
        """ Placeholder for solving the given matching game. """

        raise NotImplementedError()

    def check_stability(self):
        """ Placeholder for checking the stability of the current matching. """

        raise NotImplementedError()

    def check_validity(self):
        """ Placeholder for checking the validity of the current matching. """

        raise NotImplementedError()
