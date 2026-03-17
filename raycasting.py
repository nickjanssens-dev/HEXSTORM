import math
import pygame

from map import is_wall
from settings import (
    SCREEN_HEIGHT,
    HALF_FOV,
    NUM_RAYS,
    MAX_DEPTH,
    DELTA_ANGLE,
    DIST_TO_PROJ_PLANE,
    SCALE,
    TILE_SIZE,
    TEXTURE_SIZE,
)

def ray_casting(screen, player, wall_texture):
    start_angle = player.angle - HALF_FOV

    for ray in range(NUM_RAYS):
        ray_angle = start_angle + ray * DELTA_ANGLE

        sin_a = math.sin(ray_angle)
        cos_a = math.cos(ray_angle)

        for depth in range(1, MAX_DEPTH):
            target_x = player.x + depth * cos_a
            target_y = player.y + depth * sin_a

            if is_wall(target_x, target_y):
                corrected_depth = depth * math.cos(player.angle - ray_angle)
                corrected_depth = max(corrected_depth, 0.0001)

                wall_height = int((TILE_SIZE / corrected_depth) * DIST_TO_PROJ_PLANE)

                # Determine where the ray hit the wall
                hit_x = target_x % TILE_SIZE
                hit_y = target_y % TILE_SIZE

                # Pick the texture column based on hit position
                if hit_x < 1 or hit_x > TILE_SIZE - 1:
                    texture_x = int((hit_y / TILE_SIZE) * TEXTURE_SIZE)
                else:
                    texture_x = int((hit_x / TILE_SIZE) * TEXTURE_SIZE)

                texture_x = max(0, min(TEXTURE_SIZE - 1, texture_x))

                # Take 1 vertical column from the texture
                texture_column = wall_texture.subsurface(texture_x, 0, 1, TEXTURE_SIZE)

                # Scale it to projected wall height
                wall_column = pygame.transform.scale(texture_column, (SCALE, wall_height))

                # Distance shading
                shade = max(50, 255 - int(corrected_depth * 0.5))
                wall_column.fill((shade, shade, shade), special_flags=pygame.BLEND_MULT)

                screen.blit(
                    wall_column,
                    (ray * SCALE, (SCREEN_HEIGHT // 2) - wall_height // 2)
                )
                break