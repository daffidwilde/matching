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

One of the most ubiquitous matching games models the Stable Marriage Problem
(SM). In SM, there are two distinct player sets of size $N$: a set of suitors
$S$ and a set of reviewers $R$. Each suitor must strictly rank all of the
reviewers, and vice versa. This arrangement of suitors, reviewers, and
their preferences is called a game of size $N$ [@gale1962].

In SM, a matching is any bijection $M$ between $S$ and $R$, and it is considered
to be stable (i.e. everyone is happy enough) if it contains no blocking pairs.
A blocking pair is defined as any pair $(s, r) \in S \times R$ that would rather
be matched to one another than their current match. This definition differs
between matching games but the spirit is the same in that a pair blocks a
matching if their envy is mutually rational. Irrational envy would be where one
player wishes to be matched to another over their current match but the other
player does not (or cannot) reciprocate.

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
>>> from matching import Player
>>> from matching.games import StableMarriage
>>> suitors = [Player(name="A"), Player(name="B"), Player(name="C")]
>>> reviewers = [Player(name="D"), Player(name="E"), Player(name="F")]
>>> (A, B, C) = suitors
>>> (D, E, F) = reviewers
>>> A.set_prefs([D, E, F])
>>> B.set_prefs([D, F, E])
>>> C.set_prefs([F, D, E])
>>> D.set_prefs([B, C, A])
>>> E.set_prefs([A, C, B])
>>> F.set_prefs([C, B, A])
>>> game = StableMarriage(suitors, reviewers)
>>> game.solve()
{A: E, B: D, C: F}
```

While it is relatively easy to find solutions to games like this with pen and
paper, instances of other matching games tend to have more players than this and
require the use of software to be solved in reasonable time.

# Statement of Need

Matching games have applications in a number of fields including social and
market economics [@agar2017; @okun1995], wireless communication [@baya2016], and
education infrastructure [@chia2019]. Thus, having access to software
implementations of algorithms that are able to solve such games is essential.

The only current adversary to Matching is MatchingR [@tilly2018]. MatchingR is a
package written in C++ with an R interface and its content overlaps well with
that of Matching. However, the lack of a Python interface makes it less
relevant to researchers and other users as Python's popularity grows both in
academia and industry.

Matching is a Python library that relies on one core library from the
standard scientific Python stack -- NumPy [@numpy] -- that currently implements
algorithms for four types of matching games:

- The stable marriage problem (SM) [@gale1962];
- the hospital-resident assignment problem (HR) [@gale1962; @roth1984];
- the student-project allocation problem (SA) [@abra2007];
- the stable roommates problem (SR) [@irvi1985].

In addition to this, Matching has been developed to a high degree of best
practices in research software development [@jime2017], and is thoroughly
documented: [matching.readthedocs.io](https://matching.readthedocs.io).
Furthermore, the software automatically tested using example, integration, and
property-based unit tests with 100% coverage. The current version of Matching
has also been archived on Zenodo [@matching].

The primary limitations of Matching are the time complexities of the algorithm
implementations. In practical terms, the running time of any of the algorithms
in Matching is negligible but the theoretic complexity of each has not yet been
attained. For example, an instance of HR with 400 applicants and 20 hospitals is
solved in less than one tenth of a second:

```python
>>> from matching.games import HospitalResident
>>> import numpy as np
>>> np.random.seed(0)
>>> resident_prefs = {
...     r: np.argsort(np.random.random(size=20)) for r in range(400)
... }
>>> hospital_prefs = {
...     h: np.argsort(np.random.random(size=400)) for h in range(20)
... }
>>> capacities = {h: 20 for h in hospital_prefs}
>>> game = HospitalResident.create_from_dictionaries(
...     resident_prefs, hospital_prefs, capacities
>>> )
>>> _ = game.solve() # 48.6 ms ± 963 µs per loop
```

Matching has been designed to be used as a research tool and to aid in the
education of game theory. It is currently being used by a number of
undergraduate students and postgraduate researchers in universities around the
world, and has been used to massively streamline the final year project
allocation process for one of the largest schools at Cardiff University. With
Matching being written in Python, this tool is widely accessible by programmers
and non-programmers alike as a readable, portable, and reproducible piece of
software.

# References
