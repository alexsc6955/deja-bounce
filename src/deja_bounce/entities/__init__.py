"""
Entities package for Deja Bounce application.
This package contains all entity definitions used in the game.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from mini_arcade_core.engine.entities import BaseEntity

from .ball import Ball
from .entity_id import EntityId
from .paddle import Paddle


class DottedLine(BaseEntity):
    """
    Dotted line entity for the Pong scene.
    """

    thickness: float = 5

    @staticmethod
    def build(
        entity_id: EntityId, name: str, vw: float, vh: float
    ) -> DottedLine:
        """Build a new DottedLine entity."""
        thickness = DottedLine.thickness
        x = vw / 2
        y = vh / 2
        return DottedLine.from_dict(
            {
                "id": entity_id,
                "name": name,
                "transform": {
                    "center": {"x": x, "y": y},
                    "size": {"width": 4.0, "height": vh},
                },
                "shape": {
                    "kind": "line",
                    "a": {"x": 0.0, "y": -vh / 2},
                    "b": {"x": 0.0, "y": vh / 2},
                    "dash": {"length": 16.0, "gap": 12.0},
                },
                "style": {
                    "stroke": {
                        "color": (200, 200, 200, 255),
                        "thickness": thickness,
                    },
                },
            }
        )


__all__ = [
    "EntityId",
    "Ball",
    "Paddle",
    "DottedLine",
]
