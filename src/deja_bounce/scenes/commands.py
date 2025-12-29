"""
Module defining game commands for Deja Bounce.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from mini_arcade_core import (
    BaseCommand,
    BaseGameCommand,
    BaseSceneCommand,
    QuitGameCommand,
)
from mini_arcade_core.game import Game
from mini_arcade_core.managers import BaseCheatCommand

from deja_bounce.constants import ROOT
from deja_bounce.difficulty import DIFFICULTY_PRESETS
from deja_bounce.entities.paddle import Paddle
from deja_bounce.scenes.models import PongModel

if TYPE_CHECKING:
    from deja_bounce.scenes.pong import PongScene


Player = Literal["P1", "P2"]


class QuitCommand(QuitGameCommand):
    """
    Cheat command to quit the game.
    """


class StartGameCommand(BaseGameCommand):
    """BaseCommand to start the game."""

    def execute(self, context: Game) -> None:
        context.services.scenes.change("pong")


class CycleDifficultyCommand(BaseGameCommand):
    """BaseCommand to cycle the game difficulty."""

    levels = list(DIFFICULTY_PRESETS.keys())

    def execute(self, context: Game) -> None:
        current = context.settings.difficulty
        idx = self.levels.index(current) if current in self.levels else 0
        context.settings.difficulty = self.levels[(idx + 1) % len(self.levels)]


class EnableTrialModeCommand(BaseSceneCommand):
    """
    Command to toggle trial mode.
    """

    def execute(self, context: PongModel) -> None:
        context.trail_mode = not context.trail_mode


class PhotoModeCommand(BaseSceneCommand):
    """
    Command to toggle photo mode.
    """

    def execute(self, context: PongModel) -> None:
        context.photo_mode = not context.photo_mode


class PauseGameCommand(BaseGameCommand):
    """
    Command to pause the game.
    """

    def execute(self, context: Game) -> None:
        context.services.scenes.push("pause", as_overlay=True)


class MovePaddleCommand(BaseCommand):
    """
    Command to move a paddle up or down.
    """

    def __init__(self, paddle: Paddle, direction: str):
        self.paddle = paddle
        self.direction = direction  # "up" or "down"

    def execute(self, _context) -> None:
        if self.direction == "up":
            self.paddle.moving_up = True
        if self.direction == "down":
            self.paddle.moving_down = True


class StopPaddleCommand(BaseCommand):
    """
    Command to stop a paddle's movement.
    """

    def __init__(self, paddle: Paddle, direction: str):
        self.paddle = paddle
        self.direction = direction  # "up" or "down"

    def execute(self, _context) -> None:
        if self.direction == "up":
            self.paddle.moving_up = False
        if self.direction == "down":
            self.paddle.moving_down = False


class ScoreCommandExecutor:
    """
    Command executor to award score to a player.
    """

    def __init__(self, side: str):
        self.side = side  # "LEFT" or "RIGHT"

    def execute(self, context: PongModel):
        """
        Custom execution logic for scoring.

        :param context: PongModel context for command execution.
        :type context: PongModel
        """
        if self.side == "LEFT":
            context.score.left += 1
            context.reset_rally_direction = 1
        else:
            context.score.right += 1
            context.reset_rally_direction = -1
        ResetRallyCommand().execute(context)


class ScoreLeftCommand(BaseSceneCommand):
    """
    Command to award score to a player.
    """

    def execute(self, context: PongModel) -> None:
        ScoreCommandExecutor("LEFT").execute(context)


class ScoreRightCommand(BaseSceneCommand):
    """
    Command to award score to a player.
    """

    def execute(self, context: PongModel) -> None:
        ScoreCommandExecutor("RIGHT").execute(context)


class ResetRallyCommand(BaseSceneCommand):
    """
    Command to reset the rally after a score.
    """

    def execute(self, context: PongModel) -> None:
        context.reset_rally = not context.reset_rally


class GodModeCommand(BaseCheatCommand["PongScene"]):
    """
    Command to toggle god mode in PongScene.
    """

    def __init__(self, player: Player):
        """
        :param player: "P1" or "P2
        :type player: Player
        """
        super().__init__(enabled=True)
        self.player = player  # "P1" or "P2"

    def execute(self, context: "PongScene") -> None:
        if self.player == "P1":
            context.model.god_mode_p1 = not context.model.god_mode_p1
        elif self.player == "P2":
            context.model.god_mode_p2 = not context.model.god_mode_p2


class SlowMoCommand(BaseCheatCommand["PongScene"]):
    """
    Command to toggle slow motion mode in PongScene.
    """

    def execute(self, context: "PongScene") -> None:
        context.model.slow_mo = not context.model.slow_mo


class CpuVsCpuCommand(BaseCheatCommand["PongScene"]):
    """
    Command to toggle CPU vs CPU mode in PongScene.
    """

    def execute(self, context: "PongScene") -> None:
        context.model.cpu_vs_cpu = not context.model.cpu_vs_cpu


class SetWinnerCommandExecutor:
    """
    Command executor to set the winner of the game.
    """

    def __init__(self, player: Player):
        self.player = player  # "P1" or "P2"

    def execute(self, context: PongModel):
        """
        Custom execution logic for setting the winner.

        :param context: PongModel context for command execution.
        :type context: PongModel
        """
        context.winner = self.player


class SetWinnerP1Command(BaseSceneCommand):
    """
    Command to set player 1 as the winner.
    """

    def execute(self, context: PongModel) -> None:
        SetWinnerCommandExecutor("P1").execute(context)


class SetWinnerP2Command(BaseSceneCommand):
    """
    Command to set player 2 as the winner.
    """

    def execute(self, context: PongModel) -> None:
        SetWinnerCommandExecutor("P2").execute(context)


class TakeScreenshotCommand(BaseGameCommand):
    """
    Command to take a screenshot of the game.
    """

    def execute(self, context: Game) -> None:
        context.screenshot("screenshot.bmp", str(ROOT / "screenshots"))
