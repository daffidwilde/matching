An example
----------

Consider the following instance of SA. There are five students - Avery, Blake,
Cleo, Devon, Everest - in their final year of university. As part of this year,
they may apply to do a project. There are two members of staff providing these
projects - Dr. Xavier and Prof. Yeo. Each supervisor may take at most three
students and each offer two projects with space for two students on each. The
players' preferences are described in the graph below:

.. image:: ../../_static/sa_matching.svg
   :width: 90 %
   :align: center

Note that in this particular example, the students are ranked in the same order
by both supervisors (as is often the case in real-world applications of SA). Now
consider the matching below:

.. image:: ../../_static/sa_invalid.svg
   :width: 90 %
   :align: center

This matching is invalid, and none of the conditions for validity have been met.
Specifically:

- Avery has been allocated Dr. Yeo's first project despite not ranking it (and
  likewise for Dr. Yeo and the project)
- Dr. Yeo's first project has been allocated a total of three students which
  exceeds its capacity of two.
- In addition to this, Dr. Yeo has been allocated a fourth student, violating
  their capacity constraint.

With a few changes, we can make this matching valid. Swapping Avery and Cleo
with Devon is a start since they are Dr. Xavier's favourite students after
Blake. Then we can move Devon to Y2 as this is their most preferred project.
Doing this gives the following matching:

.. image:: ../../_static/sa_unstable.svg
   :width: 90 %
   :align: center

Unfortunately, and despite our efforts to accommodate people's preferences, this
matching is not stable. Here we have two blocking pairs, :math:`(E, X2)` and
:math:`(E, Y2)`. Although Everest prefers X1 to either of these projects, they
do not form a blocking pair as X1 is full and Dr. Xavier prefers Avery and Cleo
to Everest.

So, in order to overcome these blocking pairs without creating more, Devon must
be swapped with Everest. This also feels like the fairest move given that
Everest outranks Devon. The following graph displays this new, stable matching:

.. image:: ../../_static/sa_stable.svg
   :width: 90 %
   :align: center

It also happens that this matching is student-optimal as well as being stable
and valid.
