import pygame
import math
import settings

class Sprite:
    def __init__(self, x, y, texture, scale=0.4, z_offset=0):
        self.x = x
        self.y = y
        self.texture = texture
        self.scale = scale

        # 🔥 vertical control
        self.z_offset = z_offset     # world height (like floating)
        self.y_offset = 0            # screen adjustment (like enemies)

        self.width = texture.get_width()
        self.height = texture.get_height()

def render_sprites(screen, player, sprites, depth_buffer):
    visible_sprites = [
        sprite for sprite in sprites
        if not hasattr(sprite, "alive") or sprite.alive
    ]

    visible_sprites.sort(
        key=lambda s: math.hypot(player.x - s.x, player.y - s.y),
        reverse=True
    )

    for sprite in visible_sprites:
        dx = sprite.x - player.x
        dy = sprite.y - player.y
        distance = math.hypot(dx, dy)

        if distance < 1:
            continue

        theta = math.atan2(dy, dx)
        alpha = theta - player.angle
        alpha = (alpha + math.pi) % (2 * math.pi) - math.pi

        if abs(alpha) < settings.HALF_FOV + 0.2:

            # screen X
            screen_x = (alpha / settings.FOV + 0.5) * settings.SCREEN_WIDTH

            # perspective correction
            corrected_dist = distance * math.cos(alpha)
            corrected_dist = max(corrected_dist, 0.1)

            # projection size
            full_wall_height = int(
                (settings.TILE_SIZE / corrected_dist) * settings.DIST_TO_PROJ_PLANE
            )

            sprite_height = max(1, int(full_wall_height * sprite.scale))
            sprite_width = max(1, int(sprite_height * (sprite.width / sprite.height)))

            half_width = sprite_width // 2

            # vertical positioning
            z_offset = getattr(sprite, 'z_offset', 0)
            y_offset = getattr(sprite, 'y_offset', 0)

            proj_z = int(z_offset / corrected_dist * settings.DIST_TO_PROJ_PLANE)

            # FIXED grounding formula (matches enemies better)
            screen_y = (
                settings.SCREEN_HEIGHT // 2
                + full_wall_height // 2
                - sprite_height
                + proj_z
                + y_offset
            )

            step = sprite.texture.get_width() / sprite_width

            for i in range(sprite_width):
                pixel_x = int(screen_x - half_width + i)

                if 0 <= pixel_x < settings.SCREEN_WIDTH:
                    ray_idx = int(pixel_x // settings.SCALE)

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