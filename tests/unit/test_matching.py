""" Unit tests for the Matching class. """

import pytest

from matching import Matching, Player

suitors = [Player("A"), Player("B"), Player("C")]
reviewers = [Player(1), Player(2), Player(3)]

suitors[0].set_prefs(reviewers)
suitors[1].set_prefs([reviewers[1], reviewers[0], reviewers[2]])
suitors[2].set_prefs([reviewers[0], reviewers[2], reviewers[1]])

reviewers[0].set_prefs([suitors[1], suitors[0], suitors[2]])
reviewers[1].set_prefs([suitors[1], suitors[0], suitors[2]])
reviewers[2].set_prefs(suitors)

dictionary = dict(zip(suitors, reviewers))


def test_init():
    """ Make an instance of the Matching class and check their attributes are
    correct. """

    matching = Matching()
    assert matching == {}

    matching = Matching(dictionary)
    assert matching == dictionary


def test_repr():
    """ Check that a Matching is represented by a normal dictionary. """

    matching = Matching()
    assert repr(matching) == "{}"

    matching = Matching(dictionary)
    assert repr(matching) == str(dictionary)


def test_keys():
    """ Check a Matching can have its `keys` accessed. """

    matching = Matching()
    assert list(matching.keys()) == []

    matching = Matching(dictionary)
    assert list(matching.keys()) == suitors


def test_values():
    """ Check a Matching can have its `values` accessed. """

    matching = Matching()
    assert list(matching.values()) == []

    matching = Matching(dictionary)
    assert list(matching.values()) == reviewers


def test_getitem():
    """ Check that you can access items in a Matching correctly. """

    matching = Matching(dictionary)
    for key, val in matching.items():
        assert matching[key] == val


def test_setitem_key_error():
    """ Check that a ValueError is raised if trying to add a new item to a
    Matching. """

    matching = Matching(dictionary)

    with pytest.raises(ValueError):
        matching["foo"] = "bar"


def test_setitem_single():
    """ Check that a key in Matching can have its value changed to another
    Player instance. """

    matching = Matching(dictionary)
    suitor, reviewer = suitors[0], reviewers[-1]

    matching[suitor] = reviewer
    assert matching[suitor] == reviewer
    assert suitor.matching == reviewer
    assert reviewer.matching == suitor


def test_setitem_none():
    """ Check can set item in Matching to be None. """

    matching = Matching(dictionary)
    suitor = suitors[0]

    matching[suitor] = None
    assert matching[suitor] is None
    assert suitor.matching is None


def test_setitem_multiple():
    """ Check can set item in Matching to be a group of Player instances. """

    matching = Matching(dictionary)
    suitor = suitors[0]
    new_match = reviewers[:-1]

    matching[suitor] = new_match
    assert set(matching[suitor]) == set(new_match)
    for rev in new_match:
        assert rev.matching == suitor


def test_setitem_val_error():
    """ Check that a ValueError is raised if trying to set an item with some
    illegal new matching. """

    matching = Matching(dictionary)
    suitor = suitors[0]
    new_match = [1, 2, 3]

    with pytest.raises(ValueError):
        matching[suitor] = new_match
