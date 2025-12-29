"""
Minimal main menu scene for Deja Bounce.
"""

from __future__ import annotations

from mini_arcade_core.scenes import register_scene
from mini_arcade_core.ui import BaseMenuScene, MenuItem, MenuStyle
from mini_arcade_core.utils import logger

from deja_bounce.constants import (
    BACKGROUND,
    BUTTON_BORDER,
    BUTTON_FILL,
    DIM,
    HIGHLIGHT,
    WHITE,
)

from .commands import CycleDifficultyCommand, QuitCommand, StartGameCommand


@register_scene("menu")
class MenuScene(BaseMenuScene):
    """
    Simple main menu scene for Deja Bounce.

    Options:
      [0] Start Game
      [1] Quit
      [2] Cycle Difficulty
    """

    @property
    def menu_title(self) -> str | None:
        return "Deja Bounce"

    def menu_style(self) -> MenuStyle:
        return MenuStyle(
            background_color=(
                (*BACKGROUND, 1.0) if len(BACKGROUND) == 3 else BACKGROUND
            ),
            button_enabled=True,
            button_fill=BUTTON_FILL,
            button_border=BUTTON_BORDER,
            button_selected_border=HIGHLIGHT,
            normal=DIM,
            selected=WHITE,
            hint="Press ENTER to start · ESC to quit",
            hint_color=(200, 200, 200),
        )

    def menu_items(self):
        logger.info("MenuScene on_enter")

        items = [
            MenuItem("START", "START", StartGameCommand()),
            MenuItem("QUIT", "QUIT", QuitCommand()),
            MenuItem(
                "DIFFICULTY",
                "DIFFICULTY",
                CycleDifficultyCommand(),
                label_fn=lambda g: f"DIFFICULTY: {g.settings.difficulty.upper()}",
            ),
        ]

        return items
