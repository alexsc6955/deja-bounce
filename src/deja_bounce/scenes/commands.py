"""
Module defining game commands for Deja Bounce.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from mini_arcade_core.engine.commands import Command, CommandContext
from mini_arcade_core.utils import logger

from deja_bounce.difficulty import DIFFICULTY_PRESETS

if TYPE_CHECKING:
    from deja_bounce.scenes.pong import PongScene


Player = Literal["P1", "P2"]


class StartGameCommand(Command):
    """BaseCommand to start the game."""

    def execute(
        self,
        context: CommandContext,
    ):
        context.services.scenes.change("pong")


class CycleDifficultyCommand(Command):
    """BaseCommand to cycle the game difficulty."""

    levels = list(DIFFICULTY_PRESETS.keys())
    settings: object

    def execute(
        self,
        context: CommandContext,
    ):
        current = context.settings.difficulty
        idx = self.levels.index(current) if current in self.levels else 0
        context.settings.difficulty = self.levels[(idx + 1) % len(self.levels)]


class PauseGameCommand(Command):
    """
    Command to pause the game.
    """

    def execute(self, context: CommandContext):
        context.services.scenes.push("pause", as_overlay=True)


class GodModeCommand(Command):
    """
    Command to toggle god mode in PongScene.
    """

    def __init__(self, player: Player):
        """
        :param player: "P1" or "P2
        :type player: Player
        """
        self.player = player  # "P1" or "P2"

    def execute(self, context: CommandContext):
        logger.info(f"Toggling god mode for {self.player}")
        if self.player == "P1":
            context.world.god_mode_p1 = not context.world.god_mode_p1
        elif self.player == "P2":
            context.world.god_mode_p2 = not context.world.god_mode_p2


class SlowMoCommand(Command):
    """
    Command to toggle slow motion mode in PongScene.
    """

    def execute(self, context: CommandContext):
        context.world.slow_ball = not context.world.slow_ball


class ToggleTrailCommand(Command):
    """Toggle trail mode in PongWorld."""

    def execute(self, context: CommandContext):
        world = context.world
        if world is None:
            return

        # only works if world has trail_mode
        if not hasattr(world, "trail_mode"):
            return

        world.trail_mode = not world.trail_mode
        if not world.trail_mode and hasattr(world, "trail"):
            world.trail.clear()


class ScreenshotCommand(Command):
    """Capture a screenshot using RuntimeServices.capture."""

    def __init__(self, label: str = "pong"):
        self.label = label

    def execute(self, context: CommandContext):
        path = context.services.capture.screenshot(label=self.label)
        logger.info(f"Saved screenshot: {path}")


class ToggleSlowMoCommand(Command):
    """Toggle slow motion mode in PongWorld."""

    def execute(self, context: CommandContext):
        world = context.world
        if world is None:
            return

        world.slow_mo = not world.slow_mo


class ContinueCommand(Command):
    """
    Command to continue the game from pause.
    """

    def execute(self, context: CommandContext):
        world = context.world
        if world is not None:
            world.paused = False
            logger.info("Resuming game from pause")

            if world.saved_ball_vel is not None:
                world.ball.velocity = world.saved_ball_vel
            if world.saved_left_vel is not None:
                world.left_paddle.velocity = world.saved_left_vel
            if world.saved_right_vel is not None:
                world.right_paddle.velocity = world.saved_right_vel

        context.services.scenes.pop()


class BackToMenuCommand(Command):
    """
    Command to return to the main menu from pause.
    """

    def execute(self, context: CommandContext):
        context.services.scenes.change("menu")
