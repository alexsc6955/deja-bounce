"""
Minimal Pong-like scene using mini-arcade-core.
"""

from __future__ import annotations

from mini_arcade_core.scenes.autoreg import (
    register_scene,
)
from mini_arcade_core.scenes.sim_scene import (
    SimScene,
)

from deja_bounce.controllers.cpu import CpuPaddleController
from deja_bounce.difficulty import DIFFICULTY_PRESETS
from deja_bounce.entities import Ball, DottedLine, EntityId, Paddle
from deja_bounce.scenes.commands import (
    GodModeCommand,
    SlowMoCommand,
)
from deja_bounce.scenes.pong.models import (
    PongTickContext,
    PongWorld,
)
from deja_bounce.scenes.pong.systems import (
    BallMovementSystem,
    CpuIntentSystem,
    PaddleSystem,
    PongCollisionSystem,
    build_pong_capture_hotkeys_system,
    PongHotkeysSystem,
    PongInputSystem,
    PongPauseSystem,
    PongRenderSystem,
    PongRulesSystem,
    PongTimeScaleSystem,
    PongTrailCaptureSystem,
)


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

        dotted_center_line = DottedLine.build(
            EntityId.CENTER_LINE, "Dotted Center Line", vw, vh
        )
        left_paddle = Paddle.build(
            EntityId.LEFT_PADDLE, "Left Paddle", x=20.0, vh=vh
        )
        right_paddle = Paddle.build(
            EntityId.RIGHT_PADDLE,
            "Right Paddle",
            x=vw - Paddle.paddle_size[0] - 20.0,
            vh=vh,
        )
        ball = Ball.build(EntityId.BALL, "Ball", vw, vh)

        self.world = PongWorld(
            entities=[
                left_paddle,
                right_paddle,
                ball,
                dotted_center_line,
            ],
            viewport=(vw, vh),
        )

        # ✅ menu sets ctx.settings.difficulty
        difficulty = self.context.settings.difficulty.lower()
        cpu_cfg = DIFFICULTY_PRESETS.get(
            difficulty, DIFFICULTY_PRESETS["normal"]
        )

        cpu_controller = CpuPaddleController(
            paddle=self.world.get_entity_by_id(EntityId.RIGHT_PADDLE),
            ball=self.world.get_entity_by_id(EntityId.BALL),
            side="RIGHT",
            config=cpu_cfg,
        )

        self.systems.extend(
            [
                PongInputSystem(),
                PongPauseSystem(),
                PongHotkeysSystem(),
                build_pong_capture_hotkeys_system(self.context.services),
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
