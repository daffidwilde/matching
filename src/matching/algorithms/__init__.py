"""Top-level imports for the `matching.algorithms` subpackage."""

from .hospital_resident import hospital_resident
from .stable_marriage import stable_marriage
from .stable_roommates import stable_roommates
from .student_allocation import student_allocation

__all__ = [
    "hospital_resident",
    "stable_marriage",
    "stable_roommates",
    "student_allocation",
]
