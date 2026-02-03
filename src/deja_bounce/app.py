"""
Minimal main application for Deja Bounce.
"""

from __future__ import annotations

from mini_arcade_core import (  # pyright: ignore[reportMissingImports]
    GameConfig,
    SceneRegistry,
    run_game,
)
from mini_arcade_core.utils import logger

# Justification: in editable installs, this module is provided by the package.
# pylint: disable=no-name-in-module
from mini_arcade_native_backend import (  # pyright: ignore[reportMissingImports]
    AudioSettings,
    BackendSettings,
    FontSettings,
    NativeBackend,
    RendererSettings,
    WindowSettings,
)

from deja_bounce.constants import ASSETS_ROOT, FPS, WINDOW_SIZE

# pylint: enable=no-name-in-module


def run():
    """
    Main entry point for DejaBounce.

    - Auto-discovers scenes from the `deja_bounce.scenes` package.
    - Configures the native backend with the Deja Vu Dive font.
    - Sets up the game window with specified dimensions and background color.
    - Runs the game with the initial scene set to "menu".
    """
    scene_registry = SceneRegistry(_factories={}).discover(
        "deja_bounce.scenes", "mini_arcade_core.scenes"
    )

    font_path = ASSETS_ROOT / "fonts" / "deja_vu_dive" / "Deja-vu_dive.ttf"
    sounds = {
        "paddle_hit": str(ASSETS_ROOT / "sfx" / "paddle_hit.wav"),
        "wall_hit": str(ASSETS_ROOT / "sfx" / "wall_hit.wav"),
    }

    w_width, w_height = WINDOW_SIZE
    backend_settings = BackendSettings(
        window=WindowSettings(
            width=w_width,
            height=w_height,
            title="Deja Bounce (Native SDL2 + mini-arcade-core)",
            high_dpi=False,
        ),
        renderer=RendererSettings(background_color=(30, 30, 30)),
        fonts=[FontSettings(name="default", path=str(font_path), size=24)],
        audio=AudioSettings(
            enable=True,
            sounds=sounds,
        ),
    )
    backend = NativeBackend(settings=backend_settings)

    game_config = GameConfig(
        initial_scene="menu",
        fps=FPS,
        backend=backend,
    )
    logger.info("Starting Deja Bounce...")
    run_game(game_config=game_config, scene_registry=scene_registry)


if __name__ == "__main__":
    run()
