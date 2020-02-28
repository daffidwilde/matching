The algorithm
-------------

Finding stable and optimal solutions to SA is easily motivated since those
solutions would solve the real-world problem they model. Actually implementing
this in the real world is described in more detail in `this tutorial
<../../tutorials/project_allocation/main.ipynb>`_.

As with HR, there are two algorithms implemented in Matching to solve instances
of SA, one to handle the optimality of each party (students and
project/supervisors). These algorithms, taken from :cite:`AIM07`, follow a
similar structure to those for HR in that they take advantage of the inherent
structure of the game. Again, each party-optimal algorithm provides a unique,
stable matching for an instance of SA.

Student-optimal
+++++++++++++++

0. Assign all students to be unmatched, and all supervisors (and their projects)
   to be totally unsubscribed.

1. Take any student :math:`s` that is unmatched and has a non-empty preference
   list, and consider their most preferred project :math:`p`. Let :math:`u =
   L(p)`. Assign :math:`s` to be matched to :math:`p` (and thus :math:`u`).

2. If :math:`p` is over-subscribed, find its worst current match :math:`s'`.
   Unmatch :math:`p` and :math:`s'`. Else if :math:`u` is over-subscribed, find
   their worst current match :math:`s'` and the project :math:`p'` that
   :math:`s'` is assigned to. Unmatch :math:`p'` and :math:`s'`.

3. If :math:`p` is at capacity, find their worst current match :math:`s'`. For
   each successor :math:`t \in g_p(u)` to :math:`s'`, delete the pair :math:`(t,
   p)` from the game by removing :math:`p` from :math:`f(t)` and :math:`t` from
   :math:`g(u)` (and thus :math:`g_p(u)`).

4. If :math:`u` is at capacity, find their worst current match :math:`s'`. For
   each successor :math:`t \in g(u)` to :math:`s'`, delete the pair :math:`(t,
   p)` from the game.

5. Go to 1 until there are no such students left, then end.

Supervisor-optimal
++++++++++++++++++

0. Assign all students to be unmatched, and all supervisors (and their projects)
   to be totally unsubscribed.

1. Take any supervisor :math:`u` that is under-subscribed and whose preference
   list contains at least one student that is not currently matched
   to at least one acceptable (though currently under-subscribed) project
   offered by :math:`u`. Consider the supervisor's most preferred such student
   :math:`s` and that student's most preferred such project :math:`p`.

2. If :math:`s` is matched to some other project :math:`p'` then unmatch them.

3. Assign :math:`s` to be matched to :math:`p` (and thus :math:`u`).

4. For each successor :math:`p' \in f(s)` to :math:`p`, delete the pair
   :math:`(s, p')` from the game.

5. Go to 1 until there are no such supervisors, then end.

