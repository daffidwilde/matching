""" The base game class for facilitating and solving matching games. """
import abc
import warnings

from matching.exceptions import (
    CapacityChangedWarning,
    PlayerExcludedWarning,
    PreferencesChangedWarning,
)


class BaseGame(metaclass=abc.ABCMeta):
    """ An abstract base class for facilitating various matching games.

    Attributes
    ----------
    matching : None
        Initialised to be :code:`None`. After solving the game,
        a :code:`Matching` object is found here.
    blocking_pairs : None
        Initialised to be :code:`None`. After solving and checking the stability
        of the game instance, a list of any pairs that block the stability of
        the matching.
    clean : bool
        Defaults to :code:`False`. When passing a set of players to create a
        game instance, this allows for the automatic cleaning of the players.
    """

    def __init__(self, clean=False):

        self.matching = None
        self.blocking_pairs = None
        self.clean = clean

    def _remove_player(self, player, player_party, other_party):
        """ Remove a player from the game and any relevant preference lists. """

        party = vars(self)[player_party][:]
        party.remove(player)
        vars(self)[player_party].remove(player)
        for other in vars(self)[other_party]:
            if player in other.prefs:
                other.forget(player)

    def _check_inputs_player_prefs_unique(self, party):
        """ Check that each player in :code:`party` has not ranked another
        player more than once. If so, and :code:`clean` is :code:`True`, then
        take the first instance they appear in the preference list. """

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
        """ Check that each player in :code:`party` has ranked only players in
        :code:`other_party`. If :code:`clean`, then forget any extra
        preferences. """

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
                        player.forget(other)

    def _check_inputs_player_prefs_nonempty(self, party, other_party):
        """ Make sure that each player in :code:`party` has a nonempty
        preference list of players in :code:`other_party`. If :code:`clean`,
        remove any such player. """

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
