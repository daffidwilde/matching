# The hospital-resident assignment problem {#hospital-resident}

The hospital-resident assignment problem (HR) is an extension of SM
where residents must be assigned to placements at hospitals.

## Key definitions

### The game

Consider two distinct sets, $R$ and $H$, and let us refer to them as
residents and hospitals. Each hospital $h \in H$ has a capacity
associated with them $c_h \in \mathbb{N}$.

As in SM, each player has a preference list associated with them but
they needn\'t be exhaustive of the other party. Instead:

-   Each resident $r \in R$ must rank a non-empty subset of $H$. We
    denote this preference by $f(r)$.
-   Each hospital $h \in H$ must rank **all** those residents that have
    ranked it. That is, the preference list of $h$, denoted by $g(h)$,
    is a permutation of the set given by $\left\{r \in R \ | \ h \in
    f(r)\right\}$. If no residents rank a hospital then that hospital is
    removed from $H$.

This construction of residents, hospitals, capacities and preference
lists is a game and is denoted by $(R,H)$. This game is used to model
instances of HR.

### Matching

A matching $M$ is any mapping between $R$ and $H$. If a pair
$(r, h) \in R \times H$ are matched in $M$, we say that $M(r) = h$ and
$r \in M^{-1}(h)$.

A matching is only considered valid if **all** of the following are
satisfied:

> 1.  For all $r \in R$ with a match we have $M(r) \in f(r)$.
> 2.  For all $h \in H$ with matches we have $M^{-1}(h) \subseteq g(h)$.
> 3.  For all $h \in H$ we have $|M^{-1}(h)| \leq c_h$.

Again, a valid matching is considered stable if it does not contain any
blocking pairs.

### Blocking pair

A pair $(r, h)$ is said to block a matching $M$ if **all** the following
hold:

> 1.  There is mutual preference, i.e. $r \in g(h)$ **and**
>     $h \in f(r)$.
> 2.  Either $r$ is unmatched or they prefer $h$ to $M(r) = h'$.
> 3.  Either $|M^{-1}(h)| < c_h$ or $h$ prefers $r$ to at least one
>     $r' \in M^{-1}(h)$.

The notion of preference here is the same as in SM.

## An example

Consider the following instance of HR. There are five residents -- Ada,
Sam, Jo, Luc, Dani -- applying to work at three hospitals: Mercy, City,
General. Each hospital has two available positions, and the players\'
preferences of one another are described in the graph below:

![image](../assets/discussion/hr_matching.svg){.align-center width="80.0%"}

As with SM, this representation is a easy way to keep track of the
current state of the problem and the relationships between players.
Consider the matching presented below:

![image](../assets/discussion/hr_invalid.svg){.align-center width="80.0%"}

This matching is invalid. In fact, none of the conditions for validity
have been met: City hospital is over-subscribed and Ada has been
assigned to a hospital that they did not rank (likewise for Mercy). Some
slight tinkering can produce a valid matching:

![image](../assets/discussion/hr_unstable.svg){.align-center width="80.0%"}

Even with this, the matching is not stable. There exists one blocking
pair: $(L, M)$. Here, there is mutual preference, Luc prefers Mercy to
General and Mercy has a space remaining. Hence, a stable solution would
be as follows:

![image](../assets/discussion/hr_stable.svg){.align-center width="80.0%"}

It also so happens that this matching is both resident- and
hospital-optimal.

## The algorithm

Finding optimal, stable matchings for HR is of great importance as it
solves real-world problems. For instance, the [National Resident
Matching Program](http://www.nrmp.org) uses an algorithm like the one
presented here to assign medical students in the US to hospitals. An
algorithm which solves HR was originally presented in
`GS62`{.interpreted-text role="cite"} but further work was done to
improve on these algorithms in later years `DF81`{.interpreted-text
role="cite"}, `Rot84`{.interpreted-text role="cite"}. Unlike the
algorithm for SM, this algorithm takes a different form depending on the
desired optimality of the solution.

Below are resident-optimal and hospital-optimal algorithms for finding a
unique, stable matching for an instance of HR. Each algorithm was taken
from `GI89`{.interpreted-text role="cite"}.

### Resident-optimal

0.  Assign all residents to be unmatched, and all hospitals to be
    totally unsubscribed.
1.  Take any unmatched resident with a non-empty preference list $r$,
    and consider their most preferred hospital $h$. Match them to one
    another.
2.  If $|M^{-1}(h)| > c_h$, find the worst resident $r'$ assigned to $h$
    and unmatch the pair $(r', h)$.
3.  If $|M^{-1}(h)| = c_h$, find the worst resident $r'$ assigned to
    $h$. Then, for each successor $s \in g(h)$ to $r'$, delete the pair
    $(s, h)$ from the game by removing $h$ from $f(s)$ and $s$ from
    $g(h)$.
4.  Go to 1 until there are no such residents left, then end.

### Hospital-optimal

0.  Set all residents to be unmatched, and all hospitals to be totally
    unsubscribed.
1.  Take any hospital $h$ that is under-subscribed and whose preference
    list contains any resident they are not currently assigned to, and
    consider their most preferred such resident $r$.
2.  If $r$ is currently matched to some other hospital $h'$, then
    unmatch them from one another.
3.  Match $r$ with $h$.
4.  For each successor $s \in f(r)$ to $h$, delete the pair $(r, s)$
    from the game.
5.  Go to 1 until there are no such hospitals left, then end.
