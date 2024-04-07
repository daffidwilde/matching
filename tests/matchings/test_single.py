"""Unit tests for the SingleMatching class."""

from hypothesis import given
from hypothesis import strategies as st

from matching.matchings import SingleMatching


@st.composite
def st_single_params(draw, min_size=2, max_size=5):
    """Create a parameter set for a SingleMatching instance."""

    dictionary = draw(
        st.one_of(
            st.just(None),
            st.dictionaries(
                st.integers(), st.integers(), min_size=2, max_size=5
            ),
        )
    )
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
    assert str(matching.keys_) in repr_
    assert str(matching.values_) in repr_
