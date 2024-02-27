# Standard library imports
import os
from abc import ABC, abstractmethod
from copy import deepcopy
from random import randint, choice

# Third-party imports
import pygame

# Local folder imports
from map import Map
from character import Player, Enemy, enemies

SPAWN_CHANCE = 10


# ------------ abstract class setup ------------
class Game(ABC):
    def __init__(self, map_w: int, map_h: int) -> None:
        self.map_w = map_w
        self.map_h = map_h
        self.game_map = Map(map_w, map_h)
        self.player = Player()

    def decorate(self, before=False, after=False) -> None:
        newline = "\n"
        print(f"{newline if before else ''}-{'-' * self.map_w}{newline if after else ''}")

    @abstractmethod
    def run(self) -> None:
        ...

    @staticmethod
    def clear() -> None:
        os.system("cls||clear")

    def spawn_enemy(self, pos: list[int]) -> Enemy | None:
        x, y = pos
        chance = randint(1, 100)
        tile = self.game_map.init_map_data[y][x]
        if chance < SPAWN_CHANCE and tile.name != "water":
            return deepcopy(choice(enemies))


# ------------ ascii mode setup ------------
class AsciiMode(Game):
    def __init__(self, map_w: int = 30, map_h: int = 15) -> None:
        super().__init__(map_w, map_h)

    def run(self) -> None:
        """
        Running the game in ASCII mode means 1 cycle per input.
        This way the logic is kept simple.
        """
        while True:
            # ----- clear the screen
            self.clear()

            # ----- try to spawn an enemy on the current tile, then engage in combat
            if enemy := self.spawn_enemy(self.player.pos):
                self.start_combat(enemy)

            # ----- break out of loop if the player health pool is empty
            if self.player.health <= 0:
                input("Game Over")
                break

            # ----- calculate movement possibilities
            self.player.calculate_movement_options(self.map_w, self.map_h)

            # ----- update map with player (reveal nearby tiles)
            self.game_map.update_map(self.player.pos, self.player.marker)

            # ----- display the map and show possible directions to move
            self.game_map.display_map()
            self.decorate()
            self.player.health_bar.draw()
            self.decorate(True)
            self.game_map.display_movement_options(self.player.movement_options)

            # ----- ask for player input
            self.player.get_movement_input()

    def start_combat(self, enemy) -> None:
        while True:
            # ----- display the map in combat mode too
            self.clear()
            self.game_map.display_map()
            self.decorate()

            # ----- display health bars of combatants
            self.player.health_bar.draw()
            enemy.health_bar.draw()
            self.decorate(True)
            print("[ENTER] - ATTACK")

            input()

            # ----- execute attack of combatants
            self.player.attack(enemy)
            enemy.attack(self.player)
            print("[ENTER] - CONTINUE")

            input()

            # ----- finish combat if one of the combatants die
            if self.player.health <= 0 or enemy.health <= 0:
                self.clear()
                break


