"""Composite strategies for SM unit tests."""

from hypothesis import strategies as st

from ..common import st_single_ranks, st_single_utilities


@st.composite
def st_ranks(draw, pmin=1, pmax=5):
    """Create a set of rankings for a test."""

    size = draw(st.integers(pmin, pmax))
    suitor_ranks = draw(st_single_ranks(size))
    reviewer_ranks = draw(st_single_ranks(size))

    return suitor_ranks, reviewer_ranks


@st.composite
def st_player_ranks(draw, pmin=1, pmax=5):
    """Create a set of ranks, and choose a player from it."""

    suitor_ranks, reviewer_ranks = draw(st_ranks(pmin, pmax))
    side = draw(st.sampled_from(("suitor", "reviewer")))
    side_ranks = suitor_ranks if side == "suitor" else reviewer_ranks
    player, ranks = draw(st.sampled_from(list(enumerate(side_ranks))))

    return suitor_ranks, reviewer_ranks, player, ranks, side


@st.composite
def st_utilities(draw, pmin=1, pmax=5):
    """Create a set of utility matrices."""

    size = draw(st.integers(pmin, pmax))
    suitor_utility = draw(st_single_utilities(size))
    reviewer_utility = draw(st_single_utilities(size))

    return suitor_utility, reviewer_utility


@st.composite
def st_preferences(draw, pmin=1, pmax=5):
    """Create a set of preferences for a test."""

    size = draw(st.integers(pmin, pmax))
    suitors, reviewers = (
        draw(st.lists(elements, min_size=size, max_size=size, unique=True))
        for elements in (st.integers(), st.text())
    )

    suitor_prefs = {s: draw(st.permutations(reviewers)) for s in suitors}
    reviewer_prefs = {r: draw(st.permutations(suitors)) for r in reviewers}

    return suitor_prefs, reviewer_prefs


@st.composite
def st_preference_matchings(draw, pmin=1, pmax=5):
    """Create a set of preferences and a matching to go with them."""

    suitor_prefs, reviewer_prefs = draw(st_preferences(pmin, pmax))
    matching = dict(
        zip(
            range(len(reviewer_prefs)),
            draw(st.permutations(list(range(len(suitor_prefs))))),
        )
    )

    return suitor_prefs, reviewer_prefs, matching
