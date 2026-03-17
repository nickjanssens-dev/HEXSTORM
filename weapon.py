import pygame

from settings import SCREEN_WIDTH, SCREEN_HEIGHT


class Weapon:
    def __init__(self):
        self.frames = [
            pygame.transform.scale(
                pygame.image.load("assets/textures/weapon/the_blue_flame_first_frame.png").convert_alpha(),(250, 250)
            ),
            pygame.transform.scale(
                pygame.image.load("assets/textures/weapon/the_blue_flame_second_frame.png").convert_alpha(), (250, 250)
            ),
            pygame.transform.scale(
                pygame.image.load("assets/textures/weapon/the_blue_flame_third_frame.png").convert_alpha(), (250, 250)
            ),
        ]

        self.frame_index = 0
        self.animation_timer = 0
        self.animation_speed = 140  # milliseconds

    def update(self, dt, player):
        if player.is_moving:
            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.frame_index = (self.frame_index + 1) % len(self.frames)
        else:
            self.frame_index = 0

    def draw(self, screen):
        frame = self.frames[self.frame_index]

        weapon_x = SCREEN_WIDTH // 2 - frame.get_width() // 2
        weapon_y = SCREEN_HEIGHT - frame.get_height()

        screen.blit(frame, (weapon_x, weapon_y))