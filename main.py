import pygame
import random

from background import draw_background
from hud import draw_hud, load_hud, get_fullscreen_button_rect
from player import Player
from raycasting import ray_casting
from weapon import Weapon
from bat import Enemy   # change to: from bat import Enemy  if your file is bat.py
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


def create_bats(amount=3):
    bats = []

    for _ in range(amount):
        while True:
            sx = random.randint(1, len(game_map[0]) - 2)
            sy = random.randint(1, len(game_map) - 2)

            if game_map[sy][sx] == 0:
                bat_x = sx * TILE_SIZE + TILE_SIZE // 2
                bat_y = sy * TILE_SIZE + TILE_SIZE // 2
                bats.append(Enemy(bat_x, bat_y))
                break

    return bats


def draw_game_over(screen):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    font_big = pygame.font.SysFont("Arial", 80, bold=True)
    font_small = pygame.font.SysFont("Arial", 28)

    game_over_text = font_big.render("GAME OVER", True, (255, 50, 50))
    restart_text = font_small.render("Press R to restart", True, (255, 255, 255))

    game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
    restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))

    screen.blit(game_over_text, game_over_rect)
    screen.blit(restart_text, restart_rect)


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
    bats = create_bats(3)
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
                if event.button == 1:  # Left click
                    if get_fullscreen_button_rect().collidepoint(event.pos):
                        if screen.get_flags() & pygame.FULLSCREEN:
                            screen = pygame.display.set_mode(
                                (SCREEN_WIDTH, SCREEN_HEIGHT),
                                pygame.SCALED
                            )
                        else:
                            screen = pygame.display.set_mode(
                                (SCREEN_WIDTH, SCREEN_HEIGHT),
                                pygame.SCALED | pygame.FULLSCREEN
                            )

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    if screen.get_flags() & pygame.FULLSCREEN:
                        screen = pygame.display.set_mode(
                            (SCREEN_WIDTH, SCREEN_HEIGHT),
                            pygame.SCALED
                        )
                    else:
                        screen = pygame.display.set_mode(
                            (SCREEN_WIDTH, SCREEN_HEIGHT),
                            pygame.SCALED | pygame.FULLSCREEN
                        )

                if event.key == pygame.K_r and game_over:
                    main()
                    return

        if not game_over:
            player.movement()
            weapon.update(dt, player)

            for bat in bats:
                bat.update(player, dt)

            if player.health <= 0:
                game_over = True

        draw_background(screen, sky_texture, grass_texture, player)

        depth_buffer = ray_casting(screen, player, textures)
        render_sprites(screen, player, sprites, depth_buffer)

        for bat in bats:
            bat.draw(screen, player)

        weapon.draw(screen)
        draw_hud(screen, player, wave=wave, kills=kills, game_over=game_over)

        if game_over:
            draw_game_over(screen)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()