# ------------ pygame mode setup ------------
class PygameMode(Game):
    def __init__(self, map_w: int = 30, map_h: int = 15) -> None:
        super().__init__(map_w, map_h)

        # ----- initialize pygame
        pygame.init()

        # set tile attributes
        self.tile_size = 16
        self.hud_height = 140
        self.screen_width = self.tile_size * map_w * 2 + self.tile_size * 2
        self.screen_height = self.tile_size * map_h * 2 + self.hud_height + self.tile_size * 2

        # setup screen
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.canvas = pygame.Surface((self.map_w * self.tile_size, self.map_h * self.tile_size)).convert()
        self.map_background = pygame.Surface((self.screen_width, self.screen_height - self.hud_height)).convert_alpha()
        self.map_background.fill("brown")
        self.map_frame = pygame.transform.scale2x(pygame.image.load("images/map_frame.png")).convert_alpha()
        self.hud_frame = pygame.transform.scale2x(pygame.image.load("images/hud_frame.png")).convert_alpha()

        # load images of tiles
        self.game_map.load_images()
        self.player.marker.load_image()

        self.enemy_in_combat = None

    def run(self) -> None:
        """
        Running the game in Pygame mode means continuous cycles.
        The logic is different and a bit more complicated.
        """
        while True:
            # ----- checking for any event like key presses
            self.check_events()

            # ----- break out of loop if the player health pool is empty
            if self.player.health <= 0:  # TODO: fix
                self.draw_text("Game Over", (self.screen_width / 2, self.screen_height - 80))
                continue

            # ----- calculate movement possibilities
            self.player.calculate_movement_options(self.map_w, self.map_h)

            # ----- update map with player (reveal nearby tiles)
            self.game_map.update_map(self.player.pos, self.player.marker)

            # ----- display the map with the tiles
            self.display()

            # ----- display combat & non-combat ui
            self.display_ui()

            # ----- update the window
            pygame.display.update()

    def check_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.KEYDOWN:
                # ----- if an enemy is present, only the enter key is allowed
                if self.enemy_in_combat:
                    if event.key == pygame.K_RETURN:
                        self.next_turn()
                # ----- if there is no enemy, the player can move the available directions
                else:
                    self.check_movement_inputs(event)

    def check_movement_inputs(self, event) -> None:
        if event.key == pygame.K_w and self.player.movement_options.get("up"):
            self.player.pos[1] -= 1
            self.enemy_in_combat = self.spawn_enemy(self.player.pos)
        elif event.key == pygame.K_s and self.player.movement_options.get("down"):
            self.player.pos[1] += 1
            self.enemy_in_combat = self.spawn_enemy(self.player.pos)
        elif event.key == pygame.K_a and self.player.movement_options.get("left"):
            self.player.pos[0] -= 1
            self.enemy_in_combat = self.spawn_enemy(self.player.pos)
        elif event.key == pygame.K_d and self.player.movement_options.get("right"):
            self.player.pos[0] += 1
            self.enemy_in_combat = self.spawn_enemy(self.player.pos)

    def display(self) -> None:
        self.screen.fill("black")
        # ----- blit each tile onto the canvas if it's explored
        for i, row in enumerate(self.game_map.map_data):
            for j, tile in enumerate(row):
                if self.game_map.exploration_process[i][j]:
                    self.canvas.blit(tile.image, (j * self.tile_size, i * self.tile_size))
        # ----- blit the canvas to the screen
        self.screen.blit(self.map_background, (0, 0))
        self.screen.blit(self.map_frame, (0, 0))
        self.screen.blit(self.hud_frame, (0, self.screen_height - 140))
        self.screen.blit(pygame.transform.scale2x(self.canvas), (self.tile_size, self.tile_size))

    def display_ui(self) -> None:
        self.draw_text(self.player.name, (self.screen_width / 2, self.screen_height - 110))
        self.draw_health_bar(self.player.health, self.player.health_max, (40, 200, 40), self.screen_height - 95)

        if self.enemy_in_combat:
            self.draw_text("[ENTER] - ATTACK", (self.screen_width - 40, self.screen_height - 105), "right")
            self.draw_text(self.enemy_in_combat.name, (self.screen_width / 2, self.screen_height - 55))
            self.draw_health_bar(self.enemy_in_combat.health, self.enemy_in_combat.health_max, (200, 40, 40), self.screen_height - 40)
        else:
            for index, (direction, value) in enumerate(self.game_map.movement_options.items()):
                if self.player.movement_options.get(direction):
                    self.draw_text(value, (40, self.screen_height - 105 + index * 22), "left")

    def next_turn(self) -> None:
        # ----- prompt a single attack
        self.player.attack(self.enemy_in_combat)
        self.enemy_in_combat.attack(self.player)

        # ----- reset the attribute if either of the combatants are dead
        if self.player.health <= 0 or self.enemy_in_combat.health <= 0:
            self.enemy_in_combat = None

    def draw_text(self, text: str, pos: list[int], alignment=None, size=30, color="white") -> None:
        # font = pygame.font.Font(None, 36)
        font = pygame.font.Font("font.ttf", size)

        text_surface = font.render(text, True, color).convert_alpha()
        text_rect = text_surface.get_rect(center=pos)
        if alignment == "left":
            text_rect.midleft = pos
        elif alignment == "right":
            text_rect.midright = pos
        elif alignment == "top":
            text_rect.midtop = pos
        self.screen.blit(text_surface, text_rect)

    def draw_health_bar(self, hp: int, max_hp: int, color: list[int], y: int) -> None:
        length = 200
        width = max(hp / max_hp * length, 1)

        bar = pygame.Surface((width, 24)).convert_alpha()
        bar.fill(color)
        bar_rect = bar.get_rect(midleft=((self.screen_width / 2 - length / 2), y + 12))

        full_bar = pygame.Surface((length, 24)).convert_alpha()
        full_bar.fill("gray")
        full_bar_rect = full_bar.get_rect(midleft=((self.screen_width / 2 - length / 2), y + 12))

        outline = pygame.Surface((length, 24)).convert_alpha()
        outline.fill("black")
        outline_rect = full_bar.get_rect(center=((self.screen_width / 2), y + 12))

        self.screen.blit(full_bar, full_bar_rect)
        self.screen.blit(bar, bar_rect)
        pygame.draw.rect(self.screen, "black", outline_rect, width=3)
        self.draw_text(f"{hp}/{max_hp}", (self.screen_width / 2, y), "top", 24, "black")


