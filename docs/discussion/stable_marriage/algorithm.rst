The algorithm
-------------

David Gale and Lloyd Shapley presented an algorithm for solving SM in
:cite:`GS62`. In fact, the algorithm provides a unique, stable, suitor-optimal
matching for any instance of SM and is as follows:

0. Assign all suitors and reviewers to be unmatched.

1. Take any suitor :math:`s` that is not currently matched, and consider their
   favourite reviewer :math:`r`.

2. If :math:`r` is matched, get their current match :math:`s' = M^{-1}(r)` and
   unmatch the pair.

3. Match :math:`s` and :math:`r`, i.e. set :math:`M(s) = r`.

4. For each successor, :math:`t`, to :math:`s` in :math:`g(r)`, delete the pair
   :math:`(t, r)` from the game by removing :math:`r` from :math:`f(t)` and
   :math:`t` from :math:`g(r)`.

5. Go to 1 until there are no such suitors, then end.

.. note::
   As the game requires equally sized sets of players, the *resident-optimal*
   algorithm is equivalent to the above but with the roles of suitors and
   reviewers reversed.
