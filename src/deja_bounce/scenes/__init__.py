"""
Scene modules for Deja Bounce.
Importing this module will make all scenes available.
"""

# TODO: Refactor cyclic imports later. (MenuScene <-> PongScene)
# Justification: These imports are necessary for scene management
# and may cause cyclic imports. They will be refactored later.
# pylint: disable=cyclic-import
from __future__ import annotations

from .menu import MenuScene
from .pause import PauseScene
from .pong import PongScene

__all__ = [
    "PongScene",
    "MenuScene",
    "PauseScene",
]

# pylint: enable=cyclic-import
