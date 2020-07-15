""" Top-level imports for the library. """

import sys

if not sys.warnoptions:
    import warnings

    warnings.simplefilter("always")

from .base import BaseGame, BaseMatching, BasePlayer
from .matchings import MultipleMatching, SingleMatching
from .players import Player
from .version import __version__

__all__ = [
    "BaseGame",
    "BaseMatching",
    "BasePlayer",
    "Matching",
    "MultipleMatching",
    "Player",
    "SingleMatching",
    "__version__",
]
