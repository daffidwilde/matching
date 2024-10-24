"""Tests for the matching classes."""

from hypothesis import given
from hypothesis.strategies import (
    composite,
    integers,
    lists,
    sampled_from,
    text,
)

from matching import MultipleMatching
from matching.players import Hospital, Player


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
    """A strategy for creating multiple-match matchings from players."""

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


@given(dictionary=multiples())
def test_multiple_setitem(dictionary):
    """Test that a host player in a matching can have a list match."""

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
