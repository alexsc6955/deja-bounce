"""
Paddle entity for Deja Bounce.
"""

from __future__ import annotations

from mini_arcade_core.engine.entities import BaseEntity

from deja_bounce.entities.entity_id import EntityId


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
            }
        )
