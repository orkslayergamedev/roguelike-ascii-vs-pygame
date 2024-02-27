# Standard library imports
import sys

# Local folder imports
from game import AsciiMode, CombinedMode, PygameMode

if __name__ == "__main__":
    try:
        game_mode = sys.argv[1]
        game = AsciiMode() if game_mode == "ascii" else PygameMode()
    except IndexError:
        game = CombinedMode()
    game.run()
