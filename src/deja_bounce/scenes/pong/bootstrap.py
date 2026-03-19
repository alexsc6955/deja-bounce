"""
Bootstrap helpers for Pong scene setup.
"""

from __future__ import annotations

from typing import Any

from deja_bounce.entities import Ball, DottedLine, EntityId, Paddle
from deja_bounce.scenes.pong.models import PongWorld


def build_pong_world(
    *,
    viewport: tuple[float, float],
    entity_cfg: dict[str, Any],
) -> PongWorld:
    """
    Build the initial Pong world and gameplay entities.
    """
    dotted_center_line = DottedLine.build_from_template(
        EntityId.CENTER_LINE,
        str(
            (entity_cfg.get("center_line", {}) or {}).get(
                "name", "Dotted Center Line"
            )
        ),
        entity_cfg.get("center_line", {}) or {},
        viewport=viewport,
    )
    left_paddle = Paddle.build_from_template(
        EntityId.LEFT_PADDLE,
        str(
            (entity_cfg.get("left_paddle", {}) or {}).get(
                "name", "Left Paddle"
            )
        ),
        entity_cfg.get("left_paddle", {}) or {},
        viewport=viewport,
    )
    right_paddle = Paddle.build_from_template(
        EntityId.RIGHT_PADDLE,
        str(
            (entity_cfg.get("right_paddle", {}) or {}).get(
                "name", "Right Paddle"
            )
        ),
        entity_cfg.get("right_paddle", {}) or {},
        viewport=viewport,
    )
    ball_cfg = entity_cfg.get("ball", {}) or {}
    ball = Ball.build_from_template(
        EntityId.BALL,
        str(ball_cfg.get("name", "Ball")),
        ball_cfg,
        viewport=viewport,
    )
    reset_speed_cfg = ball_cfg.get("reset_speed", {}) or {}

    return PongWorld(
        entities=[
            left_paddle,
            right_paddle,
            ball,
            dotted_center_line,
        ],
        viewport=viewport,
        ball_spawn_position=(
            float(ball.transform.center.x),
            float(ball.transform.center.y),
        ),
        ball_reset_speed=(
            float(reset_speed_cfg.get("x", 250.0)),
            float(reset_speed_cfg.get("y", 200.0)),
        ),
    )


__all__ = ["build_pong_world"]
