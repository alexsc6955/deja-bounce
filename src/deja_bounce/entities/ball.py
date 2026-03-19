"""
Ball entity for the Pong scene.
"""

from __future__ import annotations

import random
from typing import Any

from mini_arcade_core.engine.entities import BaseEntity
from mini_arcade_core.scenes.entity_blueprints import build_entity_payload

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
                "tags": ["ball"],
            }
        )

    @staticmethod
    def build_from_template(
        entity_id: EntityId,
        name: str,
        template: dict[str, Any],
        *,
        viewport: tuple[float, float],
    ) -> "Ball":
        """Build a ball entity from a template plus runtime overrides."""

        payload = build_entity_payload(
            template,
            viewport=viewport,
            overrides={
                "id": int(entity_id),
                "name": name,
                "tags": ["ball"],
            },
        )
        kinematic = payload.get("kinematic", {}) or {}
        velocity_choices = kinematic.pop("velocity_choices", {}) or {}
        x_choices = velocity_choices.get("x", [])
        y_choices = velocity_choices.get("y", [])
        velocity = kinematic.get("velocity", {}) or {}
        if isinstance(x_choices, list) and x_choices:
            velocity["vx"] = float(random.choice(x_choices))
        if isinstance(y_choices, list) and y_choices:
            velocity["vy"] = float(random.choice(y_choices))
        kinematic["velocity"] = velocity
        payload["kinematic"] = kinematic
        return Ball.from_dict(payload)
