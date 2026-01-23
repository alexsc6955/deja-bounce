"""
Constants for the game.
"""

from __future__ import annotations

from deja_bounce.utils import find_assets_root

ASSETS_ROOT = find_assets_root()
ROOT = ASSETS_ROOT.parent

FPS = 60
WINDOW_SIZE = (800, 600)  # (360, 640)
PADDLE_SIZE = (10, 100)

# Colors
BACKGROUND = (5, 5, 15)
WHITE = (240, 240, 240)
DIM = (120, 120, 140)

# Button colors
BUTTON_FILL = (20, 20, 40)
BUTTON_BORDER = (70, 70, 120)
HIGHLIGHT = (140, 200, 255)
