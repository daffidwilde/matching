""" Tests for the Player class. """

from hypothesis import given
from hypothesis.strategies import integers, lists, text

from matching import Player


PLAYER = given(
    name=text(),
    pref_names=lists(text(), min_size=1, unique=True),
    capacity=integers(min_value=1),
)


@PLAYER
def test_init(name, pref_names, capacity):
    """ Make an instance of Player and check their attributes are correct. """

    player = Player(name, pref_names, capacity)

    assert player.name == name
    assert player.pref_names == pref_names
    assert player.capacity == capacity
    assert (
        player.matching is None
        if player.capacity == 1
        else player.matching == []
    )


@PLAYER
def test_repr(name, pref_names, capacity):
    """ Verify that a Player instance is represented by their name. """

    player = Player(name, pref_names, capacity)

    assert repr(player) == name


@PLAYER
def test_get_favourite_name(name, pref_names, capacity):
    """ Check the correct name is returned as the favourite of a player. """

    player = Player(name, pref_names, capacity)

    favourite_name = player.pref_names[0]
    assert player.get_favourite_name() == favourite_name

    other = Player(player.pref_names[0], pref_names=[player.name])

    player.matching = other
    assert player.get_favourite_name() == other.name

    player.matching = [other]
    if len(player.pref_names) > 1:
        assert player.get_favourite_name() == player.pref_names[1]
    else:
        assert player.get_favourite_name() is None


@PLAYER
def test_get_favourite(name, pref_names, capacity):
    """ Check the correct player is returned as the favourite of a player. """

    player = Player(name, pref_names, capacity)
    others = [Player(other, pref_names=[name]) for other in pref_names]

    favourite = [
        other for other in others if other.name == player.pref_names[0]
    ][0]
    assert player.get_favourite(others) == favourite

    player.matching = favourite
    assert player.get_favourite(others) == favourite

    player.matching = [favourite]
    if len(player.pref_names) > 1:
        favourite = [
            other
            for other in others
            if (
                other.name == player.pref_names[1]
                and other not in player.matching
            )
        ][0]
        assert player.get_favourite(others) == favourite
    else:
        assert player.get_favourite(others) is None


@PLAYER
def test_match(name, pref_names, capacity):
    """ Check that a player can match to another player correctly. """

    player = Player(name, pref_names, capacity)
    other = Player(pref_names[0], [name])

    player.match(other)
    assert (
        player.matching == other
        if capacity == 1
        else player.matching == [other]
    )


@PLAYER
def test_unmatch(name, pref_names, capacity):
    """ Check that a player can unmatch from another player correctly. """

    player = Player(name, pref_names, capacity)
    other = Player(pref_names[0], [name])

    player.matching = other if capacity == 1 else [other]
    player.unmatch(other)
    assert player.matching is None if capacity == 1 else player.matching == []


@PLAYER
def test_get_worst_match_idx(name, pref_names, capacity):
    """ Check that the preference index of the worst current match to a player
    can be found correctly. """

    player = Player(name, pref_names, capacity)
    others = sorted(
        [Player(other, pref_names=[name]) for other in pref_names],
        key=lambda other: player.pref_names.index(other.name),
    )

    for i, other in enumerate(others):
        if player.capacity == 1:
            player.matching = other
        else:
            player.matching.append(other)
        assert player.get_worst_match_idx() == i


@PLAYER
def test_forget(name, pref_names, capacity):
    """ Test that a player can forget somebody. """

    player = Player(name, pref_names, capacity)
    others = [Player(other, pref_names=[name]) for other in pref_names]

    for other in others[:-1]:
        player.forget(other)
        assert set(player.pref_names) == set(player.pref_names) - set(
            [other.name]
        )

    player.forget(others[-1])
    assert player.pref_names == []


@PLAYER
def test_get_successors(name, pref_names, capacity):
    """ Test that the correct successors to another player in a player's
    preference list are found with or without an index to look at. """

    player = Player(name, pref_names, capacity)
    others = sorted(
        [Player(other, pref_names=[name]) for other in pref_names],
        key=lambda other: player.pref_names.index(other.name),
    )
    favourite = player.get_favourite(others)

    player.matching = favourite
    if len(player.pref_names) > 1:
        successors = others[1:]
        assert player.get_successors(others) == successors
    else:
        assert player.get_successors(others) == []
