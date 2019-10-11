An example
----------

Consider the following instance of HR. There are five residents -- Ada, Sam, Jo,
Luc, Dani -- applying to work at three hospitals: Mercy, City, General. Each
hospital has two available positions, and the players' preferences of one
another are described in the graph below:

.. image:: ../../_static/hr_matching.svg
   :width: 80 %
   :align: center

As with SM, this representation is a easy way to keep track of the current state
of the problem and the relationships between players. Consider the matching
presented below:

.. image:: ../../_static/hr_invalid.svg
   :width: 80 %
   :align: center

This matching is invalid. In fact, none of the conditions for validity have been
met: City hospital is over-subscribed and Ada has been assigned to a hospital
that they did not rank (likewise for Mercy). Some slight tinkering can produce a
valid matching:

.. image:: ../../_static/hr_unstable.svg
   :width: 80 %
   :align: center

Even with this, the matching is not stable. There exists one blocking pair:
:math:`(L, M)`. Here, there is mutual preference, Luc prefers Mercy to General
and Mercy has a space remaining. Hence, a stable solution would be as follows:

.. image:: ../../_static/hr_stable.svg
   :width: 80 %
   :align: center

It also so happens that this matching is both resident- and hospital-optimal.
