""" Hypothesis decorators for HR tests. """

from hypothesis import given
from hypothesis.strategies import dictionaries, integers, lists, sampled_from


HOSPITAL_RESIDENT = given(
    resident_names=lists(
        elements=sampled_from(["A", "B", "C", "D"]),
        min_size=1,
        max_size=4,
        unique=True,
    ),
    hospital_names=lists(
        elements=sampled_from(["X", "Y", "Z"]),
        min_size=1,
        max_size=3,
        unique=True,
    ),
    capacities=dictionaries(
        keys=sampled_from(["X", "Y", "Z"]),
        values=integers(min_value=2),
        min_size=3,
        max_size=3,
    ),
    seed=integers(min_value=0),
)
