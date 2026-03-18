import pygame
import math
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

class Staff:
    def __init__(self):
        self.image = pygame.image.load(
            "assets/textures/weapon/staff_no_bg.png"
        ).convert_alpha()

        self.image = pygame.transform.scale(self.image, (280, 280))
        self.image = pygame.transform.rotate(self.image, 18)

        # Bobbing
        self.bob_time = 0
        self.bob_speed = 0.01
        self.bob_amount_x = 6
        self.bob_amount_y = 5

    # UPDATE
    def update(self, dt, player):
        if player.is_moving:
            self.bob_time += dt * self.bob_speed
        else:
            self.bob_time = 0

    # DRAW
    def draw(self, screen):
        # Base position (RIGHT SIDE)
        base_x = SCREEN_WIDTH - self.image.get_width() - 240
        base_y = SCREEN_HEIGHT - self.image.get_height() + 55

        # Bobbing
        offset_x = math.sin(self.bob_time) * self.bob_amount_x
        offset_y = abs(math.cos(self.bob_time)) * self.bob_amount_y

        staff_x = base_x + int(offset_x)
        staff_y = base_y + int(offset_y)

        screen.blit(self.image, (staff_x, staff_y))