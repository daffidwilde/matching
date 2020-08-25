""" Top-level imports for the library. """

import sys

from .game import BaseGame
from .matching import Matching
from .player import Player
from .version import __version__

if not sys.warnoptions:
    import warnings

    warnings.simplefilter("always")

__all__ = ["BaseGame", "Matching", "Player", "__version__"]
