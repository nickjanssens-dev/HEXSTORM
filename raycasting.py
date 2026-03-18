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

def ray_casting(screen, player, textures):
    start_angle = player.angle - HALF_FOV
    depth_buffer = []

    for ray in range(NUM_RAYS):
        ray_angle = (start_angle + ray * DELTA_ANGLE) % math.tau

        sin_a = math.sin(ray_angle)
        cos_a = math.cos(ray_angle)

        for depth in range(1, MAX_DEPTH):
            target_x = player.x + depth * cos_a
            target_y = player.y + depth * sin_a

            wall_type = is_wall(target_x, target_y)
            if wall_type > 0:
                corrected_depth = depth * math.cos(player.angle - ray_angle)
                corrected_depth = max(corrected_depth, 0.0001)
                depth_buffer.append(corrected_depth)

                wall_height = max(
                    1,
                    int((TILE_SIZE / corrected_depth) * DIST_TO_PROJ_PLANE)
                )
                wall_top = (SCREEN_HEIGHT // 2) - wall_height // 2

                hit_x = target_x % TILE_SIZE
                hit_y = target_y % TILE_SIZE

                wall_texture = textures.get(wall_type, textures.get(1))

                if hit_x < 1 or hit_x > TILE_SIZE - 1:
                    texture_x = int((hit_y / TILE_SIZE) * TEXTURE_SIZE)
                else:
                    texture_x = int((hit_x / TILE_SIZE) * TEXTURE_SIZE)

                texture_x = max(0, min(TEXTURE_SIZE - 1, texture_x))

                texture_column = wall_texture.subsurface(texture_x, 0, 1, TEXTURE_SIZE)
                wall_column = pygame.transform.scale(texture_column, (SCALE, wall_height))

                shade = max(50, 255 - int(corrected_depth * 0.5))
                wall_column.fill((shade, shade, shade), special_flags=pygame.BLEND_MULT)

                screen.blit(wall_column, (ray * SCALE, wall_top))
                break
        else:
            depth_buffer.append(MAX_DEPTH)

    return depth_buffer