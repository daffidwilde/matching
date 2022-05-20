""" Tests for the BaseGame class. """
import warnings

from hypothesis import given
from hypothesis.strategies import booleans

from matching import BaseGame, Player
from matching.exceptions import PlayerExcludedWarning, PreferencesChangedWarning

from .util import player_others


class DummyGame(BaseGame):
    def solve(self):
        pass

    def check_stability(self):
        pass

    def check_validity(self):
        pass


@given(clean=booleans())
def test_init(clean):
    """Make a BaseGame instance and test it has the correct attributes."""

    game = DummyGame(clean)

    assert isinstance(game, BaseGame)
    assert game.matching is None
    assert game.blocking_pairs is None
    assert game.clean is clean


@given(player_others=player_others())
def test_remove_player(player_others):
    """Test that a player can be removed from a game and its players."""

    player, others = player_others

    player.set_prefs(others)
    for other in others:
        other.set_prefs([player])

    game = DummyGame()
    game.players = [player]
    game.others = others

    game._remove_player(player, "players", "others")
    assert player not in game.players
    assert all(player not in other.prefs for other in game.others)


@given(player_others=player_others(), clean=booleans())
def test_check_inputs_player_prefs_unique(player_others, clean):
    """Test that a game can verify its players have unique preferences."""

    player, others = player_others

    player.set_prefs(others + others[:1])

    game = DummyGame(clean)
    game.players = [player]

    with warnings.catch_warnings(record=True) as w:
        game._check_inputs_player_prefs_unique("players")

        message = w[-1].message
        assert isinstance(message, PreferencesChangedWarning)
        assert str(message).startswith(player.name)
        assert others[0].name in str(message)
        if clean:
            assert player._pref_names == [o.name for o in others]


@given(player_others=player_others(), clean=booleans())
def test_check_inputs_player_prefs_all_in_party(player_others, clean):
    """ " Test that a game can verify its players have only got preferences in
    the correct party."""

    player, others = player_others

    outsider = Player("foo")
    player.set_prefs([outsider])

    game = DummyGame(clean)
    game.players = [player]
    game.others = others

    with warnings.catch_warnings(record=True) as w:
        game._check_inputs_player_prefs_all_in_party("players", "others")

        message = w[-1].message
        assert isinstance(message, PreferencesChangedWarning)
        assert str(message).startswith(player.name)
        assert "non-other" in str(message)
        assert outsider.name in str(message)
        if clean:
            assert outsider not in player.prefs


@given(player_others=player_others(), clean=booleans())
def test_check_inputs_player_prefs_nonempty(player_others, clean):
    """ " Test that a game can verify its players have got nonempty preference
    lists."""

    player, others = player_others

    player.set_prefs(others)
    other = others[0]

    game = DummyGame(clean)
    game.players = [player]
    game.others = [other]

    with warnings.catch_warnings(record=True) as w:
        game._check_inputs_player_prefs_nonempty("others", "players")

        message = w[-1].message
        assert isinstance(message, PlayerExcludedWarning)
        assert str(message).startswith(other.name)

        if clean:
            assert other not in game.others
            assert player.prefs == others[1:]
