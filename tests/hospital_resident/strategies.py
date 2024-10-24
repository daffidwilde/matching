"""Composite strategies for HR unit tests."""

import numpy as np
from hypothesis import strategies as st

from ..common import st_single_ranks


@st.composite
def st_ranks_capacities(draw, hmin=1, hmax=3, rmin=1, rmax=5):
    """Create a set of rankings and capacities for a test."""

    hsize = draw(st.integers(hmin, hmax))
    rsize = draw(st.integers(rmin, rmax))

    resident_ranks = draw(st_single_ranks(rsize, hsize))
    hospital_ranks = draw(st_single_ranks(hsize, rsize))
    capacities = draw(
        st.lists(st.integers(1, 3), min_size=hsize, max_size=hsize)
    )

    return resident_ranks, hospital_ranks, np.array(capacities)
