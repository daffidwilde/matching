"""A module for converting between different data structures."""

import numpy as np
from scipy.stats import rankdata


def preference_to_rank(preferences, others):
    """Convert a preference list dictionary to a rank array."""

    sorted_preferences = sorted(preferences.items(), key=lambda x: x[0])
    sorted_others = sorted(others)
    ranks = [
        [prefs.index(o) if o in prefs else len(others) for o in sorted_others]
        for _, prefs in sorted_preferences
    ]

    return np.array(ranks)


def utility_to_rank(utility):
    """Convert a utility array to a rank array."""

    rank = rankdata(-utility, method="ordinal", axis=1, nan_policy="omit")

    return rank - 1
