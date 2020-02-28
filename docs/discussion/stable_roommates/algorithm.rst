The algorithm
-------------

Robert Irving presented an efficient algorithm for finding a stable matching to
SR in :cite:`Irv85` if one exists. The algorithm comes in two phases:

Phase 1
+++++++

The first phase of the algorithm consists of one-way proposals (we still refer
to these as matches here) and removes unpreferable pairs from the game. Begin by
assigning all players to be unmatched and without any proposals. Then, for each
player :math:`p \in P`, do the following:

0. Consider the favourite player of :math:`p` and call them :math:`q`.

1. If :math:`q` is presently unmatched, set :math:`M(q) = p`. Move to 4.
   Otherwise, get :math:`p' = M(q)` and go to 2.

2. If :math:`q` prefers :math:`p` to :math:`p'`, set :math:`M(q) = p` and delete
   the pair :math:`(q, p')` from the game by removing them from each other's
   preference lists. Otherwise, delete the pair :math:`(q, p)`.

3. If :math:`q` has not already been marked as "proposed to" or :math:`f(p)` is
   now empty, move onto the next player and record :math:`q` as being "proposed
   to". Otherwise, go to 0.

Phase 2
+++++++

The second phase finds and removes all of the all-or-nothing cycles (rotations)
from the game. The preference lists at the end form a matching.

An all-or-nothing cycle is a chain of players where the links in the chain
alternate between a player's second choice and that player's worst choice. Once
a player has appeared twice as the worst choice for some player(s), a cycle has
been found and each link in the chain is removed from the game. All cycles begin
by taking any player in the game with a second choice in their preference
list as the first worst choice.

At the end of this phase, each player has at most one player in their preference
list. Matching each player to the player in the their preference list will
result in a stable matching. If any player has an empty list, then no stable
matching exists for the game. 
