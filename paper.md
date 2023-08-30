---
title: 'Matching: A Python library for solving matching games'
tags:
  - Python
  - mathematics
  - economics
  - computer science
  - game theory
  - stability
authors:
  - name: Henry Wilde
    orcid: 0000-0002-3788-7691
    affiliation: 1
  - name: Vincent Knight
    orcid: 0000-0002-4245-0638
    affiliation: 1
  - name: Jonathan Gillard
    orcid: 0000-0001-9166-298X
    affiliation: 1
affiliations:
  - name: School of Mathematics, Cardiff University
    index: 1
date: February 2020
bibliography: paper.bib
---

# Summary

Matching games allow for the allocation of resources and partnerships in a fair
way. Typically, a matching game is defined by two sets of players that each have
preferences over at least some of the elements of the other set. The objective
of the game is then to find a mapping between the sets of players in which
everyone is *happy enough* with their match.

One of the most ubiquitous matching games is the Stable Marriage Problem
(SM). In SM, there are two distinct player sets of size $N$: a set of suitors
$S$ and a set of reviewers $R$. Each suitor must strictly rank all of the
reviewers, and vice versa. This arrangement of suitors, reviewers, and
their preferences is called a game of size $N$ [@gale1962].

In SM, a matching is any bijection $M$ between $S$ and $R$, and it is considered
to be stable (i.e. no one has a reason to modify their current match) if it
contains no blocking pairs. A blocking pair is defined as any pair $(s, r) \in S
\times R$ that would rather be matched to one another than their current match.
This definition differs between matching games but the spirit is the same in
that a pair blocks a matching if their envy is mutually rational. Irrational
envy would be where one player wishes to be matched to another over their
current match but the other player does not (or cannot) reciprocate.

Consider the game of size three shown in Figure \ref{fig:sm_matching} as an
edgeless graph with suitors on the left and reviewers on the right. Beside each
vertex is the name of the player and their associated ranking of the
complementary set’s elements.

![A game of size three.\label{fig:sm_matching}](img/sm_matching.pdf)

@gale1962 presented an algorithm for finding a unique, stable and suitor-optimal
matching to any instance of SM. The matching this algorithm produces is shown in
Figure \ref{fig:sm_stable}.

![A stable, suitor-optimal solution.\label{fig:sm_stable}](img/sm_stable.pdf)

Using Matching, this matching can be computed as follows:

```python
>>> from matching.games import StableMarriage
>>> suitor_preferences = {
...     "A": ["D", "E", "F"], "B": ["D", "F", "E"], "C": ["F", "D", "E"]
... }
>>> reviewer_preferences = {
...     "D": ["B", "C", "A"], "E": ["A", "C", "B"], "F": ["C", "B", "A"]
... }
>>> game = StableMarriage.create_from_dictionaries(
...     suitor_preferences, reviewer_preferences
... )
>>> game.solve()
{A: E, B: D, C: F}

```

While it is relatively easy to find solutions to games like this with pen and
paper, instances of other matching games tend to have more players than this and
require the use of software to be solved in reasonable time.

# Statement of Need

Matching games have applications in many fields where relationships between
rational agents must be managed. Some example applications include: being able
to inform on healthcare finance policy [@agar2017]; helping to reduce the
complexity of automated wireless communication networks [@baya2016]; and
education infrastructure [@chia2019]. Thus, having access to software
implementations of algorithms that are able to solve such games is essential.

The only current adversary to Matching is MatchingR [@till2018]. MatchingR is a
package written in C++ with an R interface and its content overlaps well with
that of Matching. However, the lack of a Python interface makes it less
relevant to researchers and other users as Python's popularity grows both in
academia and industry.

Matching is a Python library that relies on one core library from the
standard scientific Python stack -- NumPy [@numpy] -- that currently implements
algorithms for four types of matching games:

- the stable marriage problem (SM) [@gale1962];
- the hospital-resident assignment problem (HR) [@gale1962; @roth1984];
- the student-project allocation problem (SA) [@abra2007];
- the stable roommates problem (SR) [@irvi1985].

MatchingR implements all of these except SA but also implements an algorithm for
the indivisible goods trading problem.

In addition to this, Matching has been developed to a high degree of best
practice in research software development [@jime2017], and is thoroughly
documented: [matching.readthedocs.io](https://matching.readthedocs.io). The
documentation has been written to maximise its effect as a resource for learning
about matching games as well as for the software itself. Furthermore, the
software is automatically tested using example, integration, and property-based
unit tests with 100% coverage. The current version of Matching has also been
archived on Zenodo [@matching]; as has all of the data used in the documentation
tutorials.

Matching has been designed to be used as a research tool and to aid in the
education of game theory. It is currently being used by a number of
undergraduate students and postgraduate researchers in universities around the
world, and has been used to massively streamline the final year project
allocation process for one of the largest schools at Cardiff University (as an
instance of SA). Furthermore, Matching proved to be instrumental in the
practical implementation of a novel initialisation method for a categoric
clustering algorithm [@wild2020]. With Matching being written in Python, this
tool is widely accessible by programmers and non-programmers alike as a
readable, portable, and reproducible piece of software.

# References
