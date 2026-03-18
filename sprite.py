import math
import pygame

from settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    HALF_FOV,
    FOV,
    DIST_TO_PROJ_PLANE,
    SCALE,
    TILE_SIZE,
)


class Sprite:
    def __init__(self, x, y, texture, scale=0.4):
        self.x = x
        self.y = y
        self.texture = texture
        self.scale = scale
        self.width = texture.get_width()
        self.height = texture.get_height()


def render_sprites(screen, player, sprites, depth_buffer):
    sprites.sort(
        key=lambda s: math.hypot(player.x - s.x, player.y - s.y),
        reverse=True
    )

    for sprite in sprites:
        dx = sprite.x - player.x
        dy = sprite.y - player.y
        distance = math.hypot(dx, dy)

        if distance < 1:
            continue

        theta = math.atan2(dy, dx)
        alpha = theta - player.angle
        alpha = (alpha + math.pi) % (2 * math.pi) - math.pi

        if abs(alpha) < HALF_FOV + 0.2:
            screen_x = (alpha / FOV + 0.5) * SCREEN_WIDTH

            corrected_dist = distance * math.cos(alpha)
            corrected_dist = max(corrected_dist, 0.1)

            full_wall_height = int((TILE_SIZE / corrected_dist) * DIST_TO_PROJ_PLANE)

            sprite_height = max(1, int(full_wall_height * sprite.scale))
            sprite_width = max(1, int(sprite_height * (sprite.width / sprite.height)))

            half_width = sprite_width // 2
            screen_y = (SCREEN_HEIGHT // 2) + (full_wall_height // 2) - sprite_height

            step = sprite.texture.get_width() / sprite_width

            for i in range(sprite_width):
                pixel_x = int(screen_x - half_width + i)

                if 0 <= pixel_x < SCREEN_WIDTH:
                    ray_idx = int(pixel_x // SCALE)

                    if 0 <= ray_idx < len(depth_buffer):
                        if corrected_dist < depth_buffer[ray_idx]:
                            tex_x = int(i * step)

                            if 0 <= tex_x < sprite.texture.get_width():
                                column = sprite.texture.subsurface(
                                    tex_x, 0, 1, sprite.texture.get_height()
                                )
                                column_scaled = pygame.transform.scale(
                                    column, (1, sprite_height)
                                )
                                screen.blit(column_scaled, (pixel_x, screen_y))