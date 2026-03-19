import pygame
import math

class IceShard:
    def __init__(self, x, y, angle):
        self.texture = pygame.image.load(
            "assets/textures/magic/ice_shard.png"
        ).convert_alpha()

        self.texture = pygame.transform.scale(self.texture, (96, 96))

        self.x = x
        self.y = y
        self.z_offset = -8
        self.angle = angle
        self.scale = 0.44

        self.width = self.texture.get_width()
        self.height = self.texture.get_height()

        self.speed = 700   # faster than fireball
        self.lifetime = 1200
        self.alive = True

        self.damage = 15
        self.hit_radius = 20
        self.slow_factor = 0.5
        self.slow_duration = 2000 # ms

    def update(self, dt):
        dt_seconds = dt / 1000.0

        self.x += math.cos(self.angle) * self.speed * dt_seconds
        self.y += math.sin(self.angle) * self.speed * dt_seconds

        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False