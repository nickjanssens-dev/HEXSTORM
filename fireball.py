import pygame

import math



class Fireball:

    def __init__(self, x, y, angle):

        self.texture = pygame.image.load(

            "assets/textures/magic/fireball_no_bg.png"

        ).convert_alpha()



        self.texture = pygame.transform.scale(self.texture, (96, 96))



        self.x = x

        self.y = y

        self.z_offset = -8

        self.angle = angle

        self.scale = 0.33



        self.width = self.texture.get_width()

        self.height = self.texture.get_height()



        self.speed = 500

        self.lifetime = 10000  # 10 seconds (effectively until it hits something)

        self.alive = True



        # Combat

        self.damage = 25

        self.hit_radius = 60

        self.aoe_radius = 120



    def update(self, dt):

        dt_seconds = dt / 1000.0



        self.x += math.cos(self.angle) * self.speed * dt_seconds

        self.y += math.sin(self.angle) * self.speed * dt_seconds



        self.lifetime -= dt

        if self.lifetime <= 0:

            self.alive = False