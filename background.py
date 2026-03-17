import pygame

from settings import SCREEN_WIDTH, SCREEN_HEIGHT


def draw_background(screen, sky_texture, grass_texture):
    half_height = SCREEN_HEIGHT // 2

    sky_scaled = pygame.transform.scale(sky_texture, (SCREEN_WIDTH, half_height))
    screen.blit(sky_scaled, (0, 0))

    tile_size = 128
    grass_tile = pygame.transform.scale(grass_texture, (tile_size, tile_size))

    for y in range(half_height, SCREEN_HEIGHT, tile_size):
        for x in range(0, SCREEN_WIDTH, tile_size):
            screen.blit(grass_tile, (x, y))