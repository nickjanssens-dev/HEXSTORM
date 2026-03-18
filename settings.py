import math

# Screen
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
FPS = 60
FULLSCREEN = False

# Map / world
TILE_SIZE = 64
TEXTURE_SIZE = 1024

# Raycasting
FOV = math.pi / 3
HALF_FOV = FOV / 2
NUM_RAYS = 200
MAX_DEPTH = TILE_SIZE * 20
DELTA_ANGLE = FOV / NUM_RAYS
DIST_TO_PROJ_PLANE = (SCREEN_WIDTH // 2) / math.tan(HALF_FOV)
SCALE = SCREEN_WIDTH // NUM_RAYS

# Player
PLAYER_POS_X = 96
PLAYER_POS_Y = 96
PLAYER_ANGLE = 0
PLAYER_SPEED = 3
PLAYER_ROT_SPEED = 0.04

# Colors
SKY_COLOR = (100, 150, 255)
FLOOR_COLOR = (60, 120, 60)
CROSSHAIR_COLOR = (220, 220, 220)

# Textures
WALL_TEXTURE_PATH = "assets/textures/walls/wall_panel.png"
POSTER_TEXTURE_PATH = "assets/textures/walls/wall_wanted_poster.png"
HEXSTORM_TEXTURE_PATH = "assets/textures/walls/wall_hexstorm.png"

SKY_TEXTURE_PATH = "assets/textures/sky_clouds_darker.png"
GRASS_TEXTURE_PATH = "assets/textures/floor_tiles.png"