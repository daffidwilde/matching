# The stable roommates problem {#stable-roommates}

The stable roommates problem (SR) describes the problem of finding a
stable matching of pairs from one even-sized set of players, all of
whom have a complete preference of the remaining players.

## Key definitions

### The game

Consider a set of $N$ players $P$ where $N$ is even. Each player in $P$
has a ranking of all other players in $P$, and we call this ranking
their preference list.

We can consider the preference lists of each player as a function which
produces tuples. We denote this function as $f$ where:

$$f : P \to P^{N-1}$$

This construction of players and their preference lists is called a game
of size $N$, and is denoted by $P$. This game is used to model instances
of SR.

### Matching

A matching $M$ is any pairing of the elements of $P$. If a pair
$(p,q) \in P \times P$ are matched in $M$, then we say that $M(p) = q$
and, equivalently, $M(q) = p$.

A matching is only considered valid if all players in $P$ are uniquely
matched with exactly one other player.

### Blocking pair

A pair $(p,q)$ is said to block a matching $M$ if **all** of the
following hold:

> 1.  Both $p$ and $q$ have a match in $M$.
> 2.  $p$ prefers $q$ to $M(p) = q'$.
> 3.  $q$ prefers $p$ to $M(q) = p'$.

The notions of preference and stability here are the same as in SM.

## An example

Consider the instance of SR below. Here there are six people looking to
bunk together on a school trip - Alex, Bowie, Carter, Dallas, Evelyn and
Finn. Their preferences of one another are described in the graph below:

![image](../assets/discussion/sr_matching.svg){.align-center width="80.0%"}

In this representation, a valid matching $M$ creates a 1-regular graph.
Again, this graphical representation makes it easy to see the current
relationships between the players. Consider the matching below:

![image](../assets/discussion/sr_unstable.svg){.align-center width="80.0%"}

Here we can see that players $C$ and $F$ would rather be matched to one
another than their current matches, $D$ and $E$ respectively. Thus,
$(C, F)$ are a blocking pair in this matching and the matching is
unstable. We can attempt to rectify this instability by swapping these
pairs over:

![image](../assets/discussion/sr_stable.svg){.align-center width="80.0%"}

Despite this move actually making $D$ worse off, there are no players
they envy where the feeling is reciprocated under this matching. With
that, there are no blocking pairs and this matching is stable.

## The algorithm

Robert Irving presented an efficient, two-phase algorithm for finding a
stable matching to SR in `Irv85`{.interpreted-text role="cite"}, if one
exists. An extended form of the algorithm was presented in
`GI89`{.interpreted-text role="cite"}, and is given below.

### Phase 1

The first phase of the algorithm consists of one-way proposals (we still
refer to these as matches here) and removes unpreferable pairs from the
game. Begin by assigning all players to be unmatched and without any
proposals. Then, while there is a player, $p$, who does not have a held
proposal and has a non-empty preference list, do the following:

0.  Consider the favourite player of $p$ and call them $q$.
1.  If $q$ is presently holding a proposal from (i.e. is matched to)
    another player, $p'$, drop the proposal. Let $p$ propose to $q$ so
    that $M(q) = p$.
2.  For each successor, $s$, to $p$ in the preference list of $q$,
    delete the pair $(s, q)$ from the game.

This phase of the algorithm will terminate either with every player
holding a proposal from one other player, or with exactly one player
having an empty preference list. The latter case occurs when an
individual has been rejected by every other player (during Step 2) and
indicates that no stable matching exists. In the case of the former, the
second phase can be carried out so long as there exists at least one
player with a preference list containing more than one element.

### Phase 2

The second phase finds and removes all of the all-or-nothing cycles
(rotations) from the game. An all-or-nothing cycle represents a series
of matches that would immediately result in a blocking pair being
formed, hence their removal.

An all-or-nothing cycle is a chain of players where the links in the
chain alternate between a player\'s second choice and that player\'s
worst choice. Once a player has appeared twice as the worst choice for
some player(s), a cycle has been found. All cycles begin by taking any
player in the game with a second choice in their preference list as the
first worst choice.

Based on an all-or-nothing cycle $(x_1, y_1), \ldots, (x_n, y_n)$, for
each $i = 1, \ldots, n$, one must delete from the game all pairs
$(y_i, z)$ such that $y_i$ prefers $x_{i-1}$ to $z$ where subscripts are
taken modulo $n$.

This is an important point that is omitted from the original paper, but
may be found in `GI89`{.interpreted-text role="cite"}.

The essential difference between this statement and that in
`Irv85`{.interpreted-text role="cite"} is the removal of unpreferable
pairs, identified using an all-or-nothing cycle, in addition to those
contained in the cycle. Without doing so, tails of cycles can be removed
rather than whole cycles, leaving some conflicting pairs in the game.

At the end of this phase, each player has at most one player in their
preference list. Matching each player to the player in the their
preference list will result in a stable matching. If any player has an
empty list, then no stable matching exists for the game.
