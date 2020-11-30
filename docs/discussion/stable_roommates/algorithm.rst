The algorithm
-------------

Robert Irving presented an efficient, two-phase algorithm for finding a stable
matching to SR in :cite:`Irv85`, if one exists. An extended form of the
algorithm was presented in :cite:`GI89`, and is given below.

Phase 1
+++++++

The first phase of the algorithm consists of one-way proposals (we still refer
to these as matches here) and removes unpreferable pairs from the game. Begin by
assigning all players to be unmatched and without any proposals. Then, while
there is a player, :math:`p`, who does not have a held proposal and has a
non-empty preference list, do the following:

0. Consider the favourite player of :math:`p` and call them :math:`q`.

1. If :math:`q` is presently holding a proposal from (i.e. is matched to)
   another player, :math:`p'`, drop the proposal. Let :math:`p` propose to
   :math:`q` so that :math:`M(q) = p`.

2. For each successor, :math:`s`, to :math:`p` in the preference list of
   :math:`q`, delete the pair :math:`(s, q)` from the game.

This phase of the algorithm will terminate either with every player holding a
proposal from one other player, or with exactly one player having an empty
preference list. The latter case occurs when an individual has been rejected by
every other player (during Step 2) and indicates that no stable matching exists.
In the case of the former, the second phase can be carried out so long as there
exists at least one player with a preference list containing more than one
element.

Phase 2
+++++++

The second phase finds and removes all of the all-or-nothing cycles (rotations)
from the game. An all-or-nothing cycle represents a series of matches that would
immediately result in a blocking pair being formed, hence their removal.

An all-or-nothing cycle is a chain of players where the links in the chain
alternate between a player's second choice and that player's worst choice. Once
a player has appeared twice as the worst choice for some player(s), a cycle has
been found. All cycles begin by taking any player in the game with a second
choice in their preference list as the first worst choice.

Based on an all-or-nothing cycle :math:`(x_1, y_1), \\ldots, (x_n, y_n)`, for
each :math:`i = 1, \\ldots, n`, one must delete from the game all pairs
:math:`(y_i, z)` such that :math:`y_i` prefers :math:`x_{i-1}` to :math:`z`
where subscripts are taken modulo :math:`n`.

This is an important point that is omitted from the original paper, but may be
found in :cite:`GI89`.

The essential difference between this statement and that in :cite:`Irv85` is the
removal of unpreferable pairs, identified using an all-or-nothing cycle, in
addition to those contained in the cycle. Without doing so, tails of cycles can
be removed rather than whole cycles, leaving some conflicting pairs in the game.

At the end of this phase, each player has at most one player in their preference
list. Matching each player to the player in the their preference list will
result in a stable matching. If any player has an empty list, then no stable
matching exists for the game. 
