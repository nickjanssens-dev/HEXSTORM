import math
import pygame

from settings import SCREEN_WIDTH, SCREEN_HEIGHT

# cache
_sky_scaled = None
_grass_tile = None


def draw_background(screen, sky_texture, grass_texture, player):
    global _sky_scaled, _grass_tile

    half_height = SCREEN_HEIGHT // 2

    # Prepare sky once
    if _sky_scaled is None:
        _sky_scaled = pygame.transform.scale(sky_texture, (SCREEN_WIDTH, half_height))

    # Prepare grass once: crop instead of scaling whole texture
    if _grass_tile is None:
        tile_size = 512
        _grass_tile = grass_texture.subsurface((0, 0, tile_size, tile_size)).copy()

    # Sky parallax
    sky_offset = int(-player.angle * (SCREEN_WIDTH / (math.pi / 2))) % SCREEN_WIDTH
    screen.blit(_sky_scaled, (sky_offset, 0))
    screen.blit(_sky_scaled, (sky_offset - SCREEN_WIDTH, 0))

    # Grass floor
    tile_size = _grass_tile.get_width()
    for y in range(half_height, SCREEN_HEIGHT, tile_size):
        for x in range(0, SCREEN_WIDTH, tile_size):
            screen.blit(_grass_tile, (x, y))