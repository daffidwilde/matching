""" A collection of example tests. """

from matching import Player
from matching.games import stable_roommates


def test_original_paper():
    """ Verify that the matching found is consistent with the example in the
    original paper. """

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


def test_example_in_issue():
    """ Verify that the matching found is consistent with the example provided
    in #64. """

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
