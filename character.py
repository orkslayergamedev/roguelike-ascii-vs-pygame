# Standard library imports
import msvcrt

# Local folder imports
from health_bar import HealthBar
from tile import player_marker
from weapon import fists, claws, jaws, short_bow


INSTANT_INPUT = False


# ------------ parent class setup ------------
class Character:
    def __init__(self,
                 name: str,
                 health: int,
                 ) -> None:
        self.name = name
        self.health = health
        self.health_max = health

        self.weapon = fists

    def attack(self, target) -> None:
        if self.health <= 0:
            return
        target.health -= self.weapon.damage
        target.health = max(target.health, 0)
        target.health_bar.update()
        print(f"{self.name} dealt {self.weapon.damage} damage to "
              f"{target.name} with {self.weapon.name}")

    def __copy__(self):
        new_instance = self.__class__.__new__(self.__class__)
        new_instance.__dict__.update(self.__dict__)
        # Add any additional attributes that need to be copied
        return new_instance


# ------------ subclass setup ------------
class Player(Character):
    def __init__(self, name: str = "Player", health: int = 100) -> None:
        super().__init__(name=name, health=health)

        self.default_weapon = self.weapon
        self.health_bar = HealthBar(self, color="green")
        self.pos = [0, 0]
        self.marker = player_marker

        self.movement_options: dict[str, bool]

    def equip(self, weapon) -> None:
        self.weapon = weapon
        print(f"{self.name} equipped a(n) {self.weapon.name}!")

    def drop(self) -> None:
        print(f"{self.name} dropped the {self.weapon.name}!")
        self.weapon = self.default_weapon

    def move(self, x: int, y: int) -> None:
        self.pos[0] += x
        self.pos[1] += y

    def calculate_movement_options(self, width, height) -> None:
        self.movement_options = {
            "up": self.pos[1] > 0,  # can go up
            "down": self.pos[1] < height - 1,  # can go down
            "left": self.pos[0] > 0,  # can go left
            "right": self.pos[0] < width - 1  # can go right
        }

    def get_movement_input(self) -> None:
        choice = msvcrt.getch().decode('utf-8') if INSTANT_INPUT else input()

        if self.movement_options["up"] and choice in ("w", "W"):
            self.pos[1] -= 1
        elif self.movement_options["down"] and choice in ("s", "S"):
            self.pos[1] += 1
        elif self.movement_options["left"] and choice in ("a", "A"):
            self.pos[0] -= 1
        elif self.movement_options["right"] and choice in ("d", "D"):
            self.pos[0] += 1


# ------------ subclass setup ------------
class Enemy(Character):
    def __init__(self,
                 name: str,
                 health: int,
                 weapon=None,
                 ) -> None:
        super().__init__(name=name, health=health)
        self.weapon = weapon

        self.health_bar = HealthBar(self, color="red")

        enemies.append(self)


enemies = []
slime = Enemy("Slime", 10, jaws)
goblin = Enemy("Goblin", 20, short_bow)
spider = Enemy("Spider", 15, jaws)
rat = Enemy("Rat", 6, claws)
