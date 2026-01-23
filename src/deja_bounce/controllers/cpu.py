"""
Minimal CPU paddle controller for Deja Bounce.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Literal

from deja_bounce.entities import Ball, Paddle

Side = Literal["LEFT", "RIGHT"]


@dataclass
class CpuConfig:
    """
    Basic CPU difficulty settings.

    - max_speed: how fast the CPU paddle can move (units/sec)
    - dead_zone: how close to the ball center before it stops moving
    """

    max_speed: float = 65.0  # slower - easier
    dead_zone: float = (
        16.0  # larger dead_zone = CPU "overshoots" less, more human = easier
    )
    reaction_distance: float = 180.0
    error_margin: float = 24.0
    inertia_factor: float = 1.0  # optional future use


class CpuPaddleController:
    """
    Very simple CPU:
    - Looks at the ball's center Y.
    - Moves paddle up/down to follow it, clamped by max_speed.
    """

    def __init__(
        self,
        paddle: Paddle,
        ball: Ball,
        *,
        side: Side = "RIGHT",
        config: CpuConfig | None = None,
    ):
        """
        :param paddle: The paddle to control.
        :type paddle: Paddle

        :param ball: The ball to track.
        :type ball: Ball

        :param config: The CPU configuration settings.
        :type config: CpuConfig, optional
        """
        self.paddle = paddle
        self.ball = ball
        self.side = side
        self.config = config or CpuConfig()

        # Make sure paddle speed matches CPU config so movement feels consistent
        self.paddle.speed = self.config.max_speed
        self._aim_offset_y = self._new_offset()

    def _new_offset(self) -> float:
        # vertical error in [-error_margin, error_margin]
        m = self.config.error_margin
        return random.uniform(-m, m) if m > 0 else 0.0

    def compute_move(self) -> float:
        """
        Decide paddle move direction:
            -1.0 = up
            0.0 = stop
            +1.0 = down
        """
        vx = self.ball.velocity.vx

        # React only when ball is moving toward this paddle
        if self.side == "RIGHT" and vx <= 0:
            return 0.0
        if self.side == "LEFT" and vx >= 0:
            return 0.0

        # Side-correct X distance check
        if self.side == "RIGHT":
            distance_x = self.paddle.position.x - (
                self.ball.position.x + self.ball.size.width
            )
        else:
            distance_x = self.ball.position.x - (
                self.paddle.position.x + self.paddle.size.width
            )

        # Too far away? don't react
        if distance_x > self.config.reaction_distance:
            return 0.0

        # Aim with error
        ball_center_y = (
            self.ball.position.y
            + self.ball.size.height / 2
            + self._aim_offset_y
        )
        paddle_center_y = self.paddle.position.y + self.paddle.size.height / 2
        diff = ball_center_y - paddle_center_y

        # Dead zone = "human jitter reduction"
        if abs(diff) < self.config.dead_zone:
            return 0.0

        return 1.0 if diff > 0 else -1.0
