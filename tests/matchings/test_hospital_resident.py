"""Tests for the `HRMatching` class."""

from hypothesis import given
from hypothesis import strategies as st

from matching import matchings

from ..common import st_sizes


@st.composite
def st_params(draw, hmin=1, hmax=3, rmin=1, rmax=5):
    """Create a parameter set for a HRMatching instance."""
    hsize = draw(st_sizes(hmin, hmax))
    rsize = draw(st_sizes(rmin, rmax))
    capacities = draw(st.lists(st.integers(1, 2), min_size=hsize, max_size=hsize))

    matched_residents = draw(st.lists(st.integers(0, rsize - 1), unique=True))
    if not matched_residents:
        matching = None
    else:
        resident_matching = {}
        for resident in matched_residents:
            hospital = draw(st.integers(0, hsize - 1))
            if capacities[hospital]:
                resident_matching[resident] = hospital
                capacities[hospital] -= 1

        matching = {
            hospital: [r for r in resident_matching if resident_matching[r] == hospital]
            for hospital in range(hsize)
            if hospital in resident_matching.values()
        }

    params = dict(
        dictionary=matching, keys=draw(st.text(min_size=1)), values=draw(st.text(min_size=1))
    )

    return params


@st.composite
def st_matchings(draw, hmin=1, hmax=3, rmin=1, rmax=5):
    """Create a HRMatching instance."""
    params = draw(st_params(hmin, hmax, rmin, rmax))

    return matchings.HRMatching(**params)


@given(st_params())
def test_init(params):
    """Check that a HRMatching can be created correctly."""
    matching = matchings.HRMatching(**params)

    assert isinstance(matching, matchings.HRMatching)
    assert isinstance(matching, dict)

    dictionary = params["dictionary"] or {}
    assert matching.items() == dictionary.items()
    assert vars(matching) == {"keys_": params["keys"], "values_": params["values"]}


@given(st_matchings())
def test_repr(matching):
    """Check that the string representation of a matching is correct."""
    repr_ = repr(matching)

    assert isinstance(repr_, str)
    assert repr_.startswith("HRMatching")
    assert str(dict(matching)) in repr_
    assert matching.keys_ in repr_
    assert matching.values_ in repr_


@given(st_params())
def test_eq(params):
    """Check that two HRMatchings are equal."""
    matching1 = matchings.HRMatching(**params)
    matching2 = matchings.HRMatching(**params)

    assert matching1 == matching2
    assert matching1 is not matching2

    if params["dictionary"] is not None:
        key = next(iter(params["dictionary"].keys()))
        matching2[key] = None

        assert matching1 != matching2
        assert vars(matching1) == vars(matching2)


@given(st_matchings())
def test_invert(matching):
    """Check that the invert method works correctly."""
    inverted = matching.invert()

    assert isinstance(inverted, matchings.HRMatching)
    assert inverted.keys_ == matching.values_
    assert inverted.values_ == matching.keys_

    for key, values in matching.items():
        for value in values:
            assert inverted[value] == [key]
