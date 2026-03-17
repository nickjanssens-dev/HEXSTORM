import pygame

from player import Player
from raycasting import ray_casting
from settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
    PLAYER_POS_X,
    PLAYER_POS_Y,
    PLAYER_ANGLE,
    PLAYER_SPEED,
    PLAYER_ROT_SPEED,
    CROSSHAIR_COLOR,
    WALL_TEXTURE_PATH,
    SKY_TEXTURE_PATH,
    GRASS_TEXTURE_PATH,
)

def draw_background(screen, sky_texture, grass_texture):
    half_height = SCREEN_HEIGHT // 2

    sky_scaled = pygame.transform.scale(sky_texture, (SCREEN_WIDTH, half_height))
    screen.blit(sky_scaled, (0, 0))

    tile_size = 128
    grass_tile = pygame.transform.scale(grass_texture, (tile_size, tile_size))

    for y in range(half_height, SCREEN_HEIGHT, tile_size):
        for x in range(0, SCREEN_WIDTH, tile_size):
            screen.blit(grass_tile, (x, y))

def draw_crosshair(screen):
    center_x = SCREEN_WIDTH // 2
    center_y = SCREEN_HEIGHT // 2
    size = 8

    pygame.draw.line(screen, CROSSHAIR_COLOR, (center_x - size, center_y), (center_x + size, center_y), 2)
    pygame.draw.line(screen, CROSSHAIR_COLOR, (center_x, center_y - size), (center_x, center_y + size), 2)

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

    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        player.movement()

        draw_background(screen, sky_texture, grass_texture)
        ray_casting(screen, player, wall_texture)
        draw_crosshair(screen)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()