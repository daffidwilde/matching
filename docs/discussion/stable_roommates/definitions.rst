Key definitions
---------------

The game
++++++++

Consider a set of :math:`N` players :math:`P` where :math:`N` is even. Each
player in :math:`P` has a ranking of all other players in :math:`P`, and we call
this ranking their preference list.

We can consider the preference lists of each player as a function which produces
tuples. We denote this function as :math:`f` where:

.. math::
   f : P \to P^{N-1}

This construction of players and their preference lists is called a game of
size :math:`N`, and is denoted by :math:`P`. This game is used to model
instances of SR.

Matching
++++++++

A matching :math:`M` is any pairing of the elements of :math:`P`. If a pair
:math:`(p,q) \in P \times P` are matched in :math:`M`, then we say that
:math:`M(p) = q` and, equivalently, :math:`M(q) = p`.

A matching is only considered valid if all players in :math:`P` are uniquely
matched with exactly one other player.

Blocking pair
+++++++++++++

A pair :math:`(p,q)` is said to block a matching :math:`M` if **all** of the
following hold:

   1. Both :math:`p` and :math:`q` have a match in :math:`M`.
   2. :math:`p` prefers :math:`q` to :math:`M(p) = q'`.
   3. :math:`q` prefers :math:`p` to :math:`M(q) = p'`.

The notions of preference and stability here are the same as in SM.
