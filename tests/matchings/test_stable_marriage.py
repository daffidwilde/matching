"""Tests for the `SMMatching` class."""

from hypothesis import given
from hypothesis import strategies as st

from matching import matchings

from ..common import st_sizes


@st.composite
def st_params(draw, min_size=2, max_size=5):
    """Create a parameter set for a SMMatching instance."""
    size = draw(st_sizes(min_size, max_size))
    midpoint = size // 2
    players = list(range(size))
    keys, values = players[:midpoint], players[midpoint:]
    dictionary = draw(st.sampled_from((None, dict(zip(keys, values)))))

    keys = draw(st.text(min_size=1))
    values = draw(st.text(min_size=1))

    params = dict(dictionary=dictionary, keys=keys, values=values)

    return params


@st.composite
def st_matchings(draw, min_size=2, max_size=5):
    """Create a SMMatching instance."""
    params = draw(st_params(min_size, max_size))

    return matchings.SMMatching(**params)


@given(st_params())
def test_init(params):
    """Check that a SMMatching can be created correctly."""
    matching = matchings.SMMatching(**params)

    assert isinstance(matching, matchings.SMMatching)
    assert isinstance(matching, dict)

    dictionary = params["dictionary"] or {}
    assert matching.items() == dictionary.items()
    assert vars(matching) == {"keys_": params["keys"], "values_": params["values"]}


@given(st_matchings())
def test_repr(matching):
    """Check that the string representation of a matching is correct."""
    repr_ = repr(matching)

    assert isinstance(repr_, str)
    assert repr_.startswith("SMMatching")
    assert str(dict(matching)) in repr_
    assert matching.keys_ in repr_
    assert matching.values_ in repr_


@given(st_params())
def test_eq(params):
    """Check the equivalence dunder works as expected."""
    matching1 = matchings.SMMatching(**params)
    matching2 = matchings.SMMatching(**params)

    assert matching1 == matching2
    assert matching1 is not matching2

    if params["dictionary"] is not None:
        key = next(iter(params["dictionary"].keys()))
        matching2[key] = None

        assert matching1 != matching2
        assert vars(matching1) == vars(matching2)


@given(st_matchings())
def test_invert(matching):
    """Check the matching inverter works as it should."""
    inverted = matching.invert()

    assert isinstance(inverted, matchings.SMMatching)
    assert set(inverted.items()) == set((val, key) for key, val in matching.items())
    assert inverted.keys_ == matching.values_
    assert inverted.values_ == matching.keys_
