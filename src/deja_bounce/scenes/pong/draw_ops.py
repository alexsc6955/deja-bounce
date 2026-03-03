"""
DrawOps are simple Drawables that render specific aspects of the game,
like the score or the ball trail.
They are used by the PongRenderSystem to build the draw calls for each frame.
"""

from __future__ import annotations

from mini_arcade_core.backend import Backend
from mini_arcade_core.scenes.sim_scene import (
    Drawable,
)

from deja_bounce.scenes.pong.models import (
    PongTickContext,
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
            alpha = int(40 + (120 * t))
            backend.render.draw_rect(
                int(x),
                int(y),
                size,
                size,
                color=(255, 255, 255, alpha),
            )
