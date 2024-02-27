# Standard library imports
import os

# Third-party imports
import pygame

# Local folder imports
from color import Color as c


class Tile:
    def __init__(self, symbol: str, name: str, color: str = c.ANSI_RESET) -> None:
        self.symbol = symbol
        self.name = name
        self.legend = f"{symbol} {name.upper()}"

        self.colored_symbol = f"{color}{symbol}{c.ANSI_RESET}"
        self.colored_name = f"{color}{name.upper()}{c.ANSI_RESET}"
        self.colored_legend = f"{self.colored_symbol} {self.colored_name}"

    def load_image(self):
        self.image = pygame.image.load(os.path.join("images", f"{self.name}.png")).convert_alpha()


plains = Tile(".", "plains", c.ANSI_YELLOW)
forest = Tile("8", "forest", c.ANSI_GREEN)
pines = Tile("Y", "pines", c.ANSI_GREEN)
mountain = Tile("A", "mountain")
water = Tile("~", "water", c.ANSI_CYAN)
player_marker = Tile("X", "player", c.ANSI_RED)
empty = Tile(" ", "???")
town = Tile("M", "town", c.ANSI_MAGENTA)
