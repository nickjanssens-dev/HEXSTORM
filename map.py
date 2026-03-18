import random
from settings import TILE_SIZE

def generate_map(width=26, height=26, num_rooms=10):
    # Fill map with default wall type 1
    new_map = [[1 for _ in range(width)] for _ in range(height)]
    rooms = []

    for _ in range(num_rooms):
        room_w = random.randint(4, 7)
        room_h = random.randint(4, 7)

        x = random.randint(1, width - room_w - 2)
        y = random.randint(1, height - room_h - 2)

        # Carve room
        for ry in range(y, y + room_h):
            for rx in range(x, x + room_w):
                new_map[ry][rx] = 0

        center_x = x + room_w // 2
        center_y = y + room_h // 2
        rooms.append((center_x, center_y))

    # Connect rooms with corridors
    for i in range(1, len(rooms)):
        x1, y1 = rooms[i - 1]
        x2, y2 = rooms[i]

        # Horizontal corridor
        for x in range(min(x1, x2), max(x1, x2) + 1):
            new_map[y1][x] = 0

        # Vertical corridor
        for y in range(min(y1, y2), max(y1, y2) + 1):
            new_map[y][x2] = 0

    # Randomly place poster walls
    for _ in range(35):
        y = random.randint(1, height - 2)
        x = random.randint(1, width - 2)
        if new_map[y][x] == 1:
            new_map[y][x] = 2

    # Randomly place HEXSTORM walls
    for _ in range(35):
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