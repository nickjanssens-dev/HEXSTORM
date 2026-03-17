import math
import pygame

from map import is_wall

class Player:
    def __init__(self, x, y, angle, speed, rot_speed):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        self.rot_speed = rot_speed

    def movement(self):
        keys = pygame.key.get_pressed()

        sin_a = math.sin(self.angle)
        cos_a = math.cos(self.angle)

        dx = 0
        dy = 0

        # Forward / backward (Arrow keys)
        if keys[pygame.K_UP]:
            dx += cos_a * self.speed
            dy += sin_a * self.speed
        if keys[pygame.K_DOWN]:
            dx -= cos_a * self.speed
            dy -= sin_a * self.speed

        # Left / right (Arrow keys)
        if keys[pygame.K_LEFT]:
            dx += sin_a * self.speed
            dy -= cos_a * self.speed
        if keys[pygame.K_RIGHT]:
            dx -= sin_a * self.speed
            dy += cos_a * self.speed

        # Rotate camera with S / D
        if keys[pygame.K_s]:
            self.angle -= self.rot_speed
        if keys[pygame.K_d]:
            self.angle += self.rot_speed

        self.move_with_collision(dx, dy)

    def move_with_collision(self, dx, dy):
        new_x = self.x + dx
        new_y = self.y + dy

        if not is_wall(new_x, self.y):
            self.x = new_x
        if not is_wall(self.x, new_y):
            self.y = new_y