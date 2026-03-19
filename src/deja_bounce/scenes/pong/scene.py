"""
Minimal Pong-like scene using mini-arcade-core.
"""

from __future__ import annotations

from dataclasses import replace

from mini_arcade.utils.logging import logger
from mini_arcade_core.scenes.autoreg import register_scene
from mini_arcade_core.scenes.bootstrap import (
    scene_entities_config,
    scene_viewport,
)
from mini_arcade_core.scenes.game_scene import (
    GameScene,
    GameSceneSystemsConfig,
)

from deja_bounce.controllers.cpu import CpuPaddleController
from deja_bounce.difficulty import DIFFICULTY_PRESETS
from deja_bounce.scenes.commands import (
    GodModeCommand,
    PauseGameCommand,
    SlowMoCommand,
    ToggleSlowMoCommand,
    ToggleTrailCommand,
)
from deja_bounce.scenes.pong.bootstrap import build_pong_world
from deja_bounce.scenes.pong.models import (
    PongIntent,
    PongTickContext,
    PongWorld,
)
from deja_bounce.scenes.pong.pipeline import build_pong_systems
from deja_bounce.scenes.pong.systems import PongRenderSystem


def _build_pong_intent(actions, _ctx: PongTickContext):
    return PongIntent(
        move_left_paddle=actions.value("move_left_paddle"),
        move_right_paddle=actions.value("move_right_paddle"),
        pause=actions.pressed("pause"),
        toggle_slow_mo=actions.pressed("toggle_slow_mo"),
        toggle_trail=actions.pressed("toggle_trail"),
    )


@register_scene("pong")
class PongScene(GameScene[PongTickContext, PongWorld]):
    """
    Minimal scene: opens a window, clears screen, handles quit/ESC.
    """

    tick_context_type = PongTickContext
    capture_config = replace(
        GameScene.capture_config,
        replay_game_id="deja_bounce",
    )
    systems_config = GameSceneSystemsConfig(
        controls_scene_key="pong",
        intent_factory=_build_pong_intent,
        input_system_name="pong_input",
        pause_command_factory=lambda _ctx: PauseGameCommand(),
        intent_command_bindings={
            "toggle_slow_mo": lambda _ctx: ToggleSlowMoCommand(),
            "toggle_trail": lambda _ctx: ToggleTrailCommand(),
        },
        render_system_factory=lambda _runtime: PongRenderSystem(),
    )
    _cpu_controller: CpuPaddleController | None = None

    def make_world(self):
        """Log scene initialization before the world is constructed."""

        logger.info("Initializing Pong world")

    def debug_overlay_lines(self) -> list[str]:
        ball = self.world.ball()
        lines = [
            f"difficulty: {self.context.settings.difficulty.level}",
            f"score: {self.world.score.left} - {self.world.score.right}",
            f"slow_mo: {self.world.slow_mo} scale={self.world.slow_mo_scale:.2f}",
            f"trail: {self.world.trail_mode} samples={len(self.world.trail)}",
        ]
        if ball is not None and ball.kinematic is not None:
            lines.extend(
                [
                    "ball:",
                    (
                        "  pos="
                        f"({ball.transform.center.x:.1f},"
                        f" {ball.transform.center.y:.1f})"
                    ),
                    (
                        "  vel="
                        f"({ball.kinematic.velocity.x:.1f},"
                        f" {ball.kinematic.velocity.y:.1f})"
                    ),
                ]
            )
        return lines

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
        viewport = scene_viewport(self)
        entity_cfg = scene_entities_config(
            self,
            error_message="Missing gameplay.scenes.pong.entities config",
        )
        self.world = build_pong_world(
            viewport=viewport,
            entity_cfg=entity_cfg,
        )

        # ✅ menu sets ctx.settings.difficulty
        difficulty = self.context.settings.difficulty.level.lower()
        cpu_cfg = DIFFICULTY_PRESETS.get(
            difficulty, DIFFICULTY_PRESETS["normal"]
        )

        self._cpu_controller = CpuPaddleController(
            paddle=self.world.right_paddle(),
            ball=self.world.ball(),
            side="RIGHT",
            config=cpu_cfg,
        )

        self.systems.extend(
            build_pong_systems(
                cpu_controller=self._cpu_controller,
                services=self.context.services,
            )
        )
