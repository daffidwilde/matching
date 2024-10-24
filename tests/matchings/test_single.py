"""Unit tests for the SingleMatching class."""

from hypothesis import given
from hypothesis import strategies as st

from matching.matchings import SingleMatching


@st.composite
def st_single_params(draw, min_size=2, max_size=5):
    """Create a parameter set for a SingleMatching instance."""

    size = draw(st.integers(min_size, max_size))
    midpoint = size // 2
    players = list(range(size))
    keys, values = players[:midpoint], players[midpoint:]
    dictionary = draw(st.sampled_from((None, dict(zip(keys, values)))))

    keys = draw(st.text())
    values = draw(st.text())
    valid = draw(st.sampled_from((None, False, True)))
    stable = draw(st.sampled_from((None, False, True)))

    params = dict(
        dictionary=dictionary,
        keys=keys,
        values=values,
        valid=valid,
        stable=stable,
    )

    return params


@st.composite
def st_singles(draw, min_size=2, max_size=5):
    """Create a SingleMatching instance."""

    params = draw(st_single_params(min_size, max_size))

    return SingleMatching(**params)


@given(st_single_params())
def test_init(params):
    """Check that a SingleMatching can be created correctly."""

    matching = SingleMatching(**params)

    assert isinstance(matching, SingleMatching)
    assert isinstance(matching, dict)

    dictionary = params["dictionary"] or {}
    assert matching.items() == dictionary.items()
    assert vars(matching) == {
        "keys_": params["keys"],
        "values_": params["values"],
        "valid": params["valid"],
        "stable": params["stable"],
    }


@given(st_singles())
def test_repr(matching):
    """Check that the string representation of a matching is correct."""

    repr_ = repr(matching)

    assert isinstance(repr_, str)
    assert repr_.startswith("SingleMatching")
    assert str(dict(matching)) in repr_
    assert matching.keys_ in repr_
    assert matching.values_ in repr_


@given(st_single_params())
def test_eq(params):
    """Check the equivalence dunder works as expected."""

    matching1 = SingleMatching(**params)
    matching2 = SingleMatching(**params)

    assert matching1 == matching2

    if params["dictionary"] is not None:
        key = next(iter(params["dictionary"].keys()))
        matching2[key] = None

        assert matching1 != matching2
        assert vars(matching1) == vars(matching2)


@given(st_singles())
def test_invert(matching):
    """Check the matching inverter works as it should."""

    inverted = matching.invert()

    assert isinstance(inverted, SingleMatching)
    assert set(inverted.items()) == set(
        (val, key) for key, val in matching.items()
    )
    assert inverted.keys_ == matching.values_
    assert inverted.values_ == matching.keys_
    assert inverted.valid == matching.valid
    assert inverted.stable == matching.stable
