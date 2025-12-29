"""
Minimal main application for Deja Bounce.
"""

from __future__ import annotations

from mini_arcade_core import GameConfig, SceneRegistry, WindowConfig, run_game
from mini_arcade_native_backend import NativeBackend

from deja_bounce.constants import ASSETS_ROOT, FPS, WINDOW_SIZE


def run():
    """Main entry point for DejaBounce."""
    registry = SceneRegistry(_factories={}).discover("deja_bounce.scenes")

    font_path = ASSETS_ROOT / "fonts" / "deja_vu_dive" / "Deja-vu_dive.ttf"

    backend = NativeBackend(font_path=str(font_path), font_size=24)
    width, height = WINDOW_SIZE
    window = WindowConfig(
        width=width,
        height=height,
        background_color=(30, 30, 30),
        title="Deja Bounce (Native SDL2 + mini-arcade-core)",
    )
    config = GameConfig(
        window=window,
        fps=FPS,
        backend=backend,
    )
    run_game(config=config, registry=registry, initial_scene="menu")


if __name__ == "__main__":
    run()
