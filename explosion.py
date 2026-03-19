import pygame
import random
import math
import settings

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        # Local offsets in world space (relative to explosion center)
        self.vx = random.uniform(-40, 40)
        self.vy = random.uniform(-40, 40)
        self.life = random.randint(500, 1000) # Longer life
        self.max_life = self.life
        self.color = random.choice([
            (255, 230, 100), # Bright Yellow
            (255, 180, 50),  # Orange-Yellow
            (255, 80, 0),    # Bright Orange
            (255, 40, 0),    # Red-Orange
            (150, 20, 0),    # Deep Red
            (80, 80, 80)     # Smoke
        ])
        self.size = random.randint(8, 20) # Bigger particles

    def update(self, dt):
        self.x += self.vx * (dt / 1000.0)
        self.y += self.vy * (dt / 1000.0)
        self.life -= dt
        return self.life > 0

class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.particles = [Particle(x, y) for _ in range(60)] # More particles
        self.alive = True
        self.z_offset = -10 # Matches fireball height roughly

    def update(self, dt):
        alive_particles = []
        for p in self.particles:
            if p.update(dt):
                alive_particles.append(p)
        self.particles = alive_particles
        
        if not self.particles:
            self.alive = False

    def draw(self, screen, player, depth_buffer):
        """Draw explosion particles as pseudo-3D sprites with depth check"""
        for p in self.particles:
            dx = p.x - player.x
            dy = p.y - player.y
            distance = math.hypot(dx, dy)

            # Basic raycasting projection for each particle
            angle_to_player = math.atan2(dy, dx) - player.angle
            while angle_to_player > math.pi: angle_to_player -= 2 * math.pi
            while angle_to_player < -math.pi: angle_to_player += 2 * math.pi

            if abs(angle_to_player) > math.pi / 2:
                continue

            corrected_depth = distance * math.cos(angle_to_player)
            if corrected_depth < 0.1: corrected_depth = 0.1

            proj_factor = settings.DIST_TO_PROJ_PLANE
            
            # Simple screen projection
            try:
                # Reusing the alpha-based screen_x logic from sprite.py for consistency
                screen_x = (angle_to_player / settings.FOV + 0.5) * settings.SCREEN_WIDTH
            except:
                continue

            # Depth check against walls
            ray_idx = int(screen_x // settings.SCALE)
            if 0 <= ray_idx < len(depth_buffer):
                if corrected_depth > depth_buffer[ray_idx] + 10: # Small offset to avoid clipping
                    continue

            # Vertical position (z-offset applied to center)
            # Standard sprite screen_y logic
            full_wall_height = int((settings.TILE_SIZE / corrected_depth) * proj_factor)
            screen_y = (settings.SCREEN_HEIGHT // 2) + (full_wall_height // 2) + (self.z_offset / corrected_depth * proj_factor)
            
            # Particle size based on distance and life
            life_ratio = p.life / p.max_life
            p_size = (p.size * life_ratio * 15 / corrected_depth) * proj_factor / 100
            
            if p_size > 1:
                # Fade color based on life
                color = list(p.color)
                # Drawing a slightly transparent circle
                s = pygame.Surface((int(p_size*2), int(p_size*2)), pygame.SRCALPHA)
                alpha = int(255 * (life_ratio ** 0.5)) # Fade out slower
                pygame.draw.circle(s, (*color, alpha), (int(p_size), int(p_size)), int(p_size))
                screen.blit(s, (int(screen_x - p_size), int(screen_y - p_size)))
