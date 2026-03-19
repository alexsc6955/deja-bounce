"""
Paddle entity for Deja Bounce.
"""

from __future__ import annotations

from typing import Any

from mini_arcade_core.engine.entities import BaseEntity
from mini_arcade_core.scenes.entity_blueprints import build_entity_payload

from deja_bounce.entities.entity_id import EntityId


def _paddle_tags(entity_id: EntityId) -> tuple[str, ...]:
    if int(entity_id) == int(EntityId.LEFT_PADDLE):
        return ("paddle", "left_paddle")
    if int(entity_id) == int(EntityId.RIGHT_PADDLE):
        return ("paddle", "right_paddle")
    return ("paddle",)


class Paddle(BaseEntity):
    """
    Paddle entity for the Pong scene.
    """

    paddle_size: tuple[float, float] = (20.0, 100.0)

    @staticmethod
    def build(entity_id: EntityId, name: str, x: float, vh: float) -> Paddle:
        """Build a new Paddle entity."""
        pad_w, pad_h = Paddle.paddle_size
        y = (vh - pad_h) / 2
        return Paddle.from_dict(
            {
                "id": entity_id,
                "name": name,
                "transform": {
                    "center": {"x": x, "y": y},
                    "size": {"width": pad_w, "height": pad_h},
                },
                "shape": {
                    "kind": "rect",
                },
                "collider": {
                    "kind": "rect",
                },
                "kinematic": {
                    "velocity": {"vx": 0.0, "vy": 0.0},
                    "acceleration": {"ax": 0.0, "ay": 0.0},
                    "max_speed": 300.0,
                },
                "style": {
                    "fill": (255, 255, 255, 255),
                },
                "tags": list(_paddle_tags(entity_id)),
            }
        )

    @staticmethod
    def build_from_template(
        entity_id: EntityId,
        name: str,
        template: dict[str, Any],
        *,
        viewport: tuple[float, float],
    ) -> "Paddle":
        """Build a paddle entity from a template plus runtime overrides."""

        payload = build_entity_payload(
            template,
            viewport=viewport,
            overrides={
                "id": int(entity_id),
                "name": name,
                "tags": list(_paddle_tags(entity_id)),
            },
        )
        return Paddle.from_dict(payload)
