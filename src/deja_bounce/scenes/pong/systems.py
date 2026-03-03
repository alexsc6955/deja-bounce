"""
Pong scene systems.
"""

from __future__ import annotations

from dataclasses import dataclass

from mini_arcade_core.backend.keys import Key
from mini_arcade_core.engine.commands import (
    StartReplayPlayCommand,
    StartReplayRecordCommand,
    StartVideoRecordCommand,
    StopReplayPlayCommand,
    StopReplayRecordCommand,
    StopVideoRecordCommand,
)
from mini_arcade_core.runtime.services import RuntimeServices
from mini_arcade_core.scenes.sim_scene import (
    DrawCall,
)
from mini_arcade_core.scenes.systems.builtins import (
    BaseQueuedRenderSystem,
    InputIntentSystem,
)
from mini_arcade_core.spaces.collision.intersections import intersects_entities
from mini_arcade_core.spaces.d2.boundaries2d import VerticalBounce
from mini_arcade_core.spaces.geometry.bounds import Bounds2D
from mini_arcade_core.spaces.geometry.size import Size2D
from mini_arcade_core.spaces.math.vec2 import Vec2

from deja_bounce.controllers.cpu import CpuPaddleController
from deja_bounce.entities import Ball, EntityId, Paddle
from deja_bounce.scenes.commands import (
    PauseGameCommand,
    ScreenshotCommand,
    ToggleSlowMoCommand,
    ToggleTrailCommand,
)
from deja_bounce.scenes.pong.draw_ops import DrawScore, DrawTrail
from deja_bounce.scenes.pong.models import (
    PongIntent,
    PongTickContext,
)


@dataclass
class PongInputSystem(InputIntentSystem):
    """
    Process input and update intent.
    """

    name: str = "pong_input"

    def build_intent(self, ctx: PongTickContext):
        """Process input and update intent."""
        down = ctx.input_frame.keys_down

        # left paddle: W/S
        left = (1.0 if Key.S in down else 0.0) - (
            1.0 if Key.W in down else 0.0
        )
        # right paddle: UP/DOWN
        right = (1.0 if Key.DOWN in down else 0.0) - (
            1.0 if Key.UP in down else 0.0
        )

        return PongIntent(
            move_left_paddle=left,
            move_right_paddle=right,
            pause=Key.ESCAPE in ctx.input_frame.keys_pressed,
            # use a non-movement key for slow-mo toggle
            toggle_slow_mo=Key.F8 in ctx.input_frame.keys_pressed,
            toggle_trail=Key.T in ctx.input_frame.keys_pressed,
            screenshot=Key.F9 in ctx.input_frame.keys_pressed,
            replay_recording=Key.F10 in ctx.input_frame.keys_pressed,
            play_replay=Key.F11 in ctx.input_frame.keys_pressed,
            video_recording=Key.F12 in ctx.input_frame.keys_pressed,
        )


@dataclass
class PongHotkeysSystem:
    """Handles one-shot hotkeys (trail toggle, screenshot, etc.)."""

    services: RuntimeServices
    name: str = "pong_hotkeys"
    order: int = 13  # after pause (12) or right after input (10/11)

    def _toggle_trail(self, ctx: PongTickContext):
        if ctx.intent.toggle_trail:
            ctx.commands.push(ToggleTrailCommand())

    def _toggle_slow_mo(self, ctx: PongTickContext):
        if ctx.intent.toggle_slow_mo:
            ctx.commands.push(ToggleSlowMoCommand())

    def _take_screenshot(self, ctx: PongTickContext):
        if ctx.intent.screenshot:
            ctx.commands.push(ScreenshotCommand(label="pong"))

    def _handle_replay_recording(self, ctx: PongTickContext):
        cap = self.services.capture
        if ctx.intent.replay_recording:
            if cap.replay_recording:
                ctx.commands.push(StopReplayRecordCommand())
            else:
                # optionally: if playing, stop play first
                if cap.replay_playing:
                    ctx.commands.push(StopReplayPlayCommand())

                ctx.commands.push(
                    StartReplayRecordCommand(
                        "pong_replay.marc",
                        game_id="deja_bounce",
                        initial_scene="pong",
                    )
                )

    def _handle_replay_play(self, ctx: PongTickContext):
        cap = self.services.capture
        if ctx.intent.play_replay:
            if cap.replay_playing:
                ctx.commands.push(StopReplayPlayCommand())
            else:
                # optionally: if recording, stop record first
                if cap.replay_recording:
                    ctx.commands.push(StopReplayRecordCommand())

                ctx.commands.push(
                    StartReplayPlayCommand(path="pong_replay.marc")
                )

    def _handle_video_recording(self, ctx: PongTickContext):
        cap = self.services.capture
        if ctx.intent.video_recording:
            if cap.video_recording:
                ctx.commands.push(StopVideoRecordCommand())
            else:
                ctx.commands.push(StartVideoRecordCommand())

    def step(self, ctx: PongTickContext):  # pylint: disable=too-many-branches
        """Execute hotkey commands based on intent."""
        if ctx.intent is None:
            return

        self._toggle_trail(ctx)
        self._toggle_slow_mo(ctx)
        self._take_screenshot(ctx)
        self._handle_replay_recording(ctx)
        self._handle_replay_play(ctx)
        self._handle_video_recording(ctx)


