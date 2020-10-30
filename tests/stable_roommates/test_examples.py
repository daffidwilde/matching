""" A collection of example tests. """

from matching import Player
from matching.algorithms import stable_roommates


def test_original_paper():
    """Verify that the matching found is consistent with the example in the
    original paper."""

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


def test_example_in_issue_64():
    """Verify that the matching found is consistent with the example provided
    in #64."""

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
    """Verify that the matching is consistent with the examples provided in
    #124."""

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
    """ Verify that a matching is given when there are only two players. """

    p1, p2 = players = [Player(1), Player(2)]

    p1.set_prefs([p2])
    p2.set_prefs([p1])

    matching = stable_roommates(players)
    assert matching == {p1: p2, p2: p1}
