""" A collection of example tests. """

from matching import Player
from matching.games import stable_marriage


def test_pride_and_prejudice():
    """ Verify that the matching found is consistent with the one adapted from
    Jane Austen's Pride and Prejudice. Also used in
    `docs/discussion/stable_marriage/example.rst`. """

    suitors = [
        Player(name="Bingley"),
        Player(name="Collins"),
        Player(name="Darcy"),
        Player(name="Wickham"),
    ]

    reviewers = [
        Player(name="Charlotte"),
        Player(name="Elizabeth"),
        Player(name="Jane"),
        Player(name="Lydia"),
    ]

    bingley, collins, darcy, wickham = suitors
    charlotte, elizabeth, jane, lydia = reviewers

    bingley.set_prefs([jane, elizabeth, lydia, charlotte])
    collins.set_prefs([jane, elizabeth, lydia, charlotte])
    darcy.set_prefs([elizabeth, jane, charlotte, lydia])
    wickham.set_prefs([lydia, jane, elizabeth, charlotte])

    charlotte.set_prefs([bingley, darcy, collins, wickham])
    elizabeth.set_prefs([wickham, darcy, bingley, collins])
    jane.set_prefs([bingley, wickham, darcy, collins])
    lydia.set_prefs([bingley, wickham, darcy, collins])

    matching = stable_marriage(suitors, reviewers)
    assert matching == {
        bingley: jane,
        collins: charlotte,
        darcy: elizabeth,
        wickham: lydia,
    }


def test_readme_example():
    """ Verify the example used in the repo README. """

    suitors = [Player(name="A"), Player(name="B"), Player(name="C")]
    reviewers = [Player(name="D"), Player(name="E"), Player(name="F")]
    (A, B, C), (D, E, F) = suitors, reviewers

    A.set_prefs([D, E, F])
    B.set_prefs([D, F, E])
    C.set_prefs([F, D, E])

    D.set_prefs([B, C, A])
    E.set_prefs([A, C, B])
    F.set_prefs([C, B, A])

    matching = stable_marriage(suitors, reviewers)
    assert matching == {A: E, B: D, C: F}
