Matching
========

A package for solving matching games.
-------------------------------------

A matching game is defined by two sets, called suitors and reviewers. Each
suitor has a ranked preference list of the reviewers and vice versa. The
objective of a matching game is to find a mapping between the two sets such that
no pair in the mapping can do better without destablising the other matchings.

In ``matching``, we divide matching games into two general problems; these are
known colloquially as stable marriage problems and hospital-resident assignment
problems, respectively.


The stable marriage problem
---------------------------

Here, our sets must be of the same size and we require each suitor (and
reviewer) to rank all members of the other set. In this way, we obtain a
matching between our suitors and reviewers where each suitor is matched to
exactly one reviewer, and so our matching is bijective.

It is known that instances of the stable matching problem can be solved to give
a unique, stable and suitor-optimal matching using an algorithm developed by
David Gale and Lloyd Shapley. The algorithm is as follows:

    1. Take any unmatched suitor, s, and their most preferred reviewer, r.
    If all suitors are matched, end.
    
    2. If r is unmatched, then match s to r, and go to 1. Otherwise, go
    to 3.
    
    3. Consider r's current match, s'. If r prefers s to s', then
    unmatch s' from r and match s to r. Otherwise, leave s unmatched
    and remove r from the preference list of s. In either case, go to 1.

By unique, we mean that the result of this algorithm is invariant of which order
unmatched suitors are considered. Stability is the concept that the pairings in
the matching are such that nobody could be matched to someone they prefer more
without their new partner then being able to be with someone better.
The final matching being suitor-optimal means that every suitor has their best
possible matching without making the matching unstable. A corollary of this is
that in fact, every reviewer has their worst possible matching after the
algorithm terminates.


The hospital-resident assignment problem
----------------------------------------

For this family of problems, we have a set of suitors (residents) and reviewers
(hospitals), and ranked preferences associated with each element of these sets,
as in the stable marriage problem. However, we do not require these sets to be
of the same size, nor do we require any given suitor (or reviewer) to rank all
elements of the other set. In addition to these sets, each reviewer has
associated with it a capacity. This capacity is the maximum number of suitors
that may be matched to it at any given time.

The algorithm which solves this problem is famously utilised in the USA by the
`National Resident Matching Program <http://www.nrmp.org/>`_ hence the nickname.
In fact, research surrounding this algorithm won the Nobel Prize for Economics
(2012).
