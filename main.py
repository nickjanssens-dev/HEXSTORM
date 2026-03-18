import pygame
import random

from background import draw_background
from hud import draw_crosshair, draw_hud
from player import Player
from raycasting import ray_casting
from weapon import Weapon
from hud import draw_crosshair, draw_hud, load_hud
from settings import (
    SCALE,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
    PLAYER_POS_X,
    PLAYER_POS_Y,
    PLAYER_ANGLE,
    PLAYER_SPEED,
    PLAYER_ROT_SPEED,
    WALL_TEXTURE_PATH,
    SKY_TEXTURE_PATH,
    GRASS_TEXTURE_PATH,
    POSTER_TEXTURE_PATH,
    HEXSTORM_TEXTURE_PATH,
)
from map import get_free_pos, game_map, TILE_SIZE
from sprite import Sprite, render_sprites


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    load_hud()

    wall_texture = pygame.image.load(WALL_TEXTURE_PATH).convert()
    poster_texture = pygame.image.load(POSTER_TEXTURE_PATH).convert()
    hexstorm_texture = pygame.image.load(HEXSTORM_TEXTURE_PATH).convert()
    textures = {1: wall_texture, 2: poster_texture, 3: hexstorm_texture}

    sky_texture = pygame.image.load(SKY_TEXTURE_PATH).convert()
    grass_texture = pygame.image.load(GRASS_TEXTURE_PATH).convert()

    plant_texture = pygame.image.load("assets/textures/sprites/plant_fern.png").convert_alpha()
    # Crop to actual plant bounds to avoid floating
    plant_texture = plant_texture.subsurface((253, 232, 502, 512))

    pygame.display.set_caption("HEXSTORM - Raycasting Prototype")
    clock = pygame.time.Clock()

    start_x, start_y = get_free_pos()
    player = Player(
        start_x,
        start_y,
        PLAYER_ANGLE,
        PLAYER_SPEED,
        PLAYER_ROT_SPEED
    )

    # Initialize sprites
    sprites = []
    # Place 15 ferns randomly in empty tiles
    for _ in range(15):
        while True:
            sx = random.randint(1, len(game_map[0]) - 2)
            sy = random.randint(1, len(game_map) - 2)
            if game_map[sy][sx] == 0:
                sprites.append(Sprite(sx * TILE_SIZE + 32, sy * TILE_SIZE + 32, plant_texture))
                break

    weapon = Weapon()

    running = True
    while running:
        dt = clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        player.movement()
        weapon.update(dt, player)

        draw_background(screen, sky_texture, grass_texture, player)
        depth_buffer = ray_casting(screen, player, textures)
        render_sprites(screen, player, sprites, depth_buffer)

        weapon.draw(screen)
        draw_crosshair(screen)
        draw_hud(screen, player)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()