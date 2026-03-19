import pygame
import math
import os
import settings
from fireball import Fireball
from ice_shard import IceShard

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

        # Spell selection
        self.current_spell = "Inferno burst"

        # Casting cooldown
        self.cast_cooldown = 400  # milliseconds
        self.cast_timer = 0

        # Casting animation
        self.is_casting = False
        self.cast_anim_time = 0
        self.cast_anim_duration = 180  # milliseconds

        self.projectile_pending = False
        self.spawn_data = None

        # Sounds
        self.fire_sound = None
        self.ice_sound = None
        
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        try:
            fire_path = os.path.join("assets", "textures", "sounds", "fireball.wav")
            print(f"DEBUG: Checking fire sound at {fire_path}")
            if os.path.exists(fire_path):
                s = pygame.mixer.Sound(fire_path)
                s.set_volume(0.4)
                self.fire_sound = s
                print("DEBUG: Fire sound loaded successfully")
            else:
                print("DEBUG: Fire sound file NOT FOUND")
            
            ice_path = os.path.join("assets", "textures", "sounds", "iceshard.wav")
            print(f"DEBUG: Checking ice sound at {ice_path}")
            if os.path.exists(ice_path):
                s = pygame.mixer.Sound(ice_path)
                s.set_volume(0.5)
                self.ice_sound = s
                print("DEBUG: Ice sound loaded successfully")
            else:
                print("DEBUG: Ice sound file NOT FOUND")
        except Exception as e:
            print(f"DEBUG: Sound loading failed: {e}")
            pass

    def update(self, dt, player):
        # Bobbing
        if player.is_moving:
            self.bob_time += dt * self.bob_speed
        else:
            self.bob_time = 0

        # Cooldown timer
        if self.cast_timer > 0:
            self.cast_timer -= dt

        # Animation timer
        if self.is_casting:
            old_progress = 1 - (self.cast_anim_time / self.cast_anim_duration)
            self.cast_anim_time -= dt
            if self.cast_anim_time <= 0:
                self.cast_anim_time = 0
                self.is_casting = False
            
            new_progress = 1 - (self.cast_anim_time / self.cast_anim_duration)
            
            # Spawn projectile at peak of thrust (progress = 0.5)
            if self.projectile_pending and old_progress < 0.5 <= new_progress:
                self.projectile_pending = False
                return self._spawn_projectile(player)
        
        return None

    def _spawn_projectile(self, player):
        if not self.spawn_data:
            return None
            
        spawn_x, spawn_y, angle = self.spawn_data
        self.spawn_data = None

        if self.current_spell == "Inferno burst":
            if self.fire_sound:
                self.fire_sound.play()
            return Fireball(spawn_x, spawn_y, angle)
        elif self.current_spell == "Ice shards":
            if self.ice_sound:
                self.ice_sound.play()
            return IceShard(spawn_x, spawn_y, angle)
        elif self.current_spell == "Healing touch":
            player.health = min(100, player.health + 40)
            return None
        elif self.current_spell == "Void bulwark":
            player.shield += 100
            return None
        elif self.current_spell == "Arcane bulwark":
            player.shield += 50
            return None

    def cast(self, player):
        cost = self.get_mana_cost()
        if not self.can_cast(player):
            return
            
        player.mana -= cost
        self.cast_timer = self.cast_cooldown
        self.is_casting = True
        self.cast_anim_time = self.cast_anim_duration
        self.projectile_pending = True

        # Calculate spawn data (will be used when animation hits peak)
        forward_distance = 60 
        right_offset = 8

        spawn_x = (
            player.x
            + math.cos(player.angle) * forward_distance
            + math.cos(player.angle + math.pi / 2) * right_offset
        )
        spawn_y = (
            player.y
            + math.sin(player.angle) * forward_distance
            + math.sin(player.angle + math.pi / 2) * right_offset
        )
        
        self.spawn_data = (spawn_x, spawn_y, player.angle)

    def get_mana_cost(self):
        if self.current_spell == "Inferno burst":
            return 50
        elif self.current_spell == "Ice shards":
            return 30
        elif self.current_spell == "Healing touch":
            return 40
        elif self.current_spell == "Void bulwark":
            return 80
        elif self.current_spell == "Arcane bulwark":
            return 60
        return 0

    def can_cast(self, player):
        return self.cast_timer <= 0 and player.mana >= self.get_mana_cost()

    def draw(self, screen):
        base_x = settings.SCREEN_WIDTH - self.image.get_width() - 240
        base_y = settings.SCREEN_HEIGHT - self.image.get_height() + 55

        # Bobbing
        offset_x = math.sin(self.bob_time) * self.bob_amount_x
        offset_y = abs(math.cos(self.bob_time)) * self.bob_amount_y

        # Casting animation
        cast_offset_x = 0
        cast_offset_y = 0
        cast_rotation = 0

        if self.is_casting:
            progress = 1 - (self.cast_anim_time / self.cast_anim_duration)

            if progress < 0.5:
                t = progress / 0.5
            else:
                t = 1 - ((progress - 0.5) / 0.5)

            cast_offset_x = -90 * t
            cast_offset_y = 14 * t
            cast_rotation = 10 * t

        staff_x = base_x + int(offset_x + cast_offset_x)
        staff_y = base_y + int(offset_y + cast_offset_y)

        rotated_image = pygame.transform.rotate(self.image, cast_rotation)
        screen.blit(rotated_image, (staff_x, staff_y))