"""
System pipeline helpers for Pong scene setup.
"""

from __future__ import annotations

from deja_bounce.controllers.cpu import CpuPaddleController
from deja_bounce.scenes.pong.systems import (
    BallMotionBundle,
    CpuIntentSystem,
    PaddleMovementBundle,
    PongCollisionSystem,
    PongRulesSystem,
    PongTimeScaleSystem,
    PongTrailCaptureSystem,
)


def build_pong_systems(
    *,
    cpu_controller: CpuPaddleController,
    services,
) -> tuple[object, ...]:
    """
    Build the ordered gameplay systems for Pong.
    """
    return (
        PongTimeScaleSystem(),
        CpuIntentSystem(controller=cpu_controller),
        PaddleMovementBundle(),
        BallMotionBundle(),
        PongTrailCaptureSystem(),
        PongCollisionSystem(services),
        PongRulesSystem(),
    )


__all__ = ["build_pong_systems"]
