An example
----------

Consider the instance of SR below. Here there are six people looking to bunk
together on a school trip - Alex, Bowie, Carter, Dallas, Evelyn and Finn. Their
preferences of one another are described in the graph below:

.. image:: ../../_static/sr_matching.svg
   :width: 80 %
   :align: center

In this representation, a valid matching :math:`M` creates a 1-regular graph.
Again, this graphical representation makes it easy to see the current
relationships between the players. Consider the matching below:

.. image:: ../../_static/sr_unstable.svg
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

.. image:: ../../_static/sr_stable.svg
   :width: 80 %
   :align: center

Upon closer inspection, we can see that each suitor is now matched with their
most preferred reviewer so as not to form a blocking pair that would upset any
current matchings. This matching is stable and is considered *suitor-optimal*.
