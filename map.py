# Standard library imports
from random import randint

# Local folder imports
from tile import (
    forest,
    mountain,
    pines,
    plains,
    player_marker,
    town,
    water,
    Tile
)


class Map:
    def __init__(self, width, height) -> None:
        self.width = width
        self.height = height

        self.init_map_data: list[list[str]]
        self.full_map_data: list[[str]]
        self.map_data: list[[str]]
        self.exploration_process: list[list[int]]

        self.generate_map()
        self.generate_patch(forest, 3, 3, 7)
        self.generate_patch(pines, 3, 3, 7)
        self.generate_patch(mountain, 3, 3, 7)
        self.generate_patch(water, 2, 3, 10)
        self.generate_patch(town, 1, 3, 3)

        self.movement_options = {
            "up": "[W] - UP",
            "down": "[S] - DOWN",
            "left": "[A] - LEFT",
            "right": "[D] - RIGHT"
        }

        self.explored_tiles = [player_marker]

    def load_images(self) -> None:
        for row in self.init_map_data:
            for tile in row:
                tile.load_image()

        self.copy_map()

    def generate_map(self) -> None:
        self.init_map_data = [[plains for _ in range(self.width)] for _ in range(self.height)]
        self.copy_map()

        self.exploration_process = [[0 for _ in range(self.width)] for _ in range(self.height)]

    def generate_patch(
            self,
            tile: Tile,
            num_patches: int,
            min_size: int,
            max_size: int,
            irregular: int = True
    ) -> None:
        for _ in range(num_patches):
            size_y = randint(min_size, max_size)  # height of patch
            size_x = randint(min_size, max_size)  # width of patch
            start_y = randint(1, self.height - size_y - 1)  # top row
            start_x = randint(1, self.width - size_x - 1)  # start of row

            if irregular:
                raw_start_x = randint(3, self.width - max_size)  # start of row

            for i in range(size_y):
                if irregular:
                    size_x = randint(int(0.7 * max_size), max_size)  # randomized width of row
                    start_x = raw_start_x - randint(1, 2)  # randomized start of row
                for j in range(size_x):
                    self.init_map_data[start_y + i][start_x + j] = tile
        self.copy_map()

    def display_movement_options(self, options: dict[str, bool]) -> None:
        for direction, value in self.movement_options.items():
            if options.get(direction):
                print(value)

    def reveal_map(self, pos: list[int]) -> None:
        x, y = pos
        sight_range = range(-2, 3)
        fov = [
            [0, 1, 1, 1, 0],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [0, 1, 1, 1, 0],

        ]
        for y_index in sight_range:
            tile_y = y + y_index
            if 0 <= tile_y < self.height:
                for x_index in sight_range:
                    tile_x = x + x_index
                    if 0 <= tile_x < self.width and fov[y_index + 2][x_index + 2]:
                        self.exploration_process[tile_y][tile_x] = 1
                        revealed_tile = self.init_map_data[tile_y][tile_x]
                        if revealed_tile not in self.explored_tiles:
                            self.explored_tiles.append(revealed_tile)

    def update_map(self, pos: list[int], marker: Tile) -> None:
        x, y = pos
        self.copy_map()
        self.reveal_map(pos)
        self.map_data[y][x] = marker

    def display_map(self) -> None:
        frame = "x" + self.width * "=" + "x"
        print(frame)
        for y_index, (row, explored_row) in enumerate(zip(self.map_data, self.exploration_process)):
            if y_index in range(len(self.explored_tiles)):
                legend = self.explored_tiles[y_index].colored_legend
            else:
                legend = ""

            print(
                "|" + "".join(
                    [
                        tile.colored_symbol if is_explored else " " for tile, is_explored in zip(row, explored_row)
                    ]
                ) + "| " + legend
            )
        print(frame)

    def copy_map(self) -> None:
        self.map_data = [list(row) for row in self.init_map_data]
