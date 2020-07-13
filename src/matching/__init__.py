""" Top-level imports for the library. """

import sys

if not sys.warnoptions:
    import warnings

    warnings.simplefilter("always")

from .game import BaseGame
from .matching import Matching
from .player import Player
from .version import __version__

__all__ = [BaseGame, Matching, Player, __version__]
