"""Top-level imports for the library."""

import sys

if not sys.warnoptions:
    import warnings

    warnings.simplefilter("always")

from . import matchings
from .base import BaseGame, BaseMatching, BasePlayer
from .matchings import _MultipleMatching as MultipleMatching
from .matchings import _SingleMatching as SingleMatching
from .players import Hospital, Player, Project, Supervisor

__version__ = "2.0.0"

__all__ = [
    "BaseGame",
    "BaseMatching",
    "BasePlayer",
    "Hospital",
    "MultipleMatching",
    "Player",
    "Project",
    "SingleMatching",
    "Supervisor",
    "__version__",
    "matchings",
]
