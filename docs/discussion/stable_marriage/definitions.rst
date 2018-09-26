Definitions
-----------

Matching game
+++++++++++++

Consider two distinct sets, :math:`S`, :math:`R`, each of size :math:`N`, and
let us refer to these sets as suitors and reviewers respectively. Each element
of :math:`S` and :math:`R` has a ranking of all the other set’s elements
associated with it, and we call this ranking their preference list. Typically,
these rankings are in descending order of preference.

We can consider the preference lists for the elements of each set as a function
which produces tuples. We call these functions :math:`f` and :math:`g`
respectively:

.. math::
   f : S \to R^N; \quad g : R \to S^N

This construction of suitors, reviewers and preference lists is called a
matching game of size :math:`N`, and the game is denoted by :math:`(S,R)`. An
instance of SMP can be modelled as a matching game :math:`(S,R)`.

Matching
++++++++

A matching :math:`M` is any bijection between :math:`S` and :math:`R`. If a pair
:math:`(s,r) \in S \times R` are matched in :math:`M`, then we say that
:math:`M(s) = r` and, equivalently, :math:`M^{−1}(r) = s`.

Blocking pair
+++++++++++++

A pair :math:`(s,r)` is said to block a matching :math:`M` if:

   - :math:`s` and :math:`r` aren’t matched by :math:`M`, i.e.
     :math:`M(s) \neq r`,
   - :math:`s` prefers :math:`r` to :math:`M(s) = r'`, and
   - :math:`r` prefers :math:`s` to :math:`M^{-1}(r) = s′`.

That is, :math:`r` appears before :math:`r′` in :math:`f(s)` **and** :math:`s`
appears before :math:`s′` in :math:`g(r)`.

Stable matching
+++++++++++++++

A matching :math:`M` is said to be stable if it contains no blocking pairs, and
unstable otherwise.
