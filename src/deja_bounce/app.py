"""
Minimal main application for Deja Bounce.
"""

from __future__ import annotations

import json

from mini_arcade.modules.backend_loader import BackendLoader
from mini_arcade.modules.settings import Settings
from mini_arcade_core import run_game  # pyright: ignore[reportMissingImports]
from mini_arcade_core.utils import logger


def run():
    """
    Main entry point for DejaBounce.

    - Auto-discovers scenes from the `deja_bounce.scenes` package.
    - Configures the backend fonts so the title keeps the Deja Vu Dive face.
    - Sets up the game window with specified dimensions and background color.
    - Runs the game with the initial scene set to "menu".
    """
    settings = Settings.for_game("deja-bounce", required=True)
    backend_cfg = settings.backend_defaults(
        resolve_paths=True
    )  # resolved absolute paths
    backend = BackendLoader.load_backend(backend_cfg)

    logger.info(f"Loaded backend: {backend.__class__.__name__}")

    engine_cfg = settings.engine_config_defaults()
    scene_cfg = settings.scene_defaults()
    gameplay_cfg = settings.gameplay_defaults()

    logger.debug(
        json.dumps(
            {
                "engine_config": engine_cfg,
                "scene_config": scene_cfg,
                "gameplay_config": gameplay_cfg,
                "backend_config": backend_cfg,
            },
            indent=4,
        )
    )
    logger.info("Starting Deja Bounce...")
    run_game(
        engine_config=engine_cfg,
        scene_config=scene_cfg,
        backend=backend,
        gameplay_config=gameplay_cfg,
    )


if __name__ == "__main__":
    run()
