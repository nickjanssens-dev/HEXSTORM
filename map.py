import random
from settings import TILE_SIZE


def generate_map(width=20, height=20, num_rooms=8):
    # Initialize with walls
    new_map = [[1 for _ in range(width)] for _ in range(height)]

    for _ in range(num_rooms):
        room_w = random.randint(3, 6)
        room_h = random.randint(3, 6)

        x = random.randint(1, width - room_w - 1)
        y = random.randint(1, height - room_h - 1)

        # Carve out the room
        for ry in range(y, y + room_h):
            for rx in range(x, x + room_w):
                new_map[ry][rx] = 0

    # Randomly add poster walls
    for _ in range(25):
        y = random.randint(1, height - 2)
        x = random.randint(1, width - 2)
        if new_map[y][x] == 1:
            new_map[y][x] = 2

    # Randomly add HEXSTORM walls
    for _ in range(25):
        y = random.randint(1, height - 2)
        x = random.randint(1, width - 2)
        if new_map[y][x] == 1:
            new_map[y][x] = 3

    return new_map


game_map = generate_map()


def is_wall(x, y):
    map_x = int(x // TILE_SIZE)
    map_y = int(y // TILE_SIZE)

    if 0 <= map_y < len(game_map) and 0 <= map_x < len(game_map[0]):
        return game_map[map_y][map_x]
    return 1


def get_free_pos():
    while True:
        y = random.randint(1, len(game_map) - 2)
        x = random.randint(1, len(game_map[0]) - 2)
        if game_map[y][x] == 0:
            return x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2