# TODO: This is not implemented in the scene yet
@dataclass
class PongTimeScaleSystem:
    """Applies time scaling (slow motion) to the simulation dt."""

    name: str = "pong_time_scale"
    order: int = 11  # after input (10), before pause (12) & movement

    def step(self, ctx: PongTickContext):
        """Apply time scaling to the simulation dt."""
        if ctx.world.paused:
            return

        if ctx.world.slow_mo:
            ctx.dt *= ctx.world.slow_mo_scale


@dataclass
class PongPauseSystem:
    """System to handle pausing the Pong game."""

    name: str = "pong_pause"
    order: int = 12  # right after input

    def step(self, ctx: PongTickContext):
        """Pause the game if pause intent is triggered."""
        if not ctx.intent or not ctx.intent.pause:
            return

        # avoid re-triggering every frame
        if ctx.world.paused:
            return

        ctx.world.paused = True

        # save velocities ONCE
        ball = ctx.world.get_entity_by_id(EntityId.BALL)
        ctx.world.saved_ball_vel = Vec2(
            ball.kinematic.velocity.x, ball.kinematic.velocity.y
        )
        left_paddle = ctx.world.get_entity_by_id(EntityId.LEFT_PADDLE)
        ctx.world.saved_left_vel = Vec2(
            left_paddle.kinematic.velocity.x,
            left_paddle.kinematic.velocity.y,
        )
        right_paddle = ctx.world.get_entity_by_id(EntityId.RIGHT_PADDLE)
        ctx.world.saved_right_vel = Vec2(
            right_paddle.kinematic.velocity.x,
            right_paddle.kinematic.velocity.y,
        )

        # freeze everything
        ball.kinematic.stop()
        left_paddle.kinematic.stop()
        right_paddle.kinematic.stop()

        ctx.commands.push(PauseGameCommand())


@dataclass
class CpuIntentSystem:
    """
    Simple CPU intent system for right paddle.
    """

    name: str = "pong_cpu_intent"
    order: int = 15  # after input, before paddles

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

        # override only CPU side
        ctx.intent = PongIntent(
            move_left_paddle=ctx.intent.move_left_paddle,
            move_right_paddle=move,
            pause=ctx.intent.pause,
        )


@dataclass
class PaddleSystem:
    """
    Move paddles based on intent.
    """

    name: str = "pong_paddles"
    order: int = 20

    def step(self, ctx: PongTickContext):
        """Move paddles based on intent."""
        if ctx.world.paused:
            return

        if ctx.intent is None:
            return

        _, vh = ctx.world.viewport

        left = ctx.world.get_entity_by_id(EntityId.LEFT_PADDLE)
        right = ctx.world.get_entity_by_id(EntityId.RIGHT_PADDLE)

        # ✅ set velocity
        left.kinematic.velocity.y = (
            ctx.intent.move_left_paddle * left.kinematic.max_speed
        )
        right.kinematic.velocity.y = (
            ctx.intent.move_right_paddle * right.kinematic.max_speed
        )

        # ✅ move left paddle using Velocity2D.advance
        lx = left.transform.center.x
        ly = left.transform.center.y + (
            ctx.intent.move_left_paddle * left.kinematic.max_speed * ctx.dt
        )
        ly = max(0.0, min(vh - left.transform.size.height, ly))
        left.transform.center = Vec2(lx, ly)

        # ✅ move right paddle using Velocity2D.advance
        rx = right.transform.center.x
        ry = right.transform.center.y + (
            ctx.intent.move_right_paddle * right.kinematic.max_speed * ctx.dt
        )
        ry = max(0.0, min(vh - right.transform.size.height, ry))
        right.transform.center = Vec2(rx, ry)


