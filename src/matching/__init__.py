"""Top-level imports for the library."""

import sys

if not sys.warnoptions:
    import warnings

    warnings.simplefilter("always")

from .base import BaseGame, BaseMatching, BasePlayer
from .matchings import MultipleMatching, SingleMatching
from .players import Hospital, Player, Project, Supervisor

__version__ = "1.4.3"

__all__ = [
    "BaseGame",
    "BaseMatching",
    "BasePlayer",
    "Hospital",
    "Matching",
    "MultipleMatching",
    "Player",
    "Project",
    "SingleMatching",
    "Supervisor",
    "__version__",
]
