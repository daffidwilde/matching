Key definitions
---------------

The game
++++++++

Consider three distinct sets, :math:`S`, :math:`P` and :math:`U`, and let us
refer to them as students, projects and supervisors. Each project :math:`p \in
P` has a single supervisor :math:`u \in U` associated with them. This
association is described as a surjective function :math:`L: P \to U` where the
supervisor :math:`u \in U` for a project :math:`p \in P` can be written as
:math:`L(p) = u`. Note that as :math:`L` is surjective, :math:`u` may have
multiple projects associated with them and we denote their set of projects as
:math:`L^{-1}(u)`.

In addition to this, each project :math:`p \in P` and supervisor :math:`u \in U`
has a capacity associated with them, denoted :math:`c_p, c_u \in \mathbb{N}`
respectively. We assume that for each :math:`u \in U` the following holds:

.. math::
   \max\left\{ c_p \ | \ p \in L^{-1}(u) \right\}
   \leq c_u \leq
   \sum_{p \in L^{-1}(u)} c_p

That is, a supervisor must be able to accommodate their largest project but not
offer more spaces than their projects sum to.

As with other matching games, each player has a preference list associated with
them. In the case of SA, we have the following constraints on those preferences:

- Each student :math:`s \in S` must rank a non-empty subset of :math:`P`. We
  denote this preference by :math:`f(s)`.
- Each supervisor :math:`u \in U` must rank **all** those students that have
  ranked **at least one** of their projects. That is, the preference list of
  :math:`u`, denoted :math:`g(u)`, is a permutation of the set given by
  :math:`\left\{ s \in S \ | \ L^{-1}(u) \cap f(s) \neq \emptyset \right\}`. If
  no students have ranked any of a supervisor's projects then that supervisor is
  removed from :math:`U`.
- The preference list of a project :math:`p \in P` is governed by its supervisor
  :math:`u = L(p)`. We denote this preference as :math:`g_p(u)` and it is simply
  :math:`g(u)` without the students who did not rank :math:`p`. If no students
  have ranked a project then that project is removed from :math:`P`.

This construction of students, projects, supervisors, associations, capacities
and preference lists is a game and is denoted by :math:`(S,P,U)`. This game is
used to model instances of SA.


Matching
++++++++

A matching :math:`M` is any mapping between :math:`S` and :math:`P`. If a pair
:math:`(s, p) \in S \times P` are matched in :math:`M`, we say that :math:`M(s)
= p` and :math:`s \in M^{-1}(p)`. We also note that since each supervisor
:math:`u \in U` oversees their projects (by definition), their matching can be
referred to as the union of its projects' matchings:

.. math::
   M^{-1}(u) = \bigcup_{p \in L^{-1}(u)} M^{-1}(p) \subseteq S

A matching is only considered valid if **all** of the following are satisfied:

    1. For all :math:`s \in S` with a match we have :math:`M(s) \in f(s)`.
    2. For all :math:`p \in P` we have :math:`M^{-1}(p) \subseteq g_p(u)` and
       :math:`|M^{-1}(p)| \leq c_p`.
    3. For all :math:`u \in U` we have :math:`M^{-1}(u) \subseteq g(u)` and
       :math:`|M^{-1}(u)| \leq c_u`.

As always, a valid matching is considered stable if it does not contain any
blocking pairs.


Blocking pair
+++++++++++++

A pair :math:`(s, p)` is said to block a matching :math:`M` if **all** the
following hold:

    1. The student has a preference of the project, i.e. :math:`p \in f(s)`.
    2. Either :math:`s` is unmatched or they prefer :math:`p` to
       :math:`M(s) = p'`.
    3. At least one of the following is true, where :math:`u = L(p)`:

          - Both :math:`p` and :math:`u` are under-subscribed, i.e.
            :math:`|M^{-1}(p)| < c_p` and :math:`|M^{-1}(u)| < c_u`.
          - :math:`|M^{-1}(p)| < c_p` and :math:`|M^{-1}(u)| = c_u`, and either
            :math:`M(s) = p' \in L^{-1}(u)` or :math:`u` prefers :math:`s` to
            their worst current match :math:`s' \in M^{-1}(u)`.
          - :math:`|M^{-1}(p)| = c_p` and :math:`u` prefers :math:`s` to the
            project's worst student :math:`s \in M^{-1}(p)`.

The notion of preference is equivalent to that in SM.
