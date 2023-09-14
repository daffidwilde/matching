"""Abstract base classes for inheritance."""

import abc
import warnings

from matching.exceptions import (
    PlayerExcludedWarning,
    PreferencesChangedWarning,
)


class BasePlayer:
    """An abstract base class to represent a player within a matching game.

    Parameters
    ----------
    name : object
        An identifier. This should be unique and descriptive.

    Attributes
    ----------
    prefs : List[BasePlayer]
        The player's preferences. Defaults to ``None`` and is updated using the
        ``set_prefs`` method.
    matching : Optional[BasePlayer]
        The current match of the player. ``None`` if not currently matched.
    _pref_names : Optional[List]
        A list of the names in ``prefs``. Updates with ``prefs`` via
        ``set_prefs`` method.
    _original_prefs : Optional[List[BasePlayer]]
        The original set of player preferences. Defaults to ``None`` and does
        not update after the first ``set_prefs`` method call.
    """

    def __init__(self, name):
        self.name = name
        self.prefs = []
        self.matching = None

        self._pref_names = []
        self._original_prefs = None

    def __repr__(self):
        return str(self.name)

    def _forget(self, other):
        """Forget another player by removing them from the player's preference
        list."""

        self.prefs = [p for p in self.prefs if p != other]

    def unmatched_message(self):
        """Message to say the player is not matched."""

        return f"{self} is unmatched."

    def not_in_preferences_message(self, other):
        """Message to say another player is an unacceptable match."""

        return (
            f"{self} is matched to {other} but they do not appear in their "
            f"preference list: {self.prefs}."
        )

    def set_prefs(self, players):
        """Set the player's preferences to be a list of players."""

        self.prefs = players
        self._pref_names = [player.name for player in players]

        if self._original_prefs is None:
            self._original_prefs = players[:]

    def prefers(self, player, other):
        """Determines whether the player prefers a player over some other
        player."""

        prefs = self._original_prefs
        return prefs.index(player) < prefs.index(other)

    @abc.abstractmethod
    def _match(self, other):
        """Placeholder for matching the player to another."""

    @abc.abstractmethod
    def _unmatch(self, other):
        """Placeholder for unmatching the player from another."""

    @abc.abstractmethod
    def get_favourite(self):
        """Placeholder for getting the player's favourite player."""

    @abc.abstractmethod
    def get_successors(self):
        """Placeholder for getting the successors of a match."""

    @abc.abstractmethod
    def check_if_match_is_unacceptable(self):
        """Placeholder for checking player's match is acceptable."""


class BaseGame(metaclass=abc.ABCMeta):
    """An abstract base class for facilitating various matching games.

    Parameters
    ----------
    clean : bool
        Defaults to ``False``. If ``True``, when passing a set of
        players to create a game instance, they will be automatically
        cleaned.

    Attributes
    ----------
    matching : BaseMatching or None
        After solving the game, an object whose class inherits from
        ``BaseMatching`` is found here. Otherwise, ``None``.
    blocking_pairs : list of (BasePlayer, BasePlayer) or None
        After checking the stability of the game instance, a list of any
        pairs that block the stability of the matching is found here.
        Otherwise, ``None``.
    """

    def __init__(self, clean=False):
        self.matching = None
        self.blocking_pairs = None
        self.clean = clean

    def _remove_player(self, player, player_party, other_party):
        """Remove a player from the game.

        This method also removes the player from any relevant player
        preference lists, removing their memory from the game.
        """

        party = getattr(self, player_party)[:]
        setattr(self, player_party, [p for p in party if p != player])
        for other in getattr(self, other_party):
            if player in other.prefs:
                other._forget(player)

    def _check_inputs_player_prefs_unique(self, party):
        """Check that noone has ranked another player more than once.

        If so, and ``clean`` is ``True``, then take the first instance
        they appear in the preference list.
        """

        for player in vars(self)[party]:
            unique_prefs = []
            for other in player.prefs:
                if other not in unique_prefs:
                    unique_prefs.append(other)
                else:
                    warnings.warn(
                        PreferencesChangedWarning(
                            f"{player} has ranked {other} multiple times."
                        )
                    )

            if self.clean:
                player.set_prefs(unique_prefs)

    def _check_inputs_player_prefs_all_in_party(self, party, other_party):
        """Check that everyone has ranked a subset of the other party.

        If ``clean`` is ``True``, then forget any extra preferences.
        """

        players = vars(self)[party]
        others = vars(self)[other_party]
        for player in players:
            for other in player.prefs:
                if other not in others:
                    warnings.warn(
                        PreferencesChangedWarning(
                            f"{player} has ranked a non-{other_party[:-1]}: "
                            f"{other}."
                        )
                    )
                    if self.clean:
                        player._forget(other)

    def _check_inputs_player_prefs_nonempty(self, party, other_party):
        """Check that everyone has a nonempty preference list.

        If ``clean`` is ``True``, remove any player with an empty list.
        """

        for player in vars(self)[party]:
            if not player.prefs:
                warnings.warn(
                    PlayerExcludedWarning(
                        f"{player} has an empty preference list."
                    )
                )
                if self.clean:
                    self._remove_player(player, party, other_party)

    @abc.abstractmethod
    def solve(self):
        """Placeholder for solving the game instance."""

    @abc.abstractmethod
    def check_stability(self):
        """Placeholder for checking the stability of the matching."""

    @abc.abstractmethod
    def check_validity(self):
        """Placeholder for checking the validity of the matching."""


class BaseMatching(dict, metaclass=abc.ABCMeta):
    """An abstract base class for storing and updating a matching.

    Attributes
    ----------
    dictionary : dict or None
        If not ``None``, a dictionary mapping a ``Player`` to one of:
        ``None``, a single ``Player`` or a list of ``Player`` instances.
    """

    def __init__(self, dictionary=None):
        self._data = {}
        if dictionary is not None:
            self._data.update(dictionary)

        super().__init__(self._data)

    def __repr__(self):
        return repr(self._data)

    def keys(self):
        """Get the underlying dictionary keys."""

        return self._data.keys()

    def values(self):
        """Get the underlying dictionary values."""

        return self._data.values()

    def __getitem__(self, player):
        return self._data[player]

    @abc.abstractmethod
    def __setitem__(self, player, new_match):
        """A placeholder function for how to update the matching."""

    def _check_player_in_keys(self, player):
        """Raise an error if ``player`` is not in the dictionary."""

        if player not in self._data.keys():
            raise ValueError(f"{player} is not a key in this matching.")

    def _check_new_valid_type(self, new, types):
        """Ensure ``new`` is an instance of one of ``types``."""

        if not isinstance(new, types):
            raise ValueError(f"{new} is not one of {types} and is not valid.")
