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

        self.health = 100
        self.max_mana = 2000
        self.mana = self.max_mana
        self.regen_rate = 50 # mana per second
        self.current_spell = "Firebolt"

        self.is_moving = False
        self.shooting = False

        # NEW
        self.alive = True
        self.shield = 0

    def movement(self):
        # Don't move if dead
        if not self.alive:
            return

        keys = pygame.key.get_pressed()

        sin_a = math.sin(self.angle)
        cos_a = math.cos(self.angle)

        dx = 0
        dy = 0

        if keys[pygame.K_UP]:
            dx += cos_a * self.speed
            dy += sin_a * self.speed
        if keys[pygame.K_DOWN]:
            dx -= cos_a * self.speed
            dy -= sin_a * self.speed

        if keys[pygame.K_LEFT]:
            dx += sin_a * self.speed
            dy -= cos_a * self.speed
        if keys[pygame.K_RIGHT]:
            dx -= sin_a * self.speed
            dy += cos_a * self.speed

        if keys[pygame.K_s]:
            self.angle -= self.rot_speed
        if keys[pygame.K_d]:
            self.angle += self.rot_speed

        self.angle %= math.tau

        self.is_moving = dx != 0 or dy != 0
        self.move_with_collision(dx, dy)

    def move_with_collision(self, dx, dy):
        new_x = self.x + dx
        new_y = self.y + dy

        if not is_wall(new_x, self.y):
            self.x = new_x
        if not is_wall(self.x, new_y):
            self.y = new_y

    def take_damage(self, amount):
        if not self.alive:
            return

        if self.shield > 0:
            if self.shield >= amount:
                self.shield -= amount
                amount = 0
            else:
                amount -= self.shield
                self.shield = 0

        self.health -= amount

        # Optional: clamp
        if self.health < 0:
            self.health = 0

        # Death handling
        if self.health == 0:
            self.alive = False

    def regenerate_mana(self, dt):
        if not self.alive:
            return
            
        if self.mana < self.max_mana:
            self.mana += self.regen_rate * (dt / 1000.0)
            if self.mana > self.max_mana:
                self.mana = self.max_mana