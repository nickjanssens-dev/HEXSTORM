import pygame
import math
import os
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, DIST_TO_PROJ_PLANE, TILE_SIZE


class Enemy:
    # Class-level cache for animations and sounds to avoid redundant loading
    _animations_cache = {}
    _attack_sound = None
    _fly_sound = None

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 0.01  # Much slower travel speed
        self.health = 100
        self.alive = True
        self.damage = 10
        self.attack_cooldown = 2000  # ms (2 seconds)
        self.attack_timer = 0

        # Each frame in the source assets is 64x64
        self.frame_size = 64

        # Load assets only if not already cached
        if not Enemy._animations_cache:
            Enemy._animations_cache = {
                "idle": self._load_sheet("Bat-IdleFly.png"),
                "run": self._load_sheet("Bat-Run.png"),
                "attack": self._load_sheet("Bat-Attack1.png") + self._load_sheet("Bat-Attack2.png"),
                "hurt": self._load_sheet("Bat-Hurt.png"),
                "die": self._load_sheet("Bat-Die.png"),
                "sleep": self._load_sheet("Bat-Sleep.png"),
                "wakeup": self._load_sheet("Bat-WakeUp.png"),
            }

            # Try to load sounds
            try:
                bat_dir = os.path.join("assets", "textures", "enemy", "bat")

                att_path = os.path.join(bat_dir, "attack.wav")
                if os.path.exists(att_path):
                    Enemy._attack_sound = pygame.mixer.Sound(att_path)

                fly_path = os.path.join(bat_dir, "fly.wav")
                if os.path.exists(fly_path):
                    Enemy._fly_sound = pygame.mixer.Sound(fly_path)
                    Enemy._fly_sound.set_volume(0.3)  # Subtle flap sound
            except (pygame.error, Exception) as e:
                print(f"Warning: Could not load enemy sounds: {e}")

        self.state = "idle"
        self.anim_index = 0.0
        self.anim_speed = 0.012  # Frames per millisecond
        self.current_sprite = Enemy._animations_cache[self.state][0]

    def _load_sheet(self, filename):
        """Helper to load a sprite sheet and slice it into 64x64 frames"""
        path = os.path.join("assets", "textures", "enemy", "bat", filename)
        try:
            sheet = pygame.image.load(path).convert_alpha()
        except (pygame.error, FileNotFoundError) as e:
            print(f"Error loading {path}: {e}")
            fail = pygame.Surface((64, 64))
            fail.fill((255, 0, 255))
            return [fail]

        sheet_w, sheet_h = sheet.get_size()
        frames = []
        for i in range(0, sheet_w, self.frame_size):
            try:
                width = min(self.frame_size, sheet_w - i)
                if width <= 0: break
                frame = sheet.subsurface((i, 0, width, sheet_h))
                frames.append(frame)
            except ValueError:
                break
        return frames if frames else [pygame.Surface((64, 64))]

    def update_animation(self, dt):
        """Update animation based on elapsed time (dt)"""
        frames = Enemy._animations_cache[self.state]
        self.anim_index += self.anim_speed * dt

        if self.anim_index >= len(frames):
            if self.state == "die":
                self.anim_index = len(frames) - 1
            else:
                self.anim_index = 0
                # Play flight sound on wings flap (reset to frame 0)
                if (self.state == "idle" or self.state == "run") and Enemy._fly_sound:
                    Enemy._fly_sound.play()

        self.current_sprite = frames[int(self.anim_index)]

    @property
    def animation_finished(self):
        frames = Enemy._animations_cache[self.state]
        return self.anim_index >= len(frames) - 1

    def update_state(self, player):
        """Determine enemy state based on distance to player and alive status"""
        if not self.alive:
            new_state = "die"
        else:
            dx = player.x - self.x
            dy = player.y - self.y
            distance_tiles = math.hypot(dx, dy) / TILE_SIZE

            if distance_tiles > 10:
                new_state = "idle"
            elif distance_tiles > 0.5:
                new_state = "run"
            else:
                new_state = "attack"

        if new_state != self.state:
            self.state = new_state
            self.anim_index = 0.0

    def update(self, player, dt):
        """Update enemy AI using delta time (dt)"""
        self.update_state(player)

        # Update attack timer
        if self.attack_timer > 0:
            self.attack_timer -= dt

        # Simple AI: move toward player
        if self.alive:
            if self.state == "attack" and self.attack_timer <= 0:
                player.take_damage(self.damage)
                self.attack_timer = self.attack_cooldown
                if Enemy._attack_sound:
                    Enemy._attack_sound.play()

            dx = player.x - self.x
            dy = player.y - self.y
            distance = math.hypot(dx, dy)
            if distance > 10:
                self.x += (dx / distance) * self.speed * dt
                self.y += (dy / distance) * self.speed * dt

        self.update_animation(dt)

    def take_damage(self, amount):
        self.health -= amount
        self.state = "hurt"
        self.anim_index = 0.0
        if self.health <= 0:
            self.alive = False

    def draw(self, screen, player):
        """Draw enemy as pseudo-3D sprite relative to player"""
        dx = self.x - player.x
        dy = self.y - player.y
        distance = math.hypot(dx, dy)

        # Distance correction for fish-eye
        angle_to_player = math.atan2(dy, dx) - player.angle

        # Normalize angle to [-pi, pi]
        while angle_to_player > math.pi: angle_to_player -= 2 * math.pi
        while angle_to_player < -math.pi: angle_to_player += 2 * math.pi

        # Only draw if the enemy is in front of the player
        if abs(angle_to_player) > math.pi / 2:
            return

        # Simple projection
        proj_factor = DIST_TO_PROJ_PLANE

        try:
            tan_val = math.tan(angle_to_player)
            screen_x = (SCREEN_WIDTH // 2) + tan_val * proj_factor
        except (ValueError, OverflowError):
            return

        # Calculate sprite height using fish-eye corrected distance
        corrected_depth = distance * math.cos(angle_to_player)
        if corrected_depth < 0.1:  # Guard against division by near-zero
            corrected_depth = 0.1

        sprite_height = (25 / corrected_depth) * DIST_TO_PROJ_PLANE

        # Maintain aspect ratio
        orig_w, orig_h = self.current_sprite.get_size()
        aspect_ratio = orig_w / orig_h
        sprite_width = sprite_height * aspect_ratio

        # Guard against zero or astronomical sizes
        if sprite_width < 1 or sprite_height < 1:
            return
        if sprite_height > SCREEN_HEIGHT * 3:  # CAP huge sprites
            sprite_height = SCREEN_HEIGHT * 3
            sprite_width = sprite_height * aspect_ratio

        # Scale the sprite
        try:
            sprite_scaled = pygame.transform.scale(self.current_sprite, (int(sprite_width), int(sprite_height)))
        except (pygame.error, MemoryError, ValueError):
            return

        screen_y = SCREEN_HEIGHT // 2 - sprite_scaled.get_height() // 2

        # Blit with final safety coords check
        if -sprite_scaled.get_width() < screen_x < SCREEN_WIDTH + sprite_scaled.get_width():
            screen.blit(sprite_scaled, (screen_x - sprite_scaled.get_width() // 2, screen_y))