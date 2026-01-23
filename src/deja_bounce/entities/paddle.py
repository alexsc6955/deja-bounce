"""
Paddle entity for Deja Bounce.
"""

from __future__ import annotations

from dataclasses import dataclass

from mini_arcade_core.spaces.d2.collision2d import RectCollider
from mini_arcade_core.spaces.d2.geometry2d import Position2D, Size2D
from mini_arcade_core.spaces.d2.physics2d import Velocity2D


@dataclass
class Paddle:
    """
    Paddle entity for the Pong scene.

    :ivar position (Position2D): Position of the paddle.
    :ivar size (Size2D): Size of the paddle.
    :ivar velocity (Velocity2D): Velocity of the paddle.
    :ivar speed (float): Movement speed of the paddle.
    """

    position: Position2D
    size: Size2D
    velocity: Velocity2D
    speed: float = 300.0

    @property
    def collider(self) -> RectCollider:
        """Collider for the paddle."""
        return RectCollider(self.position, self.size)
