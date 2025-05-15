"""Top-level imports for the `matching.games` subpackage."""

from .hospital_resident import HospitalResident
from .stable_marriage import StableMarriage
from .stable_roommates import StableRoommates
from .student_project import StudentProject

__all__ = [
    "HospitalResident",
    "StableMarriage",
    "StableRoommates",
    "StudentProject",
]
