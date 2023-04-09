"""Top-level imports for the library."""

import sys

if not sys.warnoptions:
    import warnings

    warnings.simplefilter("always")

from .base import BaseGame, BaseMatching, BasePlayer
from .matchings import MultipleMatching, SingleMatching
from .players import Player

__all__ = [
    "BaseGame",
    "BaseMatching",
    "BasePlayer",
    "Matching",
    "MultipleMatching",
    "Player",
    "SingleMatching",
]
