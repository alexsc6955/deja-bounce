"""
Ball entity for the Pong scene.
"""

from __future__ import annotations

from dataclasses import dataclass

from mini_arcade_core.spaces.d2.geometry2d import (
    Position2D,
    Size2D,
)

from mini_arcade_core.spaces.d2.collision2d import RectCollider
from mini_arcade_core.spaces.d2.physics2d import Velocity2D


@dataclass
class Ball:
    """
    Ball entity for the Pong scene.

    :ivar position (Position2D): Position of the ball.
    :ivar size (Size2D): Size of the ball.
    :ivar velocity (Velocity2D): Velocity of the ball.
    :ivar speed (float): Speed of the ball.
    """

    position: Position2D
    size: Size2D
    velocity: Velocity2D
    speed: float = 400.0

    @property
    def collider(self) -> RectCollider:
        """Collider for the ball."""
        return RectCollider(self.position, self.size)