# ------------ combined mode setup ------------
class CombinedMode(PygameMode):
    def __init__(self, map_w: int = 30, map_h: int = 15) -> None:
        super().__init__(map_w, map_h)

    def run(self) -> None:
        """
        Running the game in Combined mode means continuous cycles while displaying ASCII too.
        The logic is the most complicated, as it's the combination of the two above.
        We should only update the ASCII display whenever we give an input,
        as continuous console updating is unreadable.
        """
        # ----- necessary initial calculations and displaying
        self.player.calculate_movement_options(self.map_w, self.map_h)
        self.clear()
        self.game_map.display_map()
        self.decorate()
        self.player.health_bar.draw()
        self.decorate(True)
        self.game_map.display_movement_options(self.player.movement_options)

        while True:
            # ----- break out of loop if the player health pool is empty
            if self.player.health <= 0:
                self.draw_text("Game Over", (self.screen_width / 2, self.screen_height - 80))
                continue

            # ----- update map with player (reveal nearby tiles)
            self.game_map.update_map(self.player.pos, self.player.marker)

            # ----- checking for any event like key presses
            self.check_events()

            # ----- calculate movement possibilities
            self.player.calculate_movement_options(self.map_w, self.map_h)

            # ----- display the map with the tiles
            self.display()

            # ----- display combat & non-combat ui
            self.display_ui()

            # ----- update the window
            pygame.display.update()

    def check_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.KEYDOWN:
                # ----- if an enemy is present, only the enter key is allowed and the health bars are displayed
                if self.enemy_in_combat:
                    if event.key == pygame.K_RETURN:
                        self.clear()  # ASCII
                        self.game_map.display_map()  # ASCII
                        self.next_turn()
                        self.display_health_bars_or_movement_options()
                # ----- if there is no enemy, the player can move the available directions
                else:
                    self.check_movement_inputs(event)
                    self.clear()  # ASCII
                    self.game_map.display_map()  # ASCII
                    self.decorate()
                    self.display_health_bars_or_movement_options()

    def display_health_bars_or_movement_options(self) -> None:
        self.player.health_bar.draw()  # ASCII
        if self.enemy_in_combat:
            self.enemy_in_combat.health_bar.draw()  # ASCII
            self.decorate(True)
            print("[ENTER] - ATTACK")
        else:
            self.decorate(True)
            self.game_map.display_movement_options(self.player.movement_options)  # ASCII
