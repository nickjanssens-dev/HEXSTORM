import math
import pygame
import settings

# cache
_sky_scaled = None

def reset_background_cache():
    global _sky_scaled
    _sky_scaled = None

def draw_background(screen, sky_texture, grass_texture, player):
    global _sky_scaled

    half_height = settings.SCREEN_HEIGHT // 2

    # Prepare sky once
    if _sky_scaled is None:
        _sky_scaled = pygame.transform.scale(sky_texture, (settings.SCREEN_WIDTH, half_height))

    # Sky parallax
    sky_offset = int(-player.angle * (settings.SCREEN_WIDTH / (math.pi / 2))) % settings.SCREEN_WIDTH
    screen.blit(_sky_scaled, (sky_offset, 0))
    screen.blit(_sky_scaled, (sky_offset - settings.SCREEN_WIDTH, 0))

    # Perspective Grass Floor Casting
    # Performance optimization: Render in blocks matching raycaster scale
    # This ensures a balance between visual quality and FPS
    floor_step = 6  # Vertical resolution of the floor
    tex_size = grass_texture.get_width()

    for y in range(half_height, settings.SCREEN_HEIGHT, floor_step):
        # distance = (horizon_pos * world_tile_size) / (relative_y)
        # Using a small offset to avoid division by zero
        dist = (half_height * settings.TILE_SIZE) / (y - half_height + 0.01)

        # Distance shading factor
        shade = max(60, 255 - int(dist * 0.45))
        shade_mult = shade / 255.0

        for x in range(0, settings.SCREEN_WIDTH, settings.SCALE):
            # ray_angle = player_angle - half_fov + current_column * delta_angle
            ray_angle = player.angle - settings.HALF_FOV + (x // settings.SCALE) * settings.DELTA_ANGLE

            # Calculate world coordinates
            wx = player.x + dist * math.cos(ray_angle)
            wy = player.y + dist * math.sin(ray_angle)

            # Map to texture coordinates (tiled)
            tx = int(wx) % tex_size
            ty = int(wy) % tex_size

            color = grass_texture.get_at((tx, ty))
            
            # Apply shading
            final_color = (
                int(color.r * shade_mult),
                int(color.g * shade_mult),
                int(color.b * shade_mult)
            )

            pygame.draw.rect(screen, final_color, (x, y, settings.SCALE, floor_step))