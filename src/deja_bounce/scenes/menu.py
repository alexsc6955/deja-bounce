"""
Minimal main menu scene for Deja Bounce.
"""

from __future__ import annotations

from mini_arcade_core.engine.commands import QuitCommand
from mini_arcade_core.runtime.context import RuntimeContext
from mini_arcade_core.scenes.autoreg import register_scene
from mini_arcade_core.ui.menu import BaseMenuScene, MenuItem, MenuStyle

from deja_bounce.constants import (
    BACKGROUND,
    BUTTON_BORDER,
    BUTTON_FILL,
    DIM,
    HIGHLIGHT,
    WHITE,
)
from deja_bounce.scenes.commands import (
    CycleDifficultyCommand,
    StartGameCommand,
)


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

    @staticmethod
    def get_difficulty_label(ctx: RuntimeContext) -> str:
        """
        Get the label for the difficulty menu item.

        :param ctx: RuntimeContext for the scene.
        :type ctx: RuntimeContext

        :return: Label string showing the current difficulty.
        :rtype: str
        """
        difficulty = ctx.settings.difficulty.upper()
        return f"DIFFICULTY: {difficulty}"

    def menu_items(self):
        items = [
            MenuItem("start", "START", StartGameCommand),
            MenuItem("quit", "QUIT", QuitCommand),
            MenuItem(
                "difficulty",
                "DIFFICULTY",
                CycleDifficultyCommand,
                label_fn=self.get_difficulty_label,
            ),
        ]

        return items