@dataclass
class BallMovementSystem:
    """
    Move the ball based on its velocity.
    """

    name: str = "pong_ball_move"
    order: int = 30

    def step(self, ctx: PongTickContext):
        """Move the ball based on its velocity."""
        if ctx.world.paused:
            return

        ball = ctx.world.get_entity_by_id(EntityId.BALL)
        if ball is None or ball.kinematic is None:
            return

        # ✅ scale the ball dt
        ball_dt = ctx.dt
        if ctx.world.slow_ball:
            ball_dt *= ctx.world.slow_mo_scale

        ball.kinematic.step(ball.transform, ball_dt)


@dataclass
class PongTrailCaptureSystem:
    """Stores a ball trail when trail_mode is enabled."""

    name: str = "pong_trail_capture"
    order: int = 35  # after ball movement (30), before collision/rules/render

    def step(self, ctx: PongTickContext):
        """Capture ball trail positions."""
        if ctx.world.paused:
            return

        if not ctx.world.trail_mode:
            return

        ball = ctx.world.get_entity_by_id(EntityId.BALL)
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

        ball = ctx.world.get_entity_by_id(EntityId.BALL)
        left = ctx.world.get_entity_by_id(EntityId.LEFT_PADDLE)
        right = ctx.world.get_entity_by_id(EntityId.RIGHT_PADDLE)
        if (
            ball is None
            or left is None
            or right is None
            or ball.kinematic is None
        ):
            return

        # 1) Top / bottom bounce
        bounds = Bounds2D.from_size(Size2D(int(vw), int(vh)))
        bounced = VerticalBounce(bounds).apply(ball)
        if bounced:
            self.services.audio.play("wall_hit")

        # 2) Paddle collisions (use current velocity AFTER bounce)
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
    order: int = 50

    def _bounce_from_left_goal(self, ball: Ball, _: PongTickContext):
        # place ball just inside the field
        ball.transform.center.x = 0.0

        # ensure it goes RIGHT
        ball.kinematic.velocity.x = abs(ball.kinematic.velocity.x) or 250.0

    def _bounce_from_right_goal(self, ball: Ball, ctx: PongTickContext):
        vw, _ = ctx.world.viewport
        bw, _ = ball.transform.size.to_tuple()

        # place ball just inside the field
        ball.transform.center.x = vw - bw

        # ensure it goes LEFT
        ball.kinematic.velocity.x = -(abs(ball.kinematic.velocity.x) or 250.0)

    def step(self, ctx: PongTickContext):
        """Apply Pong rules."""
        if ctx.world.paused:
            return

        vw, vh = ctx.world.viewport
        ball = ctx.world.get_entity_by_id(EntityId.BALL)
        x, _ = ball.transform.center.to_tuple()
        bw, bh = ball.transform.size.to_tuple()

        # ball out of bounds left/right
        if x + bw < 0:
            if ctx.world.god_mode_p1:
                # player protected -> bounce back, no score for CPU
                self._bounce_from_left_goal(ball, ctx)
                return

            ctx.world.score.right += 1
            # reset ball to center
            ball.transform.center = Vec2(vw / 2 - bw / 2, vh / 2 - bh / 2)
            ball.kinematic.velocity = Vec2(-250.0, -200.0)
            return

        if x > vw:
            if ctx.world.god_mode_p2:
                # player protected -> bounce back, no score for CPU
                self._bounce_from_right_goal(ball, ctx)
                return

            ctx.world.score.left += 1
            # reset ball to center
            ball.transform.center = Vec2(vw / 2 - bw / 2, vh / 2 - bh / 2)
            ball.kinematic.velocity = Vec2(250.0, -200.0)


@dataclass
class PongRenderSystem(BaseQueuedRenderSystem[PongTickContext]):
    """Build draw_ops overlays and emit world entities via base renderer."""

    name: str = "min_render"
    order: int = 100

    def emit(self, ctx: PongTickContext, rq):
        # Add drawable-class overlays through ctx.draw_ops.
        ctx.draw_ops = [
            DrawCall(drawable=DrawTrail(), ctx=ctx),
            DrawCall(drawable=DrawScore(), ctx=ctx),
        ]
        super().emit(ctx, rq)
