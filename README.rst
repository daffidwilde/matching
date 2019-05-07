Matching
========

.. image:: https://img.shields.io/pypi/v/matching.svg
   :target: https://pypi.org/project/matching/

.. image:: https://coveralls.io/repos/github/daffidwilde/matching/badge.svg?branch=master
   :target: https://coveralls.io/github/daffidwilde/matching?branch=master

.. image:: https://travis-ci.com/daffidwilde/matching.svg?branch=master
   :target: https://travis-ci.com/daffidwilde/matching

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/ambv/black

.. image:: https://zenodo.org/badge/119597240.svg
   :target: https://zenodo.org/badge/latestdoi/119597240


A package for solving matching games.
-------------------------------------

A matching game is defined by two sets of players. Each player in one set has a
ranked preference list of those in the other, and the objective is to find some
mapping between the two sets such that no pair of players are unhappy. The
context of the terms "mapping" and "unhappy" are dependent on the framework of
the particular game being played but are largely to do with the stability of the
pairings.

In ``matching``, we deal with three types of matching game:

- the stable marriage problem (SM);
- the hospital-resident assignment problem (HR);
- the student-allocation problem (SA).


Usage
-----

With all of these games, ``matching`` uses a ``Player`` class to represent the
members of the "applying" party, i.e. residents and students. For HR and SA,
there are specific classes to represent the roles of ``Hospital``, ``Project``
and ``Supervisor``.

For instances of SM, we require a list of ``Player`` instances from each party
(suitors and reviewers) detailing their preferences lists.

Consider the following problem which is represented on a bipartite graph.

.. image:: ./img/stable_marriage.png
   :align: center
   :width: 10cm

We convey the information above in the following way:

>>> from matching import Player

>>> suitors = [Player(name="A"), Player(name="B"), Player(name="C")]
>>> reviewers = [Player(name="D"), Player(name="E"), Player(name="F")]
>>> (A, B, C), (D, E, F) = suitors, reviewers

>>> A.set_prefs([D, E, F])
>>> B.set_prefs([D, F, E])
>>> C.set_prefs([F, D, E])

>>> D.set_prefs([B, C, A])
>>> E.set_prefs([A, C, B])
>>> F.set_prefs([C, B, A])

Then to solve this matching game, we make use of the ``StableMarriage`` class,
like so:

>>> from matching.games import StableMarriage
>>> sm = StableMarriage(suitors, reviewers)
>>> sm.solve()
{A: E, B: D, C: F}

Note
^^^^

This matching is not a standard Python dictionary, though it does largely look
and behave like one. It is in fact an instance of the ``Matching`` class:

>>> matching = sm.matching
>>> matching.__class__
matching.matching.Matching

This dictionary-like object is primarily useful as a teaching device that eases
the process of manipulating a matching after a solution has been found. 


Get in contact!
---------------

I hope this package is useful, and feel free to contact me here (or on Twitter:
`@daffidwilde <https://twitter.com/daffidwilde>`_) with any issues or
recommendations. PRs always welcome!
