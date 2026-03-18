import math
import pygame

from settings import SCREEN_WIDTH, SCREEN_HEIGHT


def draw_background(screen, sky_texture, grass_texture, player):
    half_height = SCREEN_HEIGHT // 2

    # Sky: Parallax rotation
    # Map the player's angle (0 to 2*pi) to the screen width
    sky_offset = int(-player.angle * (SCREEN_WIDTH / (math.pi / 2))) % SCREEN_WIDTH
    sky_scaled = pygame.transform.scale(sky_texture, (SCREEN_WIDTH, half_height))

    screen.blit(sky_scaled, (sky_offset, 0))
    screen.blit(sky_scaled, (sky_offset - SCREEN_WIDTH, 0))

    # Floor: Static tiling
    tile_size = 128
    grass_tile = pygame.transform.scale(grass_texture, (tile_size, tile_size))

    for y in range(half_height, SCREEN_HEIGHT, tile_size):
        for x in range(0, SCREEN_WIDTH, tile_size):
            screen.blit(grass_tile, (x, y))