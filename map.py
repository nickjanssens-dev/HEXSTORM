import random
from settings import TILE_SIZE


def generate_map(width=40, height=40, num_rooms=18):
    # Start with all walls
    new_map = [[1 for _ in range(width)] for _ in range(height)]

    rooms = []

    for _ in range(num_rooms):
        room_w = random.randint(4, 8)
        room_h = random.randint(4, 8)

        x = random.randint(1, width - room_w - 2)
        y = random.randint(1, height - room_h - 2)

        new_room = (x, y, room_w, room_h)

        # Optional overlap check so rooms don't stack too much
        overlaps = False
        for other in rooms:
            ox, oy, ow, oh = other
            if (
                x < ox + ow + 1
                and x + room_w + 1 > ox
                and y < oy + oh + 1
                and y + room_h + 1 > oy
            ):
                overlaps = True
                break

        if overlaps:
            continue

        # Carve room
        for ry in range(y, y + room_h):
            for rx in range(x, x + room_w):
                new_map[ry][rx] = 0

        rooms.append(new_room)

    # Connect rooms with corridors
    for i in range(1, len(rooms)):
        prev_x, prev_y, prev_w, prev_h = rooms[i - 1]
        curr_x, curr_y, curr_w, curr_h = rooms[i]

        prev_center_x = prev_x + prev_w // 2
        prev_center_y = prev_y + prev_h // 2
        curr_center_x = curr_x + curr_w // 2
        curr_center_y = curr_y + curr_h // 2

        # Randomly choose corridor direction order for more variety
        if random.choice([True, False]):
            carve_h_corridor(new_map, prev_center_x, curr_center_x, prev_center_y)
            carve_v_corridor(new_map, prev_center_y, curr_center_y, curr_center_x)
        else:
            carve_v_corridor(new_map, prev_center_y, curr_center_y, prev_center_x)
            carve_h_corridor(new_map, prev_center_x, curr_center_x, curr_center_y)

    # Add poster walls (type 2)
    poster_count = (width * height) // 18
    for _ in range(poster_count):
        y = random.randint(1, height - 2)
        x = random.randint(1, width - 2)
        if new_map[y][x] == 1:
            new_map[y][x] = 2

    # Add HEXSTORM walls (type 3)
    hexstorm_count = (width * height) // 8
    for _ in range(hexstorm_count):
        y = random.randint(1, height - 2)
        x = random.randint(1, width - 2)
        if new_map[y][x] == 1:
            new_map[y][x] = 3

    return new_map


def carve_h_corridor(new_map, x1, x2, y):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        new_map[y][x] = 0


def carve_v_corridor(new_map, y1, y2, x):
    for y in range(min(y1, y2), max(y1, y2) + 1):
        new_map[y][x] = 0


# Bigger connected dungeon
game_map = generate_map(width=40, height=40, num_rooms=18)


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
            return (
                x * TILE_SIZE + TILE_SIZE // 2,
                y * TILE_SIZE + TILE_SIZE // 2,
            )