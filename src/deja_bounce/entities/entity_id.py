"""
Entity definitions for the Deja Bounce game.
This
"""

from __future__ import annotations

from enum import IntEnum


class EntityId(IntEnum):
    """
    Entity IDs for the Pong scene.

    :cvar CENTER_LINE: ID for the center line entity.
    :cvar LEFT_PADDLE: ID for the left paddle entity.
    :cvar RIGHT_PADDLE: ID for the right paddle entity.
    :cvar BALL: ID for the ball entity.
    """

    CENTER_LINE = 1
    LEFT_PADDLE = 2
    RIGHT_PADDLE = 3
    BALL = 4
