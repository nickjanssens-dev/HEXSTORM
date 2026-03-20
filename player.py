import math
import pygame

from map import is_wall
from controls import CONTROLS

class Player:
    def __init__(self, x, y, angle, speed, rot_speed, health=100, max_mana=2000, mana_regen_rate=50):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        self.rot_speed = rot_speed

        self.health = health
        self.max_health = health  # Store max health for healing
        self.max_mana = max_mana
        self.mana = self.max_mana
        self.regen_rate = mana_regen_rate # mana per second
        self.current_spell = "Firebolt"

        self.is_moving = False
        self.shooting = False
        
        # NEW
        self.alive = True
        self.shield = 0
        
        # Damage reduction
        self.damage_reduction = 0.0  # 0.0 = no reduction, 0.5 = 50% reduction
        self.damage_reduction_end_time = 0  # When the buff expires

    def movement(self):
        # Don't move if dead
        if not self.alive:
            return

        keys = pygame.key.get_pressed()

        sin_a = math.sin(self.angle)
        cos_a = math.cos(self.angle)

        dx = 0
        dy = 0

        # Movement using CONTROLS dictionary
        if keys[CONTROLS["move_forward"]]:
            dx += cos_a * self.speed
            dy += sin_a * self.speed
        if keys[CONTROLS["move_backward"]]:
            dx -= cos_a * self.speed
            dy -= sin_a * self.speed
        if keys[CONTROLS["move_left"]]:
            dx += sin_a * self.speed
            dy -= cos_a * self.speed
        if keys[CONTROLS["move_right"]]:
            dx -= sin_a * self.speed
            dy += cos_a * self.speed

        # Turning using CONTROLS dictionary
        if keys[CONTROLS["turn_left"]]:
            self.angle -= self.rot_speed
        if keys[CONTROLS["turn_right"]]:
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

        # Apply damage reduction if active
        if self.damage_reduction > 0:
            amount *= (1.0 - self.damage_reduction)

        if self.shield > 0:
            if self.shield >= amount:
                self.shield -= amount
                amount = 0
            else:
                amount -= self.shield
                self.shield = 0

        self.health -= amount
        self.health = max(0, int(self.health))

        # Death handling
        if self.health == 0:
            self.alive = False

    def update_damage_reduction(self, current_time):
        """Check if damage reduction buff has expired"""
        if self.damage_reduction_end_time > 0 and current_time >= self.damage_reduction_end_time:
            self.damage_reduction = 0.0
            self.damage_reduction_end_time = 0

    def update(self, current_time):
        self.update_damage_reduction(current_time)

    def regenerate_mana(self, dt):
        if not self.alive:
            return
            
        if self.mana < self.max_mana:
            self.mana += self.regen_rate * (dt / 1000.0)
            if self.mana > self.max_mana:
                self.mana = self.max_mana