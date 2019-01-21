Matching
========

.. image:: https://img.shields.io/pypi/v/matching.svg
   :target: https://pypi.org/project/matching/

A package for solving matching games.
-------------------------------------

A matching game is defined by two sets, called suitors and reviewers. Each
suitor has a ranked preference list of the reviewers and vice versa. The
objective of a matching game is to find a mapping between the two sets such that
no pair in the mapping can do better without destabilising the other matchings.

In ``matching``, we divide matching games into two general problems; these are
known colloquially as stable marriage problems and hospital-resident assignment
problems, respectively.


The stable marriage problem
---------------------------

Here, our sets must be of the same size and we require each suitor (and
reviewer) to rank all members of the other set. In this way, we obtain a
matching between our suitors and reviewers where each suitor is matched to
exactly one reviewer, and so our matching is bijective.

It is known that instances of the stable marriage problem can be solved to give
a unique, stable and suitor-optimal matching using an algorithm developed by
David Gale and Lloyd Shapley. The suitor-oriented algorithm is as follows:

0. Assign all suitors and reviewers to be unmatched.

1. Take any unmatched suitor, **s**, and their most preferred reviewer, **r**.
   If all suitors are matched, end.
    
2. If **r** is unmatched, then match **s** to **r**, and go to 1. Otherwise, go
   to 3.
    
3. Consider **r**'s current match, **s'**. If **r** prefers **s** to **s'**,
   then unmatch **s'** from **r** and match **s** to **r**. Otherwise, leave
   **s** unmatched and remove **r** from the preference list of **s**. In either
   case, go to 1.

By unique, we mean that the result of this algorithm is invariant of which order
unmatched suitors are considered. Stability is the concept that the pairings in
the matching are such that nobody could be matched to someone they prefer more
without their new partner then being able to be with someone better.
The final matching being suitor-optimal means that every suitor has their best
possible matching without making the matching unstable. A corollary of this is
that, in fact, every reviewer has their worst possible matching after the
algorithm terminates.

Usage
^^^^^

With both forms of matching game, ``matching`` uses a ``Player`` class to
represent the members of each party. In particular, for instances of the stable
marriage problem, we require a list of ``Player`` instances from each party
(suitors and reviewers) detailing their preferences lists. The preference lists
for suitors should be comprised of the names of the reviewers, and vice versa.

Consider the following stable marriage problem which is represented on a
bipartite graph.

.. image:: ./img/stable_marriage.svg
   :align: center
   :width: 10cm

We convey the information above in the following way:

>>> from matching import Player
>>> suitors = [
...     Player(name="A", pref_names=["D", "E", "F"]),
...     Player(name="B", pref_names=["D", "F", "E"]),
...     Player(name="C", pref_names=["F", "D", "E"]),
... ]
>>> reviewers = [
...     Player(name="D", pref_names=["B", "C", "A"]),
...     Player(name="E", pref_names=["A", "C", "B"]),
...     Player(name="F", pref_names=["C", "B", "A"]),
... ]

Then to solve this matching game, we make use of the ``StableMarriage`` class,
like so:

>>> from matching import StableMarriage
>>> sm = StableMarriage(suitors, reviewers)
>>> sm.solve()
{A: E, B: D, C: F}

It is easily checked - on paper or mentally - that this is the correct solution.

.. note::
   The keys and values in this dictionary are the Player instances, not the
   names. They will need to be extracted as necessary.


The hospital-resident assignment problem
----------------------------------------

For this family of problems, we have a set of suitors (residents) and reviewers
(hospitals), and ranked preferences associated with the elements of these sets,
as in the stable marriage problem. In this case, we do not require these sets to
be of the same size, nor do we require any given suitor (or reviewer) to rank
all elements of the other set.

However, there are conditions on these lists which are necessary for a valid
instance of this problem: every hospital must rank all residents who rank them,
and no hospital may rank a resident who has not been ranked by them.

In addition to these lists, each hospital has associated with it an integer
capacity. This capacity is the maximum number of residents that may be matched
to it at any given time.

An algorithm which solves this problem is famously utilised in the USA by the
`National Resident Matching Program <http://www.nrmp.org/>`_, hence the
nickname. In fact, research surrounding this algorithm won Shapley, along with
Alvin Roth, the `Nobel Prize for Economics <http://www.nytimes.com/2012/10/16/
business/economy/
alvin-roth-and-lloyd-shapley-win-nobel-in-economic-science.html>`_ in 2012. In
this package we refer to this algorithm as the Hospital-Resident algorithm.
However, it has several synonyms including: 'The Match', 'the Capacitated
Gale-Shapley algorithm', 'the Roth-Shapley algorithm', and 'the deferred
acceptance algorithm'. This algorithm has also been used to develop donor chains
for kidney transplants saving thousands of lives in the process.

The suitor- (resident-) oriented algorithm is as follows:

0. Assign all residents to be unmatched, and all hospitals to be totally
   unsubscribed.

1. Take any unmatched resident with a non-empty preference list, :math:`r`, and
   consider their most preferred hospital, :math:`h`. Match them to one another.
   
2. If, as a result of this new matching, :math:`h` is now over-subscribed, find
   the worst resident currently assigned to :math:`h`, :math:`r'`. Set
   :math:`r'` to be unmatched and remove them from the hospital's matching. Go
   to 3.

3. If :math:`h` is at capacity (fully subscribed) then find their worst current
   match :math:`r'`. Then, for each successor, :math:`s`, to :math:`r'` in the
   preference list of :math:`h`, delete the pair :math:`(s, h)` from the game.
   Go to 4.

4. Go to 1 until there are no such residents left, then end.

Usage
^^^^^

In a similar fashion to the stable marriage problem, we interpret
hospital-resident assignment problems using the ``Player`` class and a solver
class specific to HR. In addition to the preference lists of either party,
however, we pass a capacity to each hospital (reviewer).

Consider the following example. We have five medical residents - Alec, Sammy,
Jo, Lucy and David - and three hospitals, each with 2 positions available:
Mercy, City and General. We display their preferences in a similar fashion to
before:

.. image:: ./img/hospital_resident.svg
   :align: center
   :width: 10cm

In ``matching`` we summarise this problem in the following way:

>>> from matching import Player
>>> residents = [
...     Player("A", ["C"]),
...     Player("S", ["C", "M"]),
...     Player("D", ["C", "M", "G"]),
...     Player("L", ["M", "C", "G"]),
...     Player("J", ["C", "G", "M"]),
... ]
>>> hospitals = [
...     Player("M", ["D", "L", "J", "S"], capacity=2),
...     Player("C", ["D", "A", "S", "L", "J"], capacity=2),
...     Player("G", ["D", "J", "L"], capacity=2),
... ]

We then solve this problem using the ``HospitalResident`` class:

>>> from matching import HospitalResident
>>> hr = HospitalResident(suitors=residents, reviewers=hospitals)
>>> hr.solve()
{M: [L, S], C: [D, A], G: [J]}

Again, though less likely to be done in your head, you can verify that this
matching is correct according to the algorithm stated above.


Get in contact!
---------------

I hope this package is useful, and feel free to contact me here (or on Twitter:
`@daffidwilde <https://twitter.com/daffidwilde>`_) with any issues or
recommendations. PRs always welcome!
