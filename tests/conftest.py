"""Configuration for tests."""

from hypothesis import settings

settings.register_profile("ci", deadline=6000)
