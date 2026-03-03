"""
Module defining game commands for Deja Bounce.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from mini_arcade_core.engine.commands import Command, CommandContext
from mini_arcade_core.spaces.math.vec2 import Vec2
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
        context.managers.scenes.push("pause", as_overlay=True)


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

            # Restore saved velocities for refactored entity-based Pong world.
            try:
                from deja_bounce.entities import EntityId

                ball = world.get_entity_by_id(EntityId.BALL)
                left = world.get_entity_by_id(EntityId.LEFT_PADDLE)
                right = world.get_entity_by_id(EntityId.RIGHT_PADDLE)

                if (
                    ball is not None
                    and ball.kinematic is not None
                    and world.saved_ball_vel is not None
                ):
                    ball.kinematic.velocity = Vec2(
                        world.saved_ball_vel.vx, world.saved_ball_vel.vy
                    )

                if (
                    left is not None
                    and left.kinematic is not None
                    and world.saved_left_vel is not None
                ):
                    left.kinematic.velocity = Vec2(
                        world.saved_left_vel.vx, world.saved_left_vel.vy
                    )

                if (
                    right is not None
                    and right.kinematic is not None
                    and world.saved_right_vel is not None
                ):
                    right.kinematic.velocity = Vec2(
                        world.saved_right_vel.vx, world.saved_right_vel.vy
                    )
            except Exception:  # noqa: BLE001 - keep pause resume resilient
                logger.exception("Failed to restore saved velocities on resume")

        context.services.scenes.pop()


class BackToMenuCommand(Command):
    """
    Command to return to the main menu from pause.
    """

    def execute(self, context: CommandContext):
        context.managers.scenes.change("menu")
