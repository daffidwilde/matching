# The student-allocation problem {#student-allocation}

The student-allocation problem (SA) is concerned with the allocation of
students to projects and their supervisors.

In this kind of problem there are technically three sets of players, although
supervisors and their projects act together as a set of players.

Supervisors hold preferences over the students and pass them onto their
projects. Like HR, this set of players have capacities, allowing for projects
of different sizes and offering flexibility to supervisors.

## Key definitions

### The game

Consider three distinct sets, $S$, $P$ and $U$, and let us refer to them
as students, projects and supervisors. Each project $p \in
P$ has a single supervisor $u \in U$ associated with them. This
association is described as a surjective function $L: P \to U$ where the
supervisor $u \in U$ for a project $p \in P$ can be written as
$L(p) = u$. Note that as $L$ is surjective, $u$ may have multiple
projects associated with them and we denote their set of projects as
$L^{-1}(u)$.

In addition to this, each project $p \in P$ and supervisor $u \in U$ has
a capacity associated with them, denoted $c_p, c_u \in \mathbb{N}$
respectively. We assume that for each $u \in U$ the following holds:

$$\max\left\{ c_p \ | \ p \in L^{-1}(u) \right\}
\leq c_u \leq
\sum_{p \in L^{-1}(u)} c_p$$

That is, a supervisor must be able to accommodate their largest project
but not offer more spaces than their projects sum to.

As with other matching games, each player has a preference list
associated with them. In the case of SA, we have the following
constraints on those preferences:

-   Each student $s \in S$ must rank a non-empty subset of $P$. We
    denote this preference by $f(s)$.
-   Each supervisor $u \in U$ must rank **all** those students that have
    ranked **at least one** of their projects. That is, the preference
    list of $u$, denoted $g(u)$, is a permutation of the set given by
    $\left\{ s \in S \ | \ L^{-1}(u) \cap f(s) \neq \emptyset \right\}$.
    If no students have ranked any of a supervisor\'s projects then that
    supervisor is removed from $U$.
-   The preference list of a project $p \in P$ is governed by its
    supervisor $u = L(p)$. We denote this preference as $g_p(u)$ and it
    is simply $g(u)$ without the students who did not rank $p$. If no
    students have ranked a project then that project is removed from
    $P$.

This construction of students, projects, supervisors, associations,
capacities and preference lists is a game and is denoted by $(S,P,U)$.
This game is used to model instances of SA.

### Matching

A matching $M$ is any mapping between $S$ and $P$. If a pair
$(s, p) \in S \times P$ are matched in $M$, we say that $M(s)
= p$ and $s \in M^{-1}(p)$. We also note that since each supervisor
$u \in U$ oversees their projects (by definition), their matching can be
referred to as the union of its projects\' matchings:

$$M^{-1}(u) = \bigcup_{p \in L^{-1}(u)} M^{-1}(p) \subseteq S$$

A matching is only considered valid if **all** of the following are
satisfied:

> 1.  For all $s \in S$ with a match we have $M(s) \in f(s)$.
> 2.  For all $p \in P$ we have $M^{-1}(p) \subseteq g_p(u)$ and
>     $|M^{-1}(p)| \leq c_p$.
> 3.  For all $u \in U$ we have $M^{-1}(u) \subseteq g(u)$ and
>     $|M^{-1}(u)| \leq c_u$.

As always, a valid matching is considered stable if it does not contain
any blocking pairs.

### Blocking pair

A pair $(s, p)$ is said to block a matching $M$ if **all** the following
hold:

> 1.  The student has a preference of the project, i.e. $p \in f(s)$.
>
> 2.  Either $s$ is unmatched or they prefer $p$ to $M(s) = p'$.
>
> 3.  At least one of the following is true, where $u = L(p)$:
>
>     > -   Both $p$ and $u$ are under-subscribed, i.e.
>     >     $|M^{-1}(p)| < c_p$ and $|M^{-1}(u)| < c_u$.
>     > -   $|M^{-1}(p)| < c_p$ and $|M^{-1}(u)| = c_u$, and either
>     >     $M(s) = p' \in L^{-1}(u)$ or $u$ prefers $s$ to their worst
>     >     current match $s' \in M^{-1}(u)$.
>     > -   $|M^{-1}(p)| = c_p$ and $u$ prefers $s$ to the project\'s
>     >     worst student $s \in M^{-1}(p)$.

The notion of preference is equivalent to that in SM.

## An example

