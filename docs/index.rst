.. matching documentation master file, created by
   sphinx-quickstart on Tue Sep 18 12:02:05 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Matching's documentation!
====================================

Matching is a package for solving matching games.

A matching game is defined by two sets of players. Each player in one set has a
ranked preference list of those in the other, and the objective is to find some
mapping between the two sets such that no pair of players are unhappy. The
context of the terms "mapping" and "unhappy" are dependent on the framework of
the particular game being played but are largely to do with the stability of the
pairings.

In Matching, we deal with three types of matching game:

- the stable marriage problem (SM);
- the hospital-resident assignment problem (HR);
- the student-allocation problem (SA);
- the stable roommates problem (SR).

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   tutorials/index.rst
   how-to/index.rst
   discussion/index.rst
   reference/index.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
