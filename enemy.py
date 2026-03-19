import pygame
import math
import os
import settings
from map import is_wall

def check_line_of_sight(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    dist = math.hypot(dx, dy)
    if dist < 1:
        return True

    steps = int(dist / (settings.TILE_SIZE / 4))
    if steps == 0:
        return True

    step_x = dx / steps
    step_y = dy / steps

    cx, cy = x1, y1
    for _ in range(steps):
        if is_wall(cx, cy):
            return False
        cx += step_x
        cy += step_y

    return True


class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 0.04
        self.health = 100
        self.alive = True
        self.damage = 10
        self.attack_cooldown = 2000  # ms
        self.attack_timer = 0
        self.slow_timer = 0
        self.slow_factor = 1.0
        self.hit_radius = 20

        self.frame_size = 64
        self.world_height = 25  # Default world height

        self.state = "idle"
        self.anim_index = 0.0
        self.anim_speed = 0.012
        self.current_sprite = None

    def _slice_sheet(self, sheet, frame_width=None):
        if frame_width is None:
            frame_width = self.frame_size
        sheet_w, sheet_h = sheet.get_size()
        frames = []
        for i in range(0, sheet_w, frame_width):
            width = min(frame_width, sheet_w - i)
            if width <= 0: break
            frames.append(sheet.subsurface((i, 0, width, sheet_h)))
        if not frames:
            fail = pygame.Surface((64, 64))
            fail.fill((255, 0, 255))
            return [fail]
        return frames

    def get_frames(self):
        return [self.current_sprite] if self.current_sprite else []

    def play_fly_sound(self):
        pass

    def play_attack_sound(self):
        pass

    def play_death_sound(self):
        pass

    def update_animation(self, dt):
        frames = self.get_frames()
        if not frames:
            return

        self.anim_index += self.anim_speed * dt

        if self.anim_index >= len(frames):
            if self.state == "die":
                self.anim_index = len(frames) - 1
            elif self.state == "hurt":
                self.anim_index = 0.0
                self.state = "idle"
            else:
                self.anim_index = 0.0
                if self.state in ("idle", "run"):
                    self.play_fly_sound()

        self.current_sprite = frames[int(self.anim_index)]

    @property
    def animation_finished(self):
        frames = self.get_frames()
        if not frames:
            return True
        return self.anim_index >= len(frames) - 1

    def update_state(self, player):
        if not self.alive:
            new_state = "die"
        elif self.state == "hurt" and not self.animation_finished:
            return
        else:
            dx = player.x - self.x
            dy = player.y - self.y
            distance_tiles = math.hypot(dx, dy) / settings.TILE_SIZE

            has_los = check_line_of_sight(self.x, self.y, player.x, player.y)

            if distance_tiles > 10 or not has_los:
                new_state = "idle"
            elif distance_tiles > 0.5:
                new_state = "run"
            else:
                new_state = "attack"

        if new_state != self.state:
            self.state = new_state
            self.anim_index = 0.0

    def update(self, player, dt):
        self.update_state(player)

        if self.attack_timer > 0:
            self.attack_timer -= dt

        if self.slow_timer > 0:
            self.slow_timer -= dt
            if self.slow_timer <= 0:
                self.slow_factor = 1.0

        if self.alive and self.state != "hurt":
            if self.state == "attack" and self.attack_timer <= 0:
                player.take_damage(self.damage)
                self.attack_timer = self.attack_cooldown
                self.play_attack_sound()

            dx = player.x - self.x
            dy = player.y - self.y
            distance = math.hypot(dx, dy)

            if distance > 10:
                current_speed = self.speed * self.slow_factor
                new_x = self.x + (dx / distance) * current_speed * dt
                new_y = self.y + (dy / distance) * current_speed * dt

                if not is_wall(new_x, self.y):
                    self.x = new_x
                if not is_wall(self.x, new_y):
                    self.y = new_y

        self.update_animation(dt)

    def take_damage(self, amount):
        if not self.alive:
            return

        self.health -= amount

        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.state = "die"
            self.anim_index = 0.0
            self.play_death_sound()
            return

        self.state = "hurt"
        self.anim_index = 0.0

    def apply_slow(self, factor, duration):
        self.slow_factor = factor
        self.slow_timer = duration

    def draw(self, screen, player, depth_buffer):
        if not self.current_sprite:
            return

        dx = self.x - player.x
        dy = self.y - player.y
        distance = math.hypot(dx, dy)

        angle_to_player = math.atan2(dy, dx) - player.angle

        while angle_to_player > math.pi:
            angle_to_player -= 2 * math.pi
        while angle_to_player < -math.pi:
            angle_to_player += 2 * math.pi

        if abs(angle_to_player) > math.pi / 2:
            return

        proj_factor = settings.DIST_TO_PROJ_PLANE

        try:
            tan_val = math.tan(angle_to_player)
            screen_x = (settings.SCREEN_WIDTH // 2) + tan_val * proj_factor
        except (ValueError, OverflowError):
            return

        corrected_depth = distance * math.cos(angle_to_player)
        if corrected_depth < 0.1:
            corrected_depth = 0.1

        sprite_height = (self.world_height / corrected_depth) * settings.DIST_TO_PROJ_PLANE

        orig_w, orig_h = self.current_sprite.get_size()
        aspect_ratio = orig_w / orig_h
        sprite_width = sprite_height * aspect_ratio

        if sprite_width < 1 or sprite_height < 1:
            return

        if sprite_height > settings.SCREEN_HEIGHT * 3:
            sprite_height = settings.SCREEN_HEIGHT * 3
            sprite_width = sprite_height * aspect_ratio

        half_width = sprite_width // 2
        y_offset_val = getattr(self, "y_offset", 0)
        proj_y = int(y_offset_val / corrected_depth * settings.DIST_TO_PROJ_PLANE)
        screen_y = settings.SCREEN_HEIGHT // 2 - sprite_height // 2 + proj_y

        step = orig_w / max(1.0, float(sprite_width))

        for i in range(int(sprite_width)):
            pixel_x = int(screen_x - half_width + i)

            if 0 <= pixel_x < settings.SCREEN_WIDTH:
                ray_idx = int(pixel_x // settings.SCALE)

                if 0 <= ray_idx < len(depth_buffer):
                    if corrected_depth < depth_buffer[ray_idx]:
                        tex_x = int(i * step)

                        if 0 <= tex_x < orig_w:
                            column = self.current_sprite.subsurface(
                                tex_x, 0, 1, orig_h
                            )
                            column_scaled = pygame.transform.scale(
                                column, (1, int(sprite_height))
                            )
                            screen.blit(column_scaled, (pixel_x, screen_y))


class Bat(Enemy):
    _animations_cache = {}
    _attack_sound = None
    _fly_sound = None

    def __init__(self, x, y):
        super().__init__(x, y)
        self.speed = 0.04
        self.health = 100
        self.damage = 10
        self.hit_radius = 20
        self.frame_size = 64

        if not Bat._animations_cache:
            Bat._animations_cache = {
                "idle": self._load_sheet("Bat-IdleFly.png"),
                "run": self._load_sheet("Bat-Run.png"),
                "attack": self._load_sheet("Bat-Attack1.png") + self._load_sheet("Bat-Attack2.png"),
                "hurt": self._load_sheet("Bat-Hurt.png"),
                "die": self._load_sheet("Bat-Die.png"),
            }

            try:
                bat_dir = os.path.join("assets", "textures", "enemy", "bat")
                att_path = os.path.join(bat_dir, "attack.wav")
                if os.path.exists(att_path):
                    Bat._attack_sound = pygame.mixer.Sound(att_path)

                fly_path = os.path.join(bat_dir, "fly.wav")
                if os.path.exists(fly_path):
                    Bat._fly_sound = pygame.mixer.Sound(fly_path)
                    Bat._fly_sound.set_volume(0.3)
            except:
                pass

        self.animations = Bat._animations_cache
        self.current_sprite = self.animations[self.state][0]

    def _load_sheet(self, filename):
        path = os.path.join("assets", "textures", "enemy", "bat", filename)
        try:
            sheet = pygame.image.load(path).convert_alpha()
            return self._slice_sheet(sheet, self.frame_size)
        except:
            fail = pygame.Surface((64, 64))
            fail.fill((255, 0, 255))
            return [fail]

    def get_frames(self):
        return self.animations.get(self.state, self.animations["idle"])

    def play_fly_sound(self):
        if Bat._fly_sound: Bat._fly_sound.play()

    def play_attack_sound(self):
        if Bat._attack_sound: Bat._attack_sound.play()


class Skeleton(Enemy):
    _animations_cache = {}

    def __init__(self, x, y):
        super().__init__(x, y)

        self.speed = 0.02
        self.health = 200
        self.damage = 15
        self.hit_radius = 30

        # Faster looks smoother
        self.anim_speed = 0.02

        # 🔥 Grounding fix (IMPORTANT)
        self.y_offset = 6   # try 6–10 range

        if not Skeleton._animations_cache:
            Skeleton._animations_cache = {
                "idle": self._load_sheet("Skeleton_01_White_Idle.png"),
                "run": self._load_sheet("Skeleton_01_White_Walk.png"),
                "attack": self._load_sheet("Skeleton_01_White_Attack1.png")
                          + self._load_sheet("Skeleton_01_White_Attack2.png"),
                "hurt": self._load_sheet("Skeleton_01_White_Hurt.png"),
                "die": self._load_sheet("Skeleton_01_White_Die.png"),
            }

            try:
                snd_dir = os.path.join("assets", "textures", "sounds", "enemy_sounds")
                att_path = os.path.join(snd_dir, "slime_and_skelet_attack.wav")
                if os.path.exists(att_path):
                    Skeleton._attack_sound = pygame.mixer.Sound(att_path)
                    Skeleton._attack_sound.set_volume(0.5)

                die_path = os.path.join(snd_dir, "bones_snap.mp3")
                if os.path.exists(die_path):
                    Skeleton._death_sound = pygame.mixer.Sound(die_path)
                    Skeleton._death_sound.set_volume(0.6)
            except:
                pass

        self.animations = Skeleton._animations_cache
        self.current_sprite = self.animations[self.state][0]

    _attack_sound = None
    _death_sound = None

    def play_attack_sound(self):
        if Skeleton._attack_sound:
            Skeleton._attack_sound.play()

    def play_death_sound(self):
        if Skeleton._death_sound:
            Skeleton._death_sound.play()

    def _load_sheet(self, filename):
        path = os.path.join(
            "assets",
            "textures",
            "enemy",
            "Skeletons_Free_Pack",
            "Skeletons_Free_Pack",
            "Skeleton_Sword",
            "Skeleton_White",
            "Skeleton_Without_VFX",
            filename
        )

        try:
            sheet = pygame.image.load(path).convert_alpha()
        except Exception as e:
            print(f"Error loading skeleton sheet {path}: {e}")
            fail = pygame.Surface((64, 64), pygame.SRCALPHA)
            fail.fill((255, 0, 255))
            return [fail]

        frames = self._slice_sheet(sheet)
        return self._normalize_frames(frames)

    def _slice_sheet(self, sheet):
        sheet_width = sheet.get_width()
        sheet_height = sheet.get_height()

        frame_width = sheet_height

        if frame_width <= 0:
            return [sheet]

        frame_count = sheet_width // frame_width

        if frame_count <= 0:
            return [sheet]

        frames = []
        for i in range(frame_count):
            x = i * frame_width
            if x + frame_width <= sheet_width:
                frame = sheet.subsurface((x, 0, frame_width, sheet_height)).copy()
                frames.append(frame)

        return frames if frames else [sheet]



    def _normalize_frames(self, frames):
        """
        Stabilized version:
        - trims transparency
        - bottom-aligns (feet fixed)
        - reduces sideways jitter
        """
        trimmed_frames = []

        for frame in frames:
            bounds = frame.get_bounding_rect()

            if bounds.width == 0 or bounds.height == 0:
                trimmed = pygame.Surface((1, 1), pygame.SRCALPHA)
            else:
                trimmed = frame.subsurface(bounds).copy()

            trimmed_frames.append(trimmed)

        max_w = max(frame.get_width() for frame in trimmed_frames)
        max_h = max(frame.get_height() for frame in trimmed_frames)

        normalized = []

        for i, frame in enumerate(trimmed_frames):
            surface = pygame.Surface((max_w, max_h), pygame.SRCALPHA)

            # 🔥 MUCH smoother offsets (less aggressive)
            offset_x = 0
            offset_y = 0

            if i in [1]:
                offset_x = -1
            elif i in [2]:
                offset_x = -1
            elif i in [3]:
                offset_x = +1
            elif i in [4]:
                offset_x = +1

            # 🔥 tiny vertical correction (prevents foot jitter)
            if i in [2, 3]:
                offset_y = 1

            x = (max_w - frame.get_width()) // 2 + offset_x
            y = max_h - frame.get_height() + offset_y

            surface.blit(frame, (x, y))
            normalized.append(surface)

        return normalized

    def get_frames(self):
        return self.animations.get(self.state, self.animations["idle"])

    def update_animation(self, dt):
        frames = self.get_frames()
        self.anim_index += self.anim_speed * dt

        if self.anim_index >= len(frames):
            if self.state == "die":
                self.anim_index = len(frames) - 1
            elif self.state == "hurt":
                self.anim_index = 0.0
                self.state = "idle"
            else:
                self.anim_index = 0.0

        self.current_sprite = frames[int(self.anim_index)]


class Slime(Enemy):
    _animations_cache = {}

    def __init__(self, x, y):
        super().__init__(x, y)

        self.speed = 0.015
        self.health = 50
        self.damage = 5
        self.hit_radius = 25

        # Slower animation feels more "squishy"
        self.anim_speed = 0.006

        # 🔥 IMPORTANT: push slime down so it touches ground
        self.y_offset = 24   # lowered further to make it touch the ground

        if not Slime._animations_cache:
            Slime._animations_cache = {
                "idle": self._load_individual("idle", 4),
                "run": self._load_individual("move", 4),
                "attack": self._load_individual("attack", 5),
                "hurt": self._load_individual("hurt", 4),
                "die": self._load_individual("die", 4),
            }

            try:
                snd_dir = os.path.join("assets", "textures", "sounds", "enemy_sounds")
                att_path = os.path.join(snd_dir, "slime_and_skelet_attack.wav")
                if os.path.exists(att_path):
                    Slime._attack_sound = pygame.mixer.Sound(att_path)
                    Slime._attack_sound.set_volume(0.4)

                die_path = os.path.join(snd_dir, "slime_splat.mp3")
                if os.path.exists(die_path):
                    Slime._death_sound = pygame.mixer.Sound(die_path)
                    Slime._death_sound.set_volume(0.6)
            except:
                pass

        self.animations = Slime._animations_cache
        self.current_sprite = self.animations[self.state][0]

    _attack_sound = None
    _death_sound = None

    def play_attack_sound(self):
        if Slime._attack_sound:
            Slime._attack_sound.play()

    def play_death_sound(self):
        if Slime._death_sound:
            Slime._death_sound.play()

    def _load_individual(self, prefix, count):
        frames = []

        for i in range(count):
            path = os.path.join(
                "assets",
                "textures",
                "enemy",
                "Slime",
                "Individual Sprites",
                f"slime-{prefix}-{i}.png"
            )

            try:
                frame = pygame.image.load(path).convert_alpha()
                frames.append(frame)

            except Exception as e:
                print(f"Error loading slime frame {path}: {e}")
                fail = pygame.Surface((64, 64), pygame.SRCALPHA)
                fail.fill((255, 0, 255))
                frames.append(fail)

        return frames if frames else [pygame.Surface((64, 64))]

    def get_frames(self):
        return self.animations.get(self.state, self.animations["idle"])


class Wolf(Enemy):
    _animations_cache = {}

    def __init__(self, x, y):
        super().__init__(x, y)
        self.speed = 0.03
        self.health = 150
        self.damage = 12
        self.hit_radius = 26
        self.anim_speed = 0.015
        self.y_offset = 20  # Keep it grounded

        if not Wolf._animations_cache:
            Wolf._animations_cache = {
                "idle": self._load_sheet("wolf_idle.png", 8),
                "run": self._load_sheet("wolf_run.png", 3),
                "attack": self._load_sheet("wolf_run.png", 3), # Reuse run for attack
                "hurt": self._load_sheet("wolf_idle.png", 8), # Reuse idle
                "die": self._load_sheet("wolf_idle.png", 8),  # Reuse idle
            }

        self.animations = Wolf._animations_cache
        self.current_sprite = self.animations[self.state][0]

        if not Wolf._attack_sound:
            try:
                snd_dir = os.path.join("assets", "textures", "sounds", "enemy_sounds")
                att_path = os.path.join(snd_dir, "wolf-attack.wav")
                if os.path.exists(att_path):
                    Wolf._attack_sound = pygame.mixer.Sound(att_path)
                    Wolf._attack_sound.set_volume(0.5)

                die_path = os.path.join(snd_dir, "wolf-howling.wav")
                if os.path.exists(die_path):
                    Wolf._death_sound = pygame.mixer.Sound(die_path)
                    Wolf._death_sound.set_volume(0.6)
            except Exception as e:
                print(f"Error loading wolf sounds: {e}")

    _attack_sound = None
    _death_sound = None

    def play_attack_sound(self):
        if Wolf._attack_sound:
            Wolf._attack_sound.play()

    def play_death_sound(self):
        if Wolf._death_sound:
            Wolf._death_sound.play()

    def _load_sheet(self, filename, frame_count):
        path = os.path.join("assets", "textures", "enemy", "Wolf", filename)
        try:
            sheet = pygame.image.load(path).convert_alpha()
            sheet_w, sheet_h = sheet.get_size()
            frame_width = sheet_w // frame_count
            frames = []
            for i in range(frame_count):
                frame = sheet.subsurface((i * frame_width, 0, frame_width, sheet_h))
                # Scale up slightly for better visibility
                frame = pygame.transform.scale(frame, (frame_width * 2, sheet_h * 2))
                frames.append(frame)
            return frames
        except Exception as e:
            print(f"Error loading wolf sheet {path}: {e}")
            fail = pygame.Surface((64, 64))
            fail.fill((255, 0, 255))
            return [fail]

    def get_frames(self):
        return self.animations.get(self.state, self.animations["idle"])


class Necromancer(Enemy):
    _animations_cache = {}
    _attack_sound = None
    _death_sound = None

    def __init__(self, x, y):
        super().__init__(x, y)

        # --- Boss stats ---
        self.speed = 0.02
        self.health = 2000
        self.damage = 25

        # --- Scaling ---
        self.scale = 2.0

        # --- Collision / visuals (scaled accordingly) ---
        self.hit_radius = int(35 * self.scale)
        self.world_height = 150 # int(25 * self.scale)
        self.y_offset = int(12 * self.scale)

        # --- Animation ---
        self.anim_speed = 0.015

        if not Necromancer._animations_cache:
            sheet_path = os.path.join(
                'assets', 'textures', 'enemy', 'boss',
                'Necromancer_creativekind-Sheet.png'
            )
            sheet = pygame.image.load(sheet_path).convert_alpha()

            # Row mapping:
            # 0: Idle, 1: Run, 2: Attack, 3: Hurt, 4: Die
            Necromancer._animations_cache['idle'] = self._load_frames(sheet, 0, 8, 160, 128)
            Necromancer._animations_cache['run'] = self._load_frames(sheet, 1, 8, 160, 128)
            Necromancer._animations_cache['attack'] = self._load_frames(sheet, 2, 13, 160, 128)
            Necromancer._animations_cache['hurt'] = self._load_frames(sheet, 3, 13, 160, 128)
            Necromancer._animations_cache['die'] = self._load_frames(sheet, 4, 17, 160, 128)

            try:
                snd_dir = os.path.join("assets", "textures", "sounds", "enemy_sounds")
                att_path = os.path.join(snd_dir, "swoosh.mp3")
                if os.path.exists(att_path):
                    Necromancer._attack_sound = pygame.mixer.Sound(att_path)
                
                die_path = os.path.join(snd_dir, "necro_over.wav")
                if os.path.exists(die_path):
                    Necromancer._death_sound = pygame.mixer.Sound(die_path)
            except:
                pass

        self.animations = Necromancer._animations_cache
        self.current_sprite = self.animations[self.state][0]

    def _load_frames(self, sheet, row_idx, count, frame_w, frame_h):
        frames = []

        for i in range(count):
            rect = (i * frame_w, row_idx * frame_h, frame_w, frame_h)
            frame = sheet.subsurface(rect).copy()

            # 🔥 Proper scalable resizing
            scaled_w = int(frame_w * self.scale)
            scaled_h = int(frame_h * self.scale)

            frame = pygame.transform.smoothscale(frame, (scaled_w, scaled_h))
            frames.append(frame)

        return frames

    def get_frames(self):
        return self.animations.get(self.state, self.animations["idle"])

    def play_attack_sound(self):
        if Necromancer._attack_sound:
            Necromancer._attack_sound.play()

    def play_death_sound(self):
        if Necromancer._death_sound:
            Necromancer._death_sound.play()