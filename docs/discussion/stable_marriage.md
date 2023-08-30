# The stable marriage problem {#stable-marriage}

The stable marriage problem (SM) describes the problem of finding a
stable matching between two distinct, equally sized sets of players with
complete preferences.

## Key definitions

### The game

Consider two distinct sets, $S$ and $R$, each of size $N$, and let us
refer to these sets as suitors and reviewers respectively. Each element
of $S$ and $R$ has a ranking of all the other set's elements associated
with it, and we call this ranking their preference list.

We can consider the preference lists for the elements of each set as a
function which produces tuples. We call these functions $f$ and $g$
respectively:

$$f : S \to R^N; \quad g : R \to S^N$$

This construction of suitors, reviewers and preference lists is called a
game of size $N$, and is denoted by $(S,R)$. This game is used to model
instances of SM.

### Matching

A matching $M$ is any bijection between $S$ and $R$. If a pair
$(s,r) \in S \times R$ are matched in $M$, then we say that $M(s) = r$
and, equivalently, $M^{−1}(r) = s$.

### Preference

Let $(S, R)$ be an instance of SM. Consider $s \in S$ and $r,
r' \in R$. We say that $s$ prefers $r$ to $r'$ if $r$ appears before
$r'$ in $f(s)$. The definition is equivalent for reviewers.

### Blocking pair

A pair $(s,r)$ is said to block a matching $M$ if **all** of the
following hold:

1.  $s$ and $r$ aren't matched by $M$, i.e. $M(s) \neq
    r$.
2.  $s$ prefers $r$ to $M(s) = r'$.
3.  $r$ prefers $s$ to $M^{-1}(r) = s′$.

### Stable matching

A matching $M$ is said to be stable if it contains no blocking pairs,
and unstable otherwise.

## An example

Consider the unsolved matching game of size three shown below as an
edgeless graph with suitors on the left and reviewers on the right.
Beside each vertex is the name of the player and their associated
ranking of the complementary set's elements:

![image](../assets/discussion/sm_matching.svg){.align-center width="80.0%"}

In this representation, a matching $M$ creates a bipartite graph where
an edge between two vertices (players) indicates that they are matched
by $M$. Consider the matching shown below:

![image](../assets/discussion/sm_unstable.svg){.align-center width="80.0%"}

Here we can see that players $A$, $C$ and $F$ are matched to their
favourite player but $B$, $D$ and $E$ are matched to their least
favourite. There's nothing particularly special about that but we can
see that players $B$ and $D$ form a blocking pair given that they would
both rather be matched with one another than with their current match.
Hence, this matching is unstable.

We can attempt to rectify this instability by swapping the matches for
the first two rows:

![image](../assets/discussion/sm_stable.svg){.align-center width="80.0%"}

Upon closer inspection, we can see that each suitor is now matched with
their most preferred reviewer so as not to form a blocking pair that
would upset any current matchings. This matching is stable and is
considered *suitor-optimal*.

## The algorithm

David Gale and Lloyd Shapley presented an algorithm for solving SM in
@GS62. The algorithm provides a unique,
stable, suitor-optimal matching for any instance of SM. A more
efficient, robust extension of the original algorithm, taken from
@GI89, is given below.

0.  Assign all suitors and reviewers to be unmatched.
1.  Take any suitor $s$ that is not currently matched, and consider
    their favourite reviewer $r$.
2.  If $r$ is matched, get their current match $s' = M^{-1}(r)$ and
    unmatch the pair.
3.  Match $s$ and $r$, i.e. set $M(s) = r$.
4.  For each successor, $t$, to $s$ in $g(r)$, delete the pair $(t, r)$
    from the game by removing $r$ from $f(t)$ and $t$ from $g(r)$.
5.  Go to 1 until there are no such suitors, then end.

::: {.callout-tip}
## Reviewer-optimal algorithm
As the game requires equally sized sets of players, the
*reviewer-optimal* algorithm is equivalent to the above but with the
roles of suitors and reviewers reversed.
:::
