"""
Rendering system for Pong scene.
"""

from __future__ import annotations

from dataclasses import dataclass

from mini_arcade_core.scenes.systems.builtins import (
    ConfiguredQueuedRenderSystem,
    RenderOverlay,
)
from mini_arcade_core.scenes.systems.phases import SystemPhase

from deja_bounce.scenes.pong.draw_ops import DrawScore, DrawTrail
from deja_bounce.scenes.pong.models import PongTickContext


@dataclass
class PongRenderSystem(ConfiguredQueuedRenderSystem[PongTickContext]):
    """
    Declarative Pong renderer: default world rendering plus score/trail overlays.
    """

    name: str = "min_render"
    phase: int = SystemPhase.RENDERING
    order: int = 100
    overlays: tuple[RenderOverlay[PongTickContext], ...] = (
        RenderOverlay.from_drawable(DrawTrail(), layer="world", z=20),
        RenderOverlay.from_drawable(DrawScore(), layer="ui", z=90),
    )
