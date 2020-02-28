The algorithm
-------------

Finding optimal, stable matchings for HR is of great importance as it solves
real-world problems. For instance, the `National Resident Matching Program
<http://www.nrmp.org>`_ uses an algorithm like the one presented here to assign
medical students in the US to hospitals. An algorithm which solves HR was
originally presented in :cite:`GS62` but further work was done to improve on
these algorithms in later years :cite:`DF81`, :cite:`Rot84`. Unlike the
algorithm for SM, this algorithm takes a different form depending on the desired
optimality of the solution. Below are the resident-optimal and hospital-optimal
algorithms for finding a unique, stable matching for an instance of HR.

Resident-optimal
++++++++++++++++

0. Assign all residents to be unmatched, and all hospitals to be totally
   unsubscribed.

1. Take any unmatched resident with a non-empty preference list :math:`r`, and
   consider their most preferred hospital :math:`h`. Match them to one another.

2. If :math:`|M^{-1}(h)| > c_h`, find the worst resident :math:`r'` assigned to
   :math:`h` and unmatch the pair :math:`(r', h)`.

3. If :math:`|M^{-1}(h)| = c_h`, find the worst resident :math:`r'` assigned to
   :math:`h`. Then, for each successor :math:`s \in g(h)` to :math:`r'`, delete
   the pair :math:`(s, h)` from the game by removing :math:`h` from :math:`f(s)`
   and :math:`s` from :math:`g(h)`.

4. Go to 1 until there are no such residents left, then end.

Hospital-optimal
++++++++++++++++

0. Set all residents to be unmatched, and all hospitals to be totally
   unsubscribed.

1. Take any hospital :math:`h` that is under-subscribed and whose preference
   list contains any resident they are not currently assigned to, and consider
   their most preferred such resident :math:`r`.

2. If :math:`r` is currently matched to some other hospital :math:`h'`, then
   unmatch them from one another.

3. Match :math:`r` with :math:`h`.

4. For each successor :math:`s \in f(r)` to :math:`h`, delete the pair
   :math:`(r, s)` from the game.

5. Go to 1 until there are no such hospitals left, then end.
