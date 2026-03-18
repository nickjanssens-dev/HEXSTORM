import pygame
import random

from background import draw_background
from hud import draw_hud, load_hud, get_fullscreen_button_rect
from player import Player
from raycasting import ray_casting
from weapon import Weapon
from settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
    FULLSCREEN,
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


def load_textures():
    wall_texture = pygame.image.load(WALL_TEXTURE_PATH).convert()
    poster_texture = pygame.image.load(POSTER_TEXTURE_PATH).convert()
    hexstorm_texture = pygame.image.load(HEXSTORM_TEXTURE_PATH).convert()

    sky_texture = pygame.image.load(SKY_TEXTURE_PATH).convert()
    grass_texture = pygame.image.load(GRASS_TEXTURE_PATH).convert()

    textures = {
        1: wall_texture,
        2: poster_texture,
        3: hexstorm_texture,
    }

    return textures, sky_texture, grass_texture


def create_plant_sprites(amount=15):
    sprites = []

    plant_texture = pygame.image.load(
        "assets/textures/sprites/plant_fern.png"
    ).convert_alpha()

    # Crop to visible plant area
    plant_texture = plant_texture.subsurface((253, 232, 502, 512)).copy()

    for _ in range(amount):
        while True:
            sx = random.randint(1, len(game_map[0]) - 2)
            sy = random.randint(1, len(game_map) - 2)

            if game_map[sy][sx] == 0:
                sprite_x = sx * TILE_SIZE + TILE_SIZE // 2
                sprite_y = sy * TILE_SIZE + TILE_SIZE // 2
                sprites.append(Sprite(sprite_x, sprite_y, plant_texture))
                break

    return sprites


def main():
    pygame.init()

    # Initial screen setup
    flags = pygame.SCALED
    if FULLSCREEN:
        flags |= pygame.FULLSCREEN

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
    pygame.display.set_caption("HEXSTORM - Raycasting Prototype")
    clock = pygame.time.Clock()

    load_hud()

    textures, sky_texture, grass_texture = load_textures()

    start_x, start_y = get_free_pos()
    player = Player(
        start_x,
        start_y,
        PLAYER_ANGLE,
        PLAYER_SPEED,
        PLAYER_ROT_SPEED
    )

    sprites = create_plant_sprites(15)
    weapon = Weapon()

    # Wave system
    wave = 1
    kills = 0
    game_over = False

    running = True
    while running:
        dt = clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left click
                    if get_fullscreen_button_rect().collidepoint(event.pos):
                        # Toggle fullscreen
                        if screen.get_flags() & pygame.FULLSCREEN:
                            pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SCALED)
                        else:
                            pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SCALED | pygame.FULLSCREEN)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    # Toggle fullscreen
                    if screen.get_flags() & pygame.FULLSCREEN:
                        pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SCALED)
                    else:
                        pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SCALED | pygame.FULLSCREEN)

        player.movement()
        weapon.update(dt, player)

        draw_background(screen, sky_texture, grass_texture, player)

        depth_buffer = ray_casting(screen, player, textures)
        render_sprites(screen, player, sprites, depth_buffer)
        weapon.draw(screen)
        draw_hud(screen, player, wave=wave, kills=kills, game_over=game_over)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()