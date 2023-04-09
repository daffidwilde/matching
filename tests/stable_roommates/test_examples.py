"""A collection of example tests for SR."""

import pytest
from hypothesis import given
from hypothesis.strategies import permutations

from matching import Player
from matching.algorithms import stable_roommates
from matching.exceptions import NoStableMatchingWarning
from matching.games.stable_roommates import _make_players


def test_original_paper_stable():
    """Test the example from the original paper."""

    players = [Player(name) for name in ("A", "B", "C", "D", "E", "F")]
    a, b, c, d, e, f = players

    a.set_prefs([d, f, b, e, c])
    b.set_prefs([f, c, e, a, d])
    c.set_prefs([d, e, a, f, b])
    d.set_prefs([b, f, e, a, c])
    e.set_prefs([d, b, c, f, a])
    f.set_prefs([e, a, d, b, c])

    matching = stable_roommates(players)
    assert matching == {a: f, b: c, c: b, d: e, e: d, f: a}


@given(last_player_prefs=permutations([1, 2, 3]))
def test_gale_shapley_no_stable_matching(last_player_prefs):
    """Test the example from [GS62] says there is no stable matching."""

    preferences = {
        1: [2, 3, 4],
        2: [3, 1, 4],
        3: [1, 2, 4],
        4: last_player_prefs,
    }

    players = _make_players(preferences)

    with pytest.warns(NoStableMatchingWarning) as record:
        stable_roommates(players)

    assert "4" in str(record[0].message)


def test_large_example_from_book():
    """Test the example of size ten in [GI89] (Section 4.2.3)."""

    preferences = {
        1: [8, 2, 9, 3, 6, 4, 5, 7, 10],
        2: [4, 3, 8, 9, 5, 1, 10, 6, 7],
        3: [5, 6, 8, 2, 1, 7, 10, 4, 9],
        4: [10, 7, 9, 3, 1, 6, 2, 5, 8],
        5: [7, 4, 10, 8, 2, 6, 3, 1, 9],
        6: [2, 8, 7, 3, 4, 10, 1, 5, 9],
        7: [2, 1, 8, 3, 5, 10, 4, 6, 9],
        8: [10, 4, 2, 5, 6, 7, 1, 3, 9],
        9: [6, 7, 2, 5, 10, 3, 4, 8, 1],
        10: [3, 1, 6, 5, 2, 9, 8, 4, 7],
    }

    players = _make_players(preferences)
    one, two, three, four, five, six, seven, eight, nine, ten = players

    matching = stable_roommates(players)

    assert matching == {
        one: seven,
        two: eight,
        three: six,
        four: nine,
        five: ten,
        six: three,
        seven: one,
        eight: two,
        nine: four,
        ten: five,
    }


def test_example_in_issue_64():
    """Test the example provided in #64."""

    players = [
        Player(name)
        for name in ("charlie", "peter", "elise", "paul", "kelly", "sam")
    ]
    charlie, peter, elise, paul, kelly, sam = players

    charlie.set_prefs([peter, paul, sam, kelly, elise])
    peter.set_prefs([kelly, elise, sam, paul, charlie])
    elise.set_prefs([peter, sam, kelly, charlie, paul])
    paul.set_prefs([elise, charlie, sam, peter, kelly])
    kelly.set_prefs([peter, charlie, sam, elise, paul])
    sam.set_prefs([charlie, paul, kelly, elise, peter])

    matching = stable_roommates(players)
    assert matching == {
        charlie: sam,
        peter: kelly,
        elise: paul,
        paul: elise,
        kelly: peter,
        sam: charlie,
    }


def test_examples_in_issue_124():
    """Test the examples provided in #124."""

    a, b, c, d = players = [Player(name) for name in ("a", "b", "c", "d")]

    a.set_prefs([b, c, d])
    b.set_prefs([a, c, d])
    c.set_prefs([a, b, d])
    d.set_prefs([a, b, c])

    matching = stable_roommates(players)
    assert matching == {a: b, b: a, c: d, d: c}

    for player in players:
        player._unmatch()

    a.set_prefs([b, c, d])
    b.set_prefs([a, c, d])
    c.set_prefs([d, b, a])
    d.set_prefs([c, b, a])

    matching = stable_roommates(players)
    assert matching == {a: b, b: a, c: d, d: c}


def test_trivial_case():
    """Test that a matching is given when there are only two players."""

    p1, p2 = players = [Player(1), Player(2)]

    p1.set_prefs([p2])
    p2.set_prefs([p1])

    matching = stable_roommates(players)
    assert matching == {p1: p2, p2: p1}
