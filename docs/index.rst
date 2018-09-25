.. matching documentation master file, created by
   sphinx-quickstart on Tue Sep 18 12:02:05 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to matching's documentation!
====================================

A matching game is defined by two sets, called suitors and reviewers. Each
suitor has a ranked preference list of the reviewers and vice versa. The
objective of a matching game is to find a mapping between the two sets such that
no pair in the mapping can do better without upsetting the other matchings.

In :code:`matching`, we divide matching games into two general problems; these
are known colloquially as stable marriage problems and hospital-resident
assignment problems respectively.

The purpose of :code:`matching` is to solve instances of these games and house
implementations of algorithms with which to do that.

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
* :ref:`search`
