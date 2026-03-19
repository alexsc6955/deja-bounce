"""
Module defining game commands for Deja Bounce.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from mini_arcade_core.engine.commands import (
    Command,
    CommandContext,
    PushSceneIfMissingCommand,
    RemoveSceneCommand,
)
from mini_arcade_core.engine.scenes.models import ScenePolicy
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
        context.managers.scenes.change("pong")


class CycleDifficultyCommand(Command):
    """BaseCommand to cycle the game difficulty."""

    levels = list(DIFFICULTY_PRESETS.keys())

    def execute(
        self,
        context: CommandContext,
    ):
        difficulty = getattr(context.settings, "difficulty", None)
        if difficulty is None or not hasattr(difficulty, "level"):
            return

        current = str(difficulty.level).lower()
        idx = self.levels.index(current) if current in self.levels else 0
        difficulty.level = self.levels[(idx + 1) % len(self.levels)]


class PauseGameCommand(Command):
    """
    Command to pause the game.
    """

    def execute(self, context: CommandContext):
        PushSceneIfMissingCommand(
            "pause",
            as_overlay=True,
            policy=ScenePolicy(
                blocks_update=True,
                blocks_input=True,
                is_opaque=False,
                receives_input=True,
            ),
        ).execute(context)


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
        RemoveSceneCommand("pause").execute(context)


class BackToMenuCommand(Command):
    """
    Command to return to the main menu from pause.
    """

    def execute(self, context: CommandContext):
        context.managers.scenes.change("menu")
