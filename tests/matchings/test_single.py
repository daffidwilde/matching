"""Unit tests for the SingleMatching class."""

from hypothesis import given
from hypothesis import strategies as st

from matching.matchings import SingleMatching


@given(
    dictionary=st.one_of(
        st.just(None),
        st.dictionaries(st.integers(), st.integers(), min_size=2, max_size=5),
    ),
    keys=st.text(),
    values=st.text(),
    valid=st.sampled_from((None, False, True)),
    stable=st.sampled_from((None, False, True)),
)
def test_init(dictionary, keys, values, valid, stable):
    """Check that a SingleMatching can be created correctly."""

    matching = SingleMatching(
        dictionary, keys=keys, values=values, valid=valid, stable=stable
    )

    assert isinstance(matching, SingleMatching)
    assert isinstance(matching, dict)

    dictionary = dictionary or {}
    assert matching.items() == dictionary.items()
    assert vars(matching) == {
        "keys_": keys, "values_": values, "valid": valid, "stable": stable
    }
