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

Here we can see that players :math:`C` and :math:`F` would rather be matched to
one another than their current matches, :math:`D` and :math:`E` respectively.
Thus, :math:`(C, F)` are a blocking pair in this matching and the matching is
unstable. We can attempt to rectify this instability by swapping these pairs
over:

.. image:: ../../_static/sr_stable.svg
   :width: 80 %
   :align: center

Despite this move actually making :math:`D` worse off, there are no players they
envy where the feeling is reciprocated under this matching. With that, there are
no blocking pairs and this matching is stable.
