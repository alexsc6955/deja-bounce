"""
Minimal Pong-like scene using mini-arcade-core.
"""

from __future__ import annotations

from dataclasses import dataclass

from mini_arcade_core.backend import Backend
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
from mini_arcade_core.scenes.autoreg import (  # pyright: ignore[reportMissingImports]
    register_scene,
)
from mini_arcade_core.scenes.sim_scene import (  # pyright: ignore[reportMissingImports]
    Drawable,
    DrawCall,
    SimScene,
)
from mini_arcade_core.scenes.systems.builtins import (
    BaseRenderSystem,
    InputIntentSystem,
)
from mini_arcade_core.spaces.d2.boundaries2d import VerticalBounce
from mini_arcade_core.spaces.d2.geometry2d import Bounds2D, Position2D, Size2D
from mini_arcade_core.spaces.d2.physics2d import Velocity2D

from deja_bounce.constants import PADDLE_SIZE
from deja_bounce.controllers.cpu import CpuPaddleController
from deja_bounce.difficulty import DIFFICULTY_PRESETS
from deja_bounce.entities.ball import Ball
from deja_bounce.entities.paddle import Paddle
from deja_bounce.scenes.commands import (
    GodModeCommand,
    PauseGameCommand,
    ScreenshotCommand,
    SlowMoCommand,
    ToggleTrailCommand,
)
from deja_bounce.scenes.pong.models import (
    PongIntent,
    PongTickContext,
    PongWorld,
    ScoreState,
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
            toggle_slow_mo=Key.S in ctx.input_frame.keys_pressed,
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

    def step(self, ctx: PongTickContext):  # pylint: disable=too-many-branches
        """Execute hotkey commands based on intent."""
        if ctx.intent is None:
            return

        if ctx.intent.toggle_trail:
            ctx.commands.push(ToggleTrailCommand())

        if ctx.intent.screenshot:
            ctx.commands.push(ScreenshotCommand(label="pong"))

        cap = self.services.capture

        # --- Replay record toggle (F10) ---
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

        # --- Replay play toggle (F11) ---
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

        if ctx.intent.video_recording:
            if cap.video_recording:
                ctx.commands.push(StopVideoRecordCommand())
            else:
                ctx.commands.push(StartVideoRecordCommand())


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
        ctx.world.saved_ball_vel = Velocity2D(
            ctx.world.ball.velocity.vx, ctx.world.ball.velocity.vy
        )
        ctx.world.saved_left_vel = Velocity2D(
            ctx.world.left_paddle.velocity.vx,
            ctx.world.left_paddle.velocity.vy,
        )
        ctx.world.saved_right_vel = Velocity2D(
            ctx.world.right_paddle.velocity.vx,
            ctx.world.right_paddle.velocity.vy,
        )

        # freeze everything
        ctx.world.ball.velocity.stop()
        ctx.world.left_paddle.velocity.stop()
        ctx.world.right_paddle.velocity.stop()

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

        left = ctx.world.left_paddle
        right = ctx.world.right_paddle

        # ✅ set velocity
        left.velocity.vy = ctx.intent.move_left_paddle * left.speed
        right.velocity.vy = ctx.intent.move_right_paddle * right.speed

        # ✅ move left paddle using Velocity2D.advance
        lx, ly = left.position.to_tuple()
        _, ly = left.velocity.advance(lx, ly, ctx.dt)
        ly = max(0.0, min(vh - left.size.height, ly))
        left.position = Position2D(lx, ly)

        # ✅ move right paddle using Velocity2D.advance
        rx, ry = right.position.to_tuple()
        _, ry = right.velocity.advance(rx, ry, ctx.dt)
        ry = max(0.0, min(vh - right.size.height, ry))
        right.position = Position2D(rx, ry)


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

        ball = ctx.world.ball
        x, y = ball.position.to_tuple()

        # ✅ scale the ball dt
        ball_dt = ctx.dt
        if ctx.world.slow_ball:
            ball_dt *= ctx.world.slow_mo_scale

        x, y = ball.velocity.advance(x, y, ball_dt)

        ball.position = Position2D(x, y)


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

        ball = ctx.world.ball
        ctx.world.trail.append((ball.position.x, ball.position.y))


@dataclass
class PongCollisionSystem:
    """
    Handle ball collisions with walls and paddles.
    """

    services: RuntimeServices
    name: str = "pong_collision"
    order: int = 40

    def _apply_paddle_influence(self, ctx: PongTickContext, paddle: Paddle):
        ball = ctx.world.ball

        ball_center = ball.position.y + ball.size.height / 2
        paddle_center = paddle.position.y + paddle.size.height / 2
        offset = ball_center - paddle_center

        denom = (paddle.size.height / 2) if paddle.size.height > 0 else 1.0
        norm = max(-1.0, min(1.0, offset / denom))

        base_vy = 220.0
        inertia_factor = 0.30
        max_vy = 400.0

        new_vy = norm * base_vy + paddle.velocity.vy * inertia_factor
        ball.velocity.vy = max(-max_vy, min(max_vy, new_vy))

        ball.velocity.vx *= 1.03

    def step(self, ctx: PongTickContext):
        """Handle ball collisions with walls and paddles."""
        if ctx.world.paused:
            return

        vw, vh = ctx.world.viewport

        ball = ctx.world.ball
        left = ctx.world.left_paddle
        right = ctx.world.right_paddle

        # 1) Top / bottom bounce
        bounds = Bounds2D.from_size(Size2D(int(vw), int(vh)))
        bounced = VerticalBounce(bounds).apply(ball)
        if bounced:
            self.services.audio.play("wall_hit")

        # 2) Paddle collisions (use current velocity AFTER bounce)
        vx = ball.velocity.vx

        if vx < 0:
            if ball.collider.intersects(left.collider):
                ball.position.x = left.position.x + left.size.width
                ball.velocity.vx = abs(ball.velocity.vx)
                self._apply_paddle_influence(ctx, left)
                self.services.audio.play("paddle_hit")

        elif vx > 0:
            if ball.collider.intersects(right.collider):
                ball.position.x = right.position.x - ball.size.width
                ball.velocity.vx = -abs(ball.velocity.vx)
                self._apply_paddle_influence(ctx, right)
                self.services.audio.play("paddle_hit")


@dataclass
class PongRulesSystem:
    """
    Apply Pong rules: scoring, resetting ball, etc.
    """

    name: str = "pong_rules"
    order: int = 50

    def _bounce_from_left_goal(self, ctx: PongTickContext):
        ball = ctx.world.ball

        # place ball just inside the field
        ball.position.x = 0.0

        # ensure it goes RIGHT
        ball.velocity.vx = abs(ball.velocity.vx) or 250.0

    def _bounce_from_right_goal(self, ctx: PongTickContext):
        ball = ctx.world.ball
        vw, _ = ctx.world.viewport
        bw, _ = ball.size.to_tuple()

        # place ball just inside the field
        ball.position.x = vw - bw

        # ensure it goes LEFT
        ball.velocity.vx = -(abs(ball.velocity.vx) or 250.0)

    def step(self, ctx: PongTickContext):
        """Apply Pong rules."""
        if ctx.world.paused:
            return

        vw, vh = ctx.world.viewport
        x, _ = ctx.world.ball.position.to_tuple()
        bw, bh = ctx.world.ball.size.to_tuple()

        # ball out of bounds left/right
        if x + bw < 0:
            if ctx.world.god_mode_p1:
                # player protected -> bounce back, no score for CPU
                self._bounce_from_left_goal(ctx)
                return

            ctx.world.score.right += 1
            # reset ball to center
            ctx.world.ball.position = Position2D(
                vw / 2 - bw / 2, vh / 2 - bh / 2
            )
            ctx.world.ball.velocity = Velocity2D(250.0, -200.0)
            return

        if x > vw:
            if ctx.world.god_mode_p2:
                # player protected -> bounce back, no score for CPU
                self._bounce_from_right_goal(ctx)
                return

            ctx.world.score.left += 1
            # reset ball to center
            ctx.world.ball.position = Position2D(
                vw / 2 - bw / 2, vh / 2 - bh / 2
            )
            ctx.world.ball.velocity = Velocity2D(-250.0, -200.0)


class DrawCenterLine(Drawable[PongTickContext]):
    """
    Drawable to render the center dashed line.
    """

    def draw(self, backend: Backend, ctx: PongTickContext):
        vw, vh = ctx.world.viewport

        x = int(vw / 2) - 2  # center line X (2px thickness)
        dash_w = 4
        dash_h = 16
        gap = 12

        y = 0
        while y < vh:
            backend.render.draw_rect(
                x, int(y), dash_w, dash_h, color=(200, 200, 200)
            )
            y += dash_h + gap


class DrawLeftPaddle(Drawable[PongTickContext]):
    """
    Drawable to render the left paddle.
    """

    def draw(self, backend: Backend, ctx: PongTickContext):
        lx, ly = ctx.world.left_paddle.position.to_tuple()
        lw, lh = ctx.world.left_paddle.size.to_tuple()
        backend.render.draw_rect(
            int(lx), int(ly), int(lw), int(lh), color=(255, 255, 255)
        )


class DrawRightPaddle(Drawable[PongTickContext]):
    """
    Drawable to render the right paddle.
    """

    def draw(self, backend: Backend, ctx: PongTickContext):
        rx, ry = ctx.world.right_paddle.position.to_tuple()
        rw, rh = ctx.world.right_paddle.size.to_tuple()
        backend.render.draw_rect(
            int(rx), int(ry), int(rw), int(rh), color=(255, 255, 255)
        )


class DrawBall(Drawable[PongTickContext]):
    """
    Drawable to render the ball.
    """

    def draw(self, backend: Backend, ctx: PongTickContext):
        bx, by = ctx.world.ball.position.to_tuple()
        bw, bh = ctx.world.ball.size.to_tuple()
        backend.render.draw_rect(
            int(bx), int(by), int(bw), int(bh), color=(255, 255, 255)
        )


class DrawScore(Drawable[PongTickContext]):
    """
    Drawable to render the score.
    """

    def draw(self, backend: Backend, ctx: PongTickContext):
        vw, _ = ctx.world.viewport

        left_text = str(ctx.world.score.left)
        right_text = str(ctx.world.score.right)

        # measure pixel width of each score
        left_w, _ = backend.text.measure(left_text)

        center_x = vw // 2
        gap = 40  # distance from center line to each score

        # left score: right-aligned to the left side of center
        left_x = (center_x - gap) - left_w

        # right score: left-aligned to the right side of center
        right_x = center_x + gap

        backend.text.draw(left_x, 20, left_text, color=(200, 200, 200))
        backend.text.draw(right_x, 20, right_text, color=(200, 200, 200))


class DrawTrail(Drawable[PongTickContext]):
    """
    Drawable to render the ball trail.
    """

    def draw(self, backend: Backend, ctx: PongTickContext):
        if not ctx.world.trail_mode:
            return

        count = len(ctx.world.trail)
        if count == 0:
            return

        size = 10  # match ball size
        for i, (x, y) in enumerate(ctx.world.trail):
            t = (i + 1) / count  # 0..1
            alpha = t * 0.5  # max 50%
            backend.render.draw_rect(
                int(x),
                int(y),
                size,
                size,
                color=(255, 255, 255, alpha),
            )


@dataclass
class PongRenderSystem(BaseRenderSystem):
    """
    Render the Pong world.
    """

    name: str = "pong_render"
    order: int = 100

    def step(self, ctx: PongTickContext):
        """Render the Pong world."""

        ctx.draw_ops = [
            DrawCall(drawable=DrawCenterLine(), ctx=ctx),
            DrawCall(drawable=DrawLeftPaddle(), ctx=ctx),
            DrawCall(drawable=DrawRightPaddle(), ctx=ctx),
            DrawCall(drawable=DrawTrail(), ctx=ctx),
            DrawCall(drawable=DrawBall(), ctx=ctx),
            DrawCall(drawable=DrawScore(), ctx=ctx),
        ]
        super().step(ctx)


@register_scene("pong")
class PongScene(SimScene[PongTickContext, PongWorld]):
    """
    Minimal scene: opens a window, clears screen, handles quit/ESC.
    """

    tick_context_type = PongTickContext

    def on_enter(self):
        # Add cheats
        self.context.cheats.register(
            "god_mode",
            sequence=["G", "O", "D"],
            command_factory=lambda ctx: GodModeCommand("P1"),
            clear_buffer_on_match=True,
        )
        self.context.cheats.register(
            "slow_mo",
            sequence=["S", "L", "O", "W"],
            command_factory=lambda ctx: SlowMoCommand(),
            clear_buffer_on_match=True,
        )
        # Initialize world, paddles, ball, etc.
        # Justification: window typer is protocol, mypy can't infer correctly
        # pylint: disable=assignment-from-no-return
        vw, vh = self.context.services.window.get_virtual_size()
        # pylint: enable=assignment-from-no-return
        pad_w, pad_h = PADDLE_SIZE

        self.world = PongWorld(
            viewport=(vw, vh),
            left_paddle=Paddle(
                position=Position2D(20, vh / 2 - pad_h / 2),
                size=Size2D(pad_w, pad_h),
                velocity=Velocity2D(0.0, 0.0),
            ),
            right_paddle=Paddle(
                position=Position2D(vw - 20 - pad_w, vh / 2 - pad_h / 2),
                size=Size2D(pad_w, pad_h),
                velocity=Velocity2D(0.0, 0.0),
            ),
            ball=Ball(
                position=Position2D(vw / 2 - 5, vh / 2 - 5),
                size=Size2D(10, 10),
                velocity=Velocity2D(-250.0, -200.0),
            ),
            score=ScoreState(),
        )

        # ✅ menu sets ctx.settings.difficulty
        difficulty = self.context.settings.difficulty.lower()
        cpu_cfg = DIFFICULTY_PRESETS.get(
            difficulty, DIFFICULTY_PRESETS["normal"]
        )

        cpu_controller = CpuPaddleController(
            paddle=self.world.right_paddle,
            ball=self.world.ball,
            side="RIGHT",
            config=cpu_cfg,
        )

        self.systems.extend(
            [
                PongInputSystem(),
                PongPauseSystem(),
                PongHotkeysSystem(self.context.services),
                PongTimeScaleSystem(),
                CpuIntentSystem(controller=cpu_controller),
                PaddleSystem(),
                BallMovementSystem(),
                PongTrailCaptureSystem(),
                PongCollisionSystem(self.context.services),
                PongRulesSystem(),
                PongRenderSystem(),
            ]
        )
