"""A module for converting between different data structures."""

import numpy as np
from scipy.stats import rankdata


def preference_to_rank(preference, others):
    """Convert a preference dictionary to a rank array."""

    rank = np.array(
        [[others.index(o) for o in prefs] for prefs in preference.values()]
    )

    return rank


def utility_to_rank(utility):
    """Convert a utility array to a rank array."""

    rank = rankdata(-utility, method="ordinal", axis=1, nan_policy="omit")

    return rank - 1
