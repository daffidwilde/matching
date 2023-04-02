""" Tests for the matching classes. """
from hypothesis import given
from hypothesis.strategies import (
    composite,
    integers,
    lists,
    sampled_from,
    text,
)

from matching import MultipleMatching, SingleMatching
from matching.players import Hospital, Player


@composite
def singles(draw, names_from=text(), min_size=2, max_size=5):
    """A custom strategy for generating a matching for `SingleMatching` out of
    Player instances."""

    size = draw(integers(min_value=min_size, max_value=max_size))
    players = [Player(draw(names_from)) for _ in range(size)]

    midpoint = size // 2
    keys, values = players[:midpoint], players[midpoint:]
    dictionary = dict(zip(keys, values))

    return dictionary


@composite
def multiples(
    draw,
    host_names_from=text(),
    player_names_from=text(),
    min_hosts=2,
    max_hosts=5,
    min_players=10,
    max_players=20,
):
    """A custom strategy for generating a matching for `MultipleMatching` out
    of `Hospital` and lists of `Player` instances."""

    num_hosts = draw(integers(min_value=min_hosts, max_value=max_hosts))
    num_players = draw(integers(min_value=min_players, max_value=max_players))

    hosts = [
        Hospital(draw(host_names_from), max_players) for _ in range(num_hosts)
    ]
    players = [Player(draw(player_names_from)) for _ in range(num_players)]

    dictionary = {}
    for host in hosts:
        matches = draw(lists(sampled_from(players), min_size=0, unique=True))
        dictionary[host] = matches

    return dictionary


@given(dictionary=singles())
def test_single_setitem_none(dictionary):
    """Test that a player key in a `SingleMatching` instance can have its
    value set to `None`."""

    matching = SingleMatching(dictionary)
    key = list(dictionary.keys())[0]

    matching[key] = None
    assert matching[key] is None
    assert key.matching is None


@given(dictionary=singles())
def test_single_setitem_player(dictionary):
    """Test that a player key in a `SingleMatching` instance can have its
    value set to another player."""

    matching = SingleMatching(dictionary)
    key = list(dictionary.keys())[0]
    val = list(dictionary.values())[-1]

    matching[key] = val
    assert matching[key] == val
    assert key.matching == val
    assert val.matching == key


@given(dictionary=multiples())
def test_multiple_setitem(dictionary):
    """Test that a host player key in a `MultipleMatching` instance can have
    its value set to a sublist of the matching's values."""

    matching = MultipleMatching(dictionary)
    host = list(dictionary.keys())[0]
    players = list(
        {player for players in dictionary.values() for player in players}
    )[:-1]

    matching[host] = players
    assert matching[host] == players
    assert host.matching == players
    for player in players:
        assert player.matching == host
