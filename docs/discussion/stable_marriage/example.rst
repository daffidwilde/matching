An example
----------

Consider the unsolved matching game of size three shown below as an edgeless
graph with suitors on the left and reviewers on the right. Beside each vertex is
the name of the player and their associated ranking of the complementary set’s
elements:

.. image:: ../../_static/sm_matching.svg
   :width: 80 %
   :align: center

In this representation, a matching :math:`M` creates a bipartite graph where an
edge between two vertices (players) indicates that they are matched by
:math:`M`. Consider the matching shown below:

.. image:: ../../_static/sm_unstable.svg
   :width: 80 %
   :align: center

Here we can see that players :math:`A`, :math:`C` and :math:`F` are matched to
their favourite player but :math:`B`, :math:`D` and :math:`E` are matched to
their least favourite. There’s nothing particularly special about that but we
can see that players :math:`B` and :math:`D` form a blocking pair given that
they would both rather be matched with one another than with their current
match. Hence, this matching is unstable.

We can attempt to rectify this instability by swapping the matches for the first
two rows:

.. image:: ../../_static/sm_stable.svg
   :width: 80 %
   :align: center

Upon closer inspection, we can see that each suitor is now matched with their
most preferred reviewer so as not to form a blocking pair that would upset any
current matchings. This matching is stable and is considered *suitor-optimal*.
