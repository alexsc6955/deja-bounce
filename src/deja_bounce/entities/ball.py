"""
Ball entity for the Pong scene.
"""

from __future__ import annotations

import random

from mini_arcade_core.engine.entities import BaseEntity

from deja_bounce.entities.entity_id import EntityId


class Ball(BaseEntity):
    """
    Ball entity for the Pong scene.
    """

    @staticmethod
    def build(entity_id: EntityId, name: str, vw: float, vh: float) -> Ball:
        """Build a new Ball entity."""
        bw, bh = 10.0, 10.0
        vx = 250.0 * random.choice((-1.0, 1.0))
        vy = 200.0 * random.choice((-1.0, 1.0))
        return Ball.from_dict(
            {
                "id": entity_id,
                "name": name,
                "transform": {
                    "center": {"x": vw / 2 - bw / 2, "y": vh / 2 - bh / 2},
                    "size": {"width": bw, "height": bh},
                },
                "shape": {
                    "kind": "rect",
                },
                "collider": {
                    "kind": "rect",
                },
                "kinematic": {
                    "velocity": {"vx": vx, "vy": vy},
                    "acceleration": {"ax": 0.0, "ay": 0.0},
                    "max_speed": 0.0,
                },
                "style": {
                    "fill": (255, 255, 255, 255),
                },
            }
        )
