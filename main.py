import pygame

from background import draw_background
from hud import draw_crosshair, draw_hud
from player import Player
from raycasting import ray_casting
from weapon import Weapon
from settings import (
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
)


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    wall_texture = pygame.image.load(WALL_TEXTURE_PATH).convert()
    sky_texture = pygame.image.load(SKY_TEXTURE_PATH).convert()
    grass_texture = pygame.image.load(GRASS_TEXTURE_PATH).convert()

    pygame.display.set_caption("HEXSTORM - Raycasting Prototype")
    clock = pygame.time.Clock()

    player = Player(
        PLAYER_POS_X,
        PLAYER_POS_Y,
        PLAYER_ANGLE,
        PLAYER_SPEED,
        PLAYER_ROT_SPEED
    )

    weapon = Weapon()

    running = True
    while running:
        dt = clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        player.movement()
        weapon.update(dt, player)

        draw_background(screen, sky_texture, grass_texture)
        ray_casting(screen, player, wall_texture)
        weapon.draw(screen)
        draw_crosshair(screen)
        draw_hud(screen, player)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()