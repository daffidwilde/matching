"""Tests for the BaseMatching class."""

import pytest
from hypothesis import given
from hypothesis.strategies import dictionaries, text

from matching import BaseMatching

DICTIONARIES = given(
    dictionary=dictionaries(
        keys=text(),
        values=text(),
        min_size=1,
        max_size=3,
    )
)


@DICTIONARIES
def test_init(dictionary):
    """Make a matching and check their attributes are correct."""

    matching = BaseMatching()
    assert matching == {}

    matching = BaseMatching(dictionary)
    assert matching == dictionary


@DICTIONARIES
def test_repr(dictionary):
    """Check that a matching is represented by a normal dictionary."""

    matching = BaseMatching()
    assert repr(matching) == "{}"

    matching = BaseMatching(dictionary)
    assert repr(matching) == str(dictionary)


@DICTIONARIES
def test_keys(dictionary):
    """Check a matching can have its `keys` accessed."""

    matching = BaseMatching()
    assert list(matching.keys()) == []

    matching = BaseMatching(dictionary)
    assert list(matching.keys()) == list(dictionary.keys())


@DICTIONARIES
def test_values(dictionary):
    """Check a matching can have its `values` accessed."""

    matching = BaseMatching()
    assert list(matching.values()) == []

    matching = BaseMatching(dictionary)
    assert list(matching.values()) == list(dictionary.values())


@DICTIONARIES
def test_getitem(dictionary):
    """Check that you can access items in a matching correctly."""

    matching = BaseMatching(dictionary)
    for (mkey, mval), (dkey, dval) in zip(
        matching.items(), dictionary.items()
    ):
        assert matching[mkey] == mval
        assert (mkey, mval) == (dkey, dval)


@DICTIONARIES
def test_setitem_check_player_in_keys(dictionary):
    """Check for error when adding a new item to a matching."""

    key = list(dictionary.keys())[0]
    matching = BaseMatching(dictionary)
    assert matching._check_player_in_keys(key) is None

    with pytest.raises(ValueError):
        matching._check_player_in_keys(key + "foo")


@DICTIONARIES
def test_setitem_check_new_valid_type(dictionary):
    """Check for error if a new match is not one of correct type."""

    val = list(dictionary.values())[0]
    matching = BaseMatching(dictionary)
    assert matching._check_new_valid_type(val, str) is None

    with pytest.raises(ValueError):
        matching._check_new_valid_type(val, float)
