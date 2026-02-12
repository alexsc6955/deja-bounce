"""
Pong scene Model
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Deque

from mini_arcade_core.scenes.sim_scene import (  # pyright: ignore[reportMissingImports]
    BaseIntent,
    BaseTickContext,
    BaseWorld,
)
from mini_arcade_core.spaces.d2.physics2d import Velocity2D

from deja_bounce.entities.ball import Ball
from deja_bounce.entities.paddle import Paddle


@dataclass
class ScoreState:
    """
    Score state for the Pong scene.

    :ivar left (int): Score for the left player.
    :ivar right (int): Score for the right player.
    """

    left: int = 0
    right: int = 0


# Justification: many attributes needed for world state
# pylint: disable=too-many-instance-attributes
@dataclass
class PongWorld(BaseWorld):
    """
    Pong world state.

    :ivar viewport (tuple[float, float]): Viewport size (width, height).
    :ivar left_paddle (Paddle): Left paddle entity.
    :ivar right_paddle (Paddle): Right paddle entity.
    :ivar ball (Ball): Ball entity.
    :ivar score (ScoreState): Current score state.
    """

    viewport: tuple[float, float]
    left_paddle: Paddle
    right_paddle: Paddle
    ball: Ball
    score: ScoreState
    paused: bool = False

    # snapshot to restore after pause
    saved_ball_vel: Velocity2D | None = None
    saved_left_vel: Velocity2D | None = None
    saved_right_vel: Velocity2D | None = None

    god_mode_p1: bool = False
    god_mode_p2: bool = False

    slow_mo: bool = False
    slow_ball: bool = False
    slow_mo_scale: float = 0.25

    trail_mode: bool = False
    trail: Deque[tuple[float, float]] = field(
        default_factory=lambda: deque(maxlen=30)
    )


@dataclass(frozen=True)
class PongIntent(BaseIntent):
    """
    Player intent for the Pong scene.

    :ivar move_left_paddle (float): Movement intent for left paddle (-1.0 to +1.0).
    :ivar move_right_paddle (float): Movement intent for right paddle (-1.0 to +1.0).
    :ivar serve (bool): Whether to serve the ball.
    :ivar pause (bool): Whether to pause the game.
    """

    move_left_paddle: float  # -1.0 (up) to +1.0 (down)
    move_right_paddle: float  # -1.0 (up) to +1.0 (down)
    pause: bool = False

    toggle_slow_mo: bool = False
    toggle_trail: bool = False
    screenshot: bool = False
    replay_recording: bool = False
    play_replay: bool = False
    video_recording: bool = False


# pylint: enable=too-many-instance-attributes


@dataclass
class PongTickContext(BaseTickContext[PongWorld, PongIntent]):
    """
    Context for a Pong scene tick.

    :ivar input_frame (InputFrame): Current input frame.
    :ivar dt (float): Delta time since last tick.

    :ivar world (PongWorld): Current Pong world state.
    :ivar commands (CommandQueue): Command queue.

    :ivar intent (Optional[PongIntent]): Player intent for this tick.
    :ivar packet (Optional[RenderPacket]): Render packet for this tick.
    """
