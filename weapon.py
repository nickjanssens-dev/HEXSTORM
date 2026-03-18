import os
import pygame
import math

from settings import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE
from map import game_map


class Weapon:
    def __init__(self):
        self.frames = [
            pygame.transform.scale(
                pygame.image.load("assets/textures/weapon/the_blue_flame_first_frame.png").convert_alpha(),
                (250, 250)
            ),
            pygame.transform.scale(
                pygame.image.load("assets/textures/weapon/the_blue_flame_second_frame.png").convert_alpha(),
                (250, 250)
            ),
            pygame.transform.scale(
                pygame.image.load("assets/textures/weapon/the_blue_flame_third_frame.png").convert_alpha(),
                (250, 250)
            ),
        ]

        # Blast effect
        blast_path = os.path.join("assets", "textures", "misc", "blast.png")
        self.blast_image = pygame.image.load(blast_path).convert_alpha()
        self.blast_image = pygame.transform.scale(self.blast_image, (240, 240))

        self.frame_index = 0
        self.animation_timer = 0
        self.animation_speed = 100

        self.is_shooting = False
        self.shoot_cooldown = 250
        self.last_shot_time = 0

        self.hit_position = None

        # Blast timing
        self.show_blast = False
        self.blast_duration = 80
        self.blast_timer = 0

        # Weapon bobbing
        self.bob_time = 0
        self.bob_speed = 0.01
        self.bob_amount_x = 8
        self.bob_amount_y = 6

    def update(self, dt, player):
        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pressed()
        current_time = pygame.time.get_ticks()

        if (keys[pygame.K_SPACE] or mouse[0]) and current_time - self.last_shot_time > self.shoot_cooldown:
            self.is_shooting = True
            self.last_shot_time = current_time
            self.frame_index = 1
            self.animation_timer = 0
            self.hit_position = self.shoot(player)

            self.show_blast = True
            self.blast_timer = self.blast_duration

        if self.is_shooting:
            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.frame_index += 1

                if self.frame_index >= len(self.frames):
                    self.frame_index = 0
                    self.is_shooting = False
                    self.hit_position = None

        else:
            self.frame_index = 0

        if self.show_blast:
            self.blast_timer -= dt
            if self.blast_timer <= 0:
                self.show_blast = False

        if player.is_moving:
            self.bob_time += dt * self.bob_speed
        else:
            self.bob_time = 0

    def shoot(self, player):
        angle = player.angle
        sin_a = math.sin(angle)
        cos_a = math.cos(angle)

        for depth in range(1, 800):
            x = player.x + depth * cos_a
            y = player.y + depth * sin_a

            map_x = int(x // TILE_SIZE)
            map_y = int(y // TILE_SIZE)

            if 0 <= map_y < len(game_map) and 0 <= map_x < len(game_map[0]):
                if game_map[map_y][map_x] > 0:
                    return (x, y)

        return None

    def draw(self, screen):
        frame = self.frames[self.frame_index]

        base_x = SCREEN_WIDTH // 2 - frame.get_width() // 2
        base_y = SCREEN_HEIGHT - frame.get_height()

        offset_x = math.sin(self.bob_time) * self.bob_amount_x
        offset_y = abs(math.cos(self.bob_time)) * self.bob_amount_y

        if self.is_shooting:
            offset_y -= 12

        weapon_x = base_x + int(offset_x)
        weapon_y = base_y + int(offset_y)

        screen.blit(frame, (weapon_x, weapon_y))

        if self.show_blast:
            self.draw_blast(screen)

    def draw_blast(self, screen):
        # Horizontal shift → right
        offset_x = 90  # increase for more right

        # Vertical shift → up (further away)
        offset_y = -60  # more negative = further away

        blast_x = SCREEN_WIDTH // 2 - self.blast_image.get_width() // 2 + offset_x
        blast_y = SCREEN_HEIGHT // 2 - self.blast_image.get_height() // 2 + offset_y

        screen.blit(self.blast_image, (blast_x, blast_y))