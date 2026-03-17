from settings import TILE_SIZE

game_map = [
    [1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1],
]

def is_wall(x, y):
    map_x = int(x // TILE_SIZE)
    map_y = int(y // TILE_SIZE)

    if 0 <= map_y < len(game_map) and 0 <= map_x < len(game_map[0]):
        return game_map[map_y][map_x] == 1
    return True