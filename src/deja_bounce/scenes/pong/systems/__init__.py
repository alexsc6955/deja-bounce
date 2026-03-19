"""
Pong scene systems.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from mini_arcade_core.runtime.services import RuntimeServices
from mini_arcade_core.scenes.systems import SystemBundle
from mini_arcade_core.scenes.systems.builtins import (
    AxisIntentBinding,
    IntentAxisVelocitySystem,
    KinematicMotionSystem,
    MotionBinding,
    ViewportConstraintBinding,
    ViewportConstraintSystem,
)
from mini_arcade_core.scenes.systems.phases import SystemPhase
from mini_arcade_core.spaces.collision.intersections import intersects_entities
from mini_arcade_core.spaces.d2.boundaries2d import VerticalBounce
from mini_arcade_core.spaces.geometry.bounds import Bounds2D
from mini_arcade_core.spaces.geometry.size import Size2D
from mini_arcade_core.spaces.math.vec2 import Vec2

from deja_bounce.controllers.cpu import CpuPaddleController
from deja_bounce.entities import Ball, EntityId, Paddle
from deja_bounce.scenes.commands import ToggleSlowMoCommand, ToggleTrailCommand
from deja_bounce.scenes.pong.models import PongIntent, PongTickContext
from deja_bounce.scenes.pong.systems.render import PongRenderSystem

__all__ = [
    "PongHotkeysSystem",
    "PongTimeScaleSystem",
    "CpuIntentSystem",
    "PaddleMovementBundle",
    "PaddleSystem",
    "BallMotionBundle",
    "BallMovementSystem",
    "PongTrailCaptureSystem",
    "PongCollisionSystem",
    "PongRulesSystem",
    "PongRenderSystem",
]


@dataclass
class PongHotkeysSystem:
    """Handles one-shot hotkeys (trail toggle, screenshot, etc.)."""

    name: str = "pong_hotkeys"
    phase: int = SystemPhase.CONTROL
    order: int = 13

    def _toggle_trail(self, ctx: PongTickContext):
        if ctx.intent.toggle_trail:
            ctx.commands.push(ToggleTrailCommand())

    def _toggle_slow_mo(self, ctx: PongTickContext):
        if ctx.intent.toggle_slow_mo:
            ctx.commands.push(ToggleSlowMoCommand())

    def step(self, ctx: PongTickContext):
        """Execute hotkey commands based on intent."""
        if ctx.intent is None:
            return

        self._toggle_trail(ctx)
        self._toggle_slow_mo(ctx)


# TODO: This is not implemented in the scene yet.
@dataclass
class PongTimeScaleSystem:
    """Applies time scaling (slow motion) to the simulation dt."""

    name: str = "pong_time_scale"
    phase: int = SystemPhase.CONTROL
    order: int = 11

    def step(self, ctx: PongTickContext):
        """Apply time scaling to the simulation dt."""
        if ctx.world.paused:
            return

        if ctx.world.slow_mo:
            ctx.dt *= ctx.world.slow_mo_scale


@dataclass
class CpuIntentSystem:
    """
    Simple CPU intent system for right paddle.
    """

    name: str = "pong_cpu_intent"
    phase: int = SystemPhase.CONTROL
    order: int = 15
    reaction_deadzone: float = 6.0
    controller: CpuPaddleController | None = None

    def enabled(self, _ctx: PongTickContext) -> bool:
        """Whether CPU control is enabled."""
        return self.controller is not None

    def step(self, ctx: PongTickContext):
        """Update intent for CPU-controlled paddle."""
        if not self.enabled(ctx) or ctx.intent is None:
            return

        move = self.controller.compute_move()
        ctx.intent = PongIntent(
            move_left_paddle=ctx.intent.move_left_paddle,
            move_right_paddle=move,
            pause=ctx.intent.pause,
        )


@dataclass
class PaddleMovementBundle(SystemBundle[PongTickContext]):
    """
    Bundle of processors that apply paddle intent, motion, and clamping.
    """

    _velocity: IntentAxisVelocitySystem[PongTickContext] = field(
        init=False,
        repr=False,
    )
    _motion: KinematicMotionSystem[PongTickContext] = field(
        init=False,
        repr=False,
    )
    _constraints: ViewportConstraintSystem[PongTickContext] = field(
        init=False,
        repr=False,
    )

    def __post_init__(self) -> None:
        def _enabled(ctx: PongTickContext) -> bool:
            return (not ctx.world.paused) and (ctx.intent is not None)

        def _left(ctx: PongTickContext):
            return ctx.world.left_paddle()

        def _right(ctx: PongTickContext):
            return ctx.world.right_paddle()

        def _paddles(ctx: PongTickContext):
            return tuple(
                entity
                for entity in (_left(ctx), _right(ctx))
                if entity is not None
            )

        self._velocity = IntentAxisVelocitySystem(
            enabled_when=_enabled,
            bindings=(
                AxisIntentBinding(
                    entity_getter=_left,
                    value_getter=lambda ctx: float(
                        ctx.intent.move_left_paddle
                    ),
                    axis="y",
                ),
                AxisIntentBinding(
                    entity_getter=_right,
                    value_getter=lambda ctx: float(
                        ctx.intent.move_right_paddle
                    ),
                    axis="y",
                ),
            ),
        )
        self._motion = KinematicMotionSystem(
            enabled_when=_enabled,
            bindings=(MotionBinding(entities_getter=_paddles),),
        )
        self._constraints = ViewportConstraintSystem(
            enabled_when=_enabled,
            bindings=(
                ViewportConstraintBinding(
                    entities_getter=_paddles,
                    policy="clamp",
                    axes=("y",),
                ),
            ),
        )

    def iter_systems(self) -> Iterable[object]:
        return (self._velocity, self._motion, self._constraints)


@dataclass
class BallMotionBundle(SystemBundle[PongTickContext]):
    """
    Bundle of processors that integrate ball motion.
    """

    _motion: KinematicMotionSystem[PongTickContext] = field(
        init=False,
        repr=False,
    )

    def __post_init__(self) -> None:
        self._motion = KinematicMotionSystem(
            enabled_when=lambda ctx: not ctx.world.paused,
            bindings=(
                MotionBinding(
                    entities_getter=lambda ctx: tuple(
                        entity
                        for entity in (ctx.world.ball(),)
                        if entity is not None
                    ),
                    dt_getter=lambda ctx, _entity: float(ctx.dt)
                    * (
                        float(ctx.world.slow_mo_scale)
                        if ctx.world.slow_ball
                        else 1.0
                    ),
                ),
            ),
        )

    def iter_systems(self) -> Iterable[object]:
        return (self._motion,)


PaddleSystem = PaddleMovementBundle
BallMovementSystem = BallMotionBundle


@dataclass
class PongTrailCaptureSystem:
    """Stores a ball trail when trail_mode is enabled."""

    name: str = "pong_trail_capture"
    phase: int = SystemPhase.PRESENTATION
    order: int = 35

    def step(self, ctx: PongTickContext):
        """Capture ball trail positions."""
        if ctx.world.paused:
            return
        if not ctx.world.trail_mode:
            return

        ball = ctx.world.ball()
        if ball is None:
            return
        ctx.world.trail.append(
            (ball.transform.center.x, ball.transform.center.y)
        )


@dataclass
class PongCollisionSystem:
    """
    Handle ball collisions with walls and paddles.
    """

    services: RuntimeServices
    name: str = "pong_collision"
    phase: int = SystemPhase.SIMULATION
    order: int = 40

    def _apply_paddle_influence(self, ball: Ball, paddle: Paddle):
        ball_center = ball.transform.center.y + ball.transform.size.height / 2
        paddle_center = (
            paddle.transform.center.y + paddle.transform.size.height / 2
        )
        offset = ball_center - paddle_center

        denom = (
            (paddle.transform.size.height / 2)
            if paddle.transform.size.height > 0
            else 1.0
        )
        norm = max(-1.0, min(1.0, offset / denom))

        base_vy = 220.0
        inertia_factor = 0.30
        max_vy = 400.0

        paddle_vy = (
            paddle.kinematic.velocity.y
            if paddle.kinematic is not None
            else 0.0
        )
        new_vy = norm * base_vy + paddle_vy * inertia_factor
        ball.kinematic.velocity.y = max(-max_vy, min(max_vy, new_vy))
        ball.kinematic.velocity.x *= 1.03

    def step(self, ctx: PongTickContext):
        """Handle ball collisions with walls and paddles."""
        if ctx.world.paused:
            return

        vw, vh = ctx.world.viewport
        ball = ctx.world.ball()
        left = ctx.world.left_paddle()
        right = ctx.world.right_paddle()
        if (
            ball is None
            or left is None
            or right is None
            or ball.kinematic is None
        ):
            return

        bounds = Bounds2D.from_size(Size2D(int(vw), int(vh)))
        bounced = VerticalBounce(bounds).apply(ball)
        if bounced:
            self.services.audio.play("wall_hit")

        vx = ball.kinematic.velocity.x
        if vx < 0:
            if intersects_entities(ball, left):
                ball.transform.center.x = (
                    left.transform.center.x + left.transform.size.width
                )
                ball.kinematic.velocity.x = abs(ball.kinematic.velocity.x)
                self._apply_paddle_influence(ball, left)
                self.services.audio.play("paddle_hit")
        elif vx > 0 and intersects_entities(ball, right):
            ball.transform.center.x = (
                right.transform.center.x - ball.transform.size.width
            )
            ball.kinematic.velocity.x = -abs(ball.kinematic.velocity.x)
            self._apply_paddle_influence(ball, right)
            self.services.audio.play("paddle_hit")


@dataclass
class PongRulesSystem:
    """
    Apply Pong rules: scoring, resetting ball, etc.
    """

    name: str = "pong_rules"
    phase: int = SystemPhase.SIMULATION
    order: int = 50

    def _bounce_from_left_goal(self, ball: Ball, _ctx: PongTickContext):
        ball.transform.center.x = 0.0
        ball.kinematic.velocity.x = abs(ball.kinematic.velocity.x) or 250.0

    def _bounce_from_right_goal(self, ball: Ball, ctx: PongTickContext):
        vw, _ = ctx.world.viewport
        bw, _ = ball.transform.size.to_tuple()
        ball.transform.center.x = vw - bw
        ball.kinematic.velocity.x = -(abs(ball.kinematic.velocity.x) or 250.0)

    def step(self, ctx: PongTickContext):
        """Apply Pong rules."""
        if ctx.world.paused:
            return

        vw, _ = ctx.world.viewport
        ball = ctx.world.ball()
        x, _ = ball.transform.center.to_tuple()
        bw, _ = ball.transform.size.to_tuple()

        if x + bw < 0:
            if ctx.world.god_mode_p1:
                self._bounce_from_left_goal(ball, ctx)
                return

            ctx.world.score.right += 1
            spawn_x, spawn_y = ctx.world.ball_spawn_position
            reset_vx, reset_vy = ctx.world.ball_reset_speed
            ball.transform.center = Vec2(spawn_x, spawn_y)
            ball.kinematic.velocity = Vec2(-abs(reset_vx), -abs(reset_vy))
            return

        if x > vw:
            if ctx.world.god_mode_p2:
                self._bounce_from_right_goal(ball, ctx)
                return

            ctx.world.score.left += 1
            spawn_x, spawn_y = ctx.world.ball_spawn_position
            reset_vx, reset_vy = ctx.world.ball_reset_speed
            ball.transform.center = Vec2(spawn_x, spawn_y)
            ball.kinematic.velocity = Vec2(abs(reset_vx), -abs(reset_vy))