Consider the following instance of SA. There are five students - Avery,
Blake, Cleo, Devon, Everest - in their final year of university. As part
of this year, they may apply to do a project. There are two members of
staff providing these projects - Dr. Xavier and Prof. Yeo. Each
supervisor may take at most three students and each offer two projects
with space for two students on each. The players\' preferences are
described in the graph below:

![image](../assets/discussion/sa_matching.svg){.align-center width="90.0%"}

Note that in this particular example, the students are ranked in the
same order by both supervisors (as is often the case in real-world
applications of SA). Now consider the matching below:

![image](../assets/discussion/sa_invalid.svg){.align-center width="90.0%"}

This matching is invalid, and none of the conditions for validity have
been met. Specifically:

-   Avery has been allocated Dr. Yeo\'s first project despite not
    ranking it (and likewise for Dr. Yeo and the project)
-   Dr. Yeo\'s first project has been allocated a total of three
    students which exceeds its capacity of two.
-   In addition to this, Dr. Yeo has been allocated a fourth student,
    violating their capacity constraint.

With a few changes, we can make this matching valid. Swapping Avery and
Cleo with Devon is a start since they are Dr. Xavier\'s favourite
students after Blake. Then we can move Devon to Y2 as this is their most
preferred project. Doing this gives the following matching:

![image](../assets/discussion/sa_unstable.svg){.align-center width="90.0%"}

Unfortunately, and despite our efforts to accommodate people\'s
preferences, this matching is not stable. Here we have two blocking
pairs, $(E, X2)$ and $(E, Y2)$. Although Everest prefers X1 to either of
these projects, they do not form a blocking pair as X1 is full and Dr.
Xavier prefers Avery and Cleo to Everest.

So, in order to overcome these blocking pairs without creating more,
Devon must be swapped with Everest. This also feels like the fairest
move given that Everest outranks Devon. The following graph displays
this new, stable matching:

![image](../assets/discussion/sa_stable.svg){.align-center width="90.0%"}

It also happens that this matching is student-optimal as well as being
stable and valid.

## The algorithm

Finding stable and optimal solutions to SA is easily motivated since
those solutions would solve the real-world problem they model. Actually
implementing this in the real world is described in more detail in [this
tutorial](../../tutorials/student_allocation.ipynb).

As with HR, there are two algorithms implemented in Matching to solve
instances of SA, one to handle the optimality of each party (students
and project/supervisors). These algorithms, taken from
`AIM07`{.interpreted-text role="cite"}, follow a similar structure to
those for HR in that they take advantage of the inherent structure of
the game. Again, each party-optimal algorithm provides a unique, stable
matching for an instance of SA.

### Student-optimal

0.  Assign all students to be unmatched, and all supervisors (and their
    projects) to be totally unsubscribed.
1.  Take any student $s$ that is unmatched and has a non-empty
    preference list, and consider their most preferred project $p$. Let
    $u =
    L(p)$. Assign $s$ to be matched to $p$ (and thus $u$).
2.  If $p$ is over-subscribed, find its worst current match $s'$.
    Unmatch $p$ and $s'$. Else if $u$ is over-subscribed, find their
    worst current match $s'$ and the project $p'$ that $s'$ is assigned
    to. Unmatch $p'$ and $s'$.
3.  If $p$ is at capacity, find their worst current match $s'$. For each
    successor $t \in g_p(u)$ to $s'$, delete the pair $(t,
    p)$ from the game by removing $p$ from $f(t)$ and $t$ from $g(u)$
    (and thus $g_p(u)$).
4.  If $u$ is at capacity, find their worst current match $s'$. For each
    successor $t \in g(u)$ to $s'$, delete the pair $(t,
    p)$ from the game.
5.  Go to 1 until there are no such students left, then end.

### Supervisor-optimal

0.  Assign all students to be unmatched, and all supervisors (and their
    projects) to be totally unsubscribed.
1.  Take any supervisor $u$ that is under-subscribed and whose
    preference list contains at least one student that is not currently
    matched to at least one acceptable (though currently
    under-subscribed) project offered by $u$. Consider the supervisor\'s
    most preferred such student $s$ and that student\'s most preferred
    such project $p$.
2.  If $s$ is matched to some other project $p'$ then unmatch them.
3.  Assign $s$ to be matched to $p$ (and thus $u$).
4.  For each successor $p' \in f(s)$ to $p$, delete the pair $(s, p')$
    from the game.
5.  Go to 1 until there are no such supervisors, then end.
