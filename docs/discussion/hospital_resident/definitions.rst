Key definitions
---------------

The game
++++++++

Consider two distinct sets, :math:`R` and :math:`H`, and let us refer to them as
residents and hospitals. Each hospital :math:`h \in H` has a capacity associated
with them :math:`c_h \in \mathbb{N}`.

As in SM, each player has a preference list associated with them but they
needn't be exhaustive of the other party. Instead:

- Each resident :math:`r \in R` must rank a non-empty subset of :math:`H`. We
  denote this preference by :math:`f(r)`.
- Each hospital :math:`h \in H` must rank **all** those residents that have
  ranked it. That is, the preference list of :math:`h`, denoted by :math:`g(h)`,
  is a permutation of the set given by :math:`\left\{r \in R \ | \ h \in
  f(r)\right\}`. If no residents rank a hospital then that hospital is removed
  from :math:`H`.

This construction of residents, hospitals, capacities and preference lists is
a game and is denoted by :math:`(R,H)`. This game is used to model instances of
HR.

Matching
++++++++

A matching :math:`M` is any mapping between :math:`R` and :math:`H`. If a pair
:math:`(r, h) \in R \times H` are matched in :math:`M`, we say that
:math:`M(r) = h` and :math:`r \in M^{-1}(h)`.

A matching is only considered valid if **all** of the following are satisfied:

    1. For all :math:`r \in R` with a match we have :math:`M(r) \in f(r)`.
    2. For all :math:`h \in H` with matches we have
       :math:`M^{-1}(h) \subseteq g(h)`.
    3. For all :math:`h \in H` we have :math:`|M^{-1}(h)| \leq c_h`.

Again, a valid matching is considered stable if it does not contain any blocking
pairs.

Blocking pair
+++++++++++++

A pair :math:`(r, h)` is said to block a matching :math:`M` if **all** the
following hold:

    1. There is mutual preference, i.e. :math:`r \in g(h)` **and**
       :math:`h \in f(r)`.
    2. Either :math:`r` is unmatched or they prefer :math:`h` to
       :math:`M(r) = h'`.
    3. Either :math:`|M^{-1}(h)| < c_h` or :math:`h` prefers :math:`r` to at
       least one :math:`r' \in M^{-1}(h)`.

The notion of preference here is the same as in SM.
