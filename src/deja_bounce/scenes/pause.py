"""
Pause scene for Deja Bounce game.
Provides a menu to continue or return to the main menu.
"""

from __future__ import annotations

from mini_arcade_core.scenes.autoreg import register_scene
from mini_arcade_core.ui.menu import BaseMenuScene, MenuItem, MenuStyle

from deja_bounce.scenes.commands import BackToMenuCommand, ContinueCommand


@register_scene("pause")
class PauseScene(BaseMenuScene):
    """
    Pause scene with options to continue or return to main menu.
    """

    @property
    def menu_title(self) -> str | None:
        return "PAUSED"

    def menu_style(self) -> MenuStyle:
        return MenuStyle(
            overlay_color=(0, 0, 0, 0.5),
            panel_color=(20, 20, 20, 0.75),
        )

    def menu_items(self):
        """Initialize the pause menu."""
        return [
            MenuItem("CONTINUE", "Continue", ContinueCommand),
            MenuItem(
                "MAIN_MENU",
                "Main Menu",
                BackToMenuCommand,
            ),
        ]
