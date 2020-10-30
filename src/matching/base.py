""" Abstract base classes for inheritance. """
import abc
import warnings

from matching.exceptions import PlayerExcludedWarning, PreferencesChangedWarning


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

        prefs = self.prefs[:]
        prefs.remove(other)
        self.prefs = prefs

    def unmatched_message(self):

        return f"{self} is unmatched."

    def not_in_preferences_message(self, other):

        return (
            f"{self} is matched to {other} but they do not appear in their "
            f"preference list: {self.prefs}."
        )

    def set_prefs(self, players):
        """ Set the player's preferences to be a list of players. """

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
        """A placeholder function for assigning the player to be matched to
        some other player."""

    @abc.abstractmethod
    def _unmatch(self, other):
        """A placeholder function for unassigning the player from its match
        with some other player."""

    @abc.abstractmethod
    def get_favourite(self):
        """A placeholder function for getting the player's favourite, feasible
        player."""

    @abc.abstractmethod
    def get_successors(self):
        """A placeholder function for getting the logically feasible
        'successors' of the player."""

    @abc.abstractmethod
    def check_if_match_is_unacceptable(self):
        """A placeholder for chacking the acceptability of the current
        match(es) of the player."""


class BaseGame(metaclass=abc.ABCMeta):
    """An abstract base class for facilitating various matching games.

    Parameters
    ----------
    clean
        Defaults to :code:`False`. If :code:`True`, when passing a set of
        players to create a game instance, they will be automatically cleaned.

    Attributes
    ----------
    matching
        After solving the game, a :code:`Matching` object is found here.
        Otherwise, :code:`None`.
    blocking_pairs
        After checking the stability of the game instance, a list of any pairs
        that block the stability of the matching is found here. Otherwise,
        :code:`None`.
    """

    def __init__(self, clean=False):

        self.matching = None
        self.blocking_pairs = None
        self.clean = clean

    def _remove_player(self, player, player_party, other_party):
        """Remove a player from the game instance as well as any relevant
        player preference lists."""

        party = vars(self)[player_party][:]
        party.remove(player)
        vars(self)[player_party].remove(player)
        for other in vars(self)[other_party]:
            if player in other.prefs:
                other._forget(player)

    def _check_inputs_player_prefs_unique(self, party):
        """Check that each player in :code:`party` has not ranked another
        player more than once. If so, and :code:`clean` is :code:`True`, then
        take the first instance they appear in the preference list."""

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
        """Check that each player in :code:`party` has ranked only players in
        :code:`other_party`. If :code:`clean`, then forget any extra
        preferences."""

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
        """Make sure that each player in :code:`party` has a nonempty
        preference list of players in :code:`other_party`. If :code:`clean`,
        remove any such player."""

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
        """ Placeholder for solving the given matching game. """

    @abc.abstractmethod
    def check_stability(self):
        """ Placeholder for checking the stability of the current matching. """

    @abc.abstractmethod
    def check_validity(self):
        """ Placeholder for checking the validity of the current matching. """


class BaseMatching(dict, metaclass=abc.ABCMeta):
    """An abstract base class for the storing and updating of a matching.

    Attributes
    ----------
    dictionary : dict or None
        If not ``None``, a dictionary mapping a ``Player`` to one of: ``None``,
        a single ``Player`` or a list of ``Player`` instances.
    """

    def __init__(self, dictionary=None):

        self._data = {}
        if dictionary is not None:
            self._data.update(dictionary)

        super().__init__(self._data)

    def __repr__(self):

        return repr(self._data)

    def keys(self):

        return self._data.keys()

    def values(self):

        return self._data.values()

    def __getitem__(self, player):

        return self._data[player]

    @abc.abstractmethod
    def __setitem__(self, player, new_match):
        """ A placeholder function for how to update the matching. """

    def _check_player_in_keys(self, player):
        """ Raise an error if :code:`player` is not in the dictionary. """

        if player not in self._data.keys():
            raise ValueError(f"{player} is not a key in this matching.")

    def _check_new_valid_type(self, new, types):
        """Raise an error is :code:`new` is not an instance of one of
        :code:`types`."""

        if not isinstance(new, types):
            raise ValueError(f"{new} is not one of {types} and is not valid.")
