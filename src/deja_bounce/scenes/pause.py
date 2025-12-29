"""
Pause scene for Deja Bounce game.
Provides a menu to continue or return to the main menu.
"""

from __future__ import annotations

from mini_arcade_core import BaseCommand
from mini_arcade_core.game import Game
from mini_arcade_core.keymaps import Key
from mini_arcade_core.scenes import register_scene
from mini_arcade_core.ui import BaseMenuScene, MenuItem, MenuStyle

from .commands import QuitCommand


class ContinueCommand(BaseCommand):
    """
    Command to continue the game from pause.
    """

    def execute(self, context: Game) -> None:
        context.pop_scene()


class BackToMenuCommand(BaseCommand):
    """
    Command to return to the main menu from pause.
    """

    def execute(self, context: Game) -> None:
        context.services.scenes.change("menu")


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
            MenuItem("CONTINUE", "Continue", ContinueCommand()),
            MenuItem(
                "MAIN_MENU",
                "Main Menu",
                BackToMenuCommand(),
            ),
        ]

    def quit_command(self):
        return None

    def on_enter(self):
        self.services.input.on_quit(QuitCommand(), "quit_game")
        self.services.input.on_key_down(
            Key.ESCAPE, ContinueCommand(), "continue_game"
        )
        super().on_enter()
