""" Hypothesis decorators for unit tests. """

from hypothesis import given
from hypothesis.strategies import lists, text

PLAYER = given(name=text(), pref_names=lists(text(), min_size=1, unique=True))
