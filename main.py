import math
import os
import queue
import random
import subprocess
import sys
import threading
import importlib.util
from time import time as get_time

import pygame

from background import draw_background
from controls import CONTROLS
from enemy import Bat, Skeleton, Slime, Wolf, Necromancer
from explosion import Explosion
from hud import draw_hud, load_hud, get_fullscreen_button_rect
from map import get_free_pos, game_map, TILE_SIZE, is_wall
from player import Player
from raycasting import ray_casting
from settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
    FULLSCREEN,
    PLAYER_ANGLE,
    PLAYER_SPEED,
    PLAYER_ROT_SPEED,
    WALL_TEXTURE_PATH,
    SKY_TEXTURE_PATH,
    GRASS_TEXTURE_PATH,
    POSTER_TEXTURE_PATH,
    HEXSTORM_TEXTURE_PATH,
)
from sprite import Sprite, render_sprites
from staff import Staff
from weapon import Weapon

def ensure_dependencies():
    """Check and install required dependencies automatically."""
    missing_deps = []

    if importlib.util.find_spec("pygame") is None:
        missing_deps.append("pygame")

    if missing_deps:
        print("HEXSTORM - Installing missing dependencies...")

        for dep in missing_deps:
            print(f"Installing {dep}...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
                print(f"✓ {dep} installed successfully")
            except subprocess.CalledProcessError:
                print(f"✗ Failed to install {dep}")
                print("Please install manually: pip install pygame")
                sys.exit(1)

        print("Dependencies installed! Restarting game...")
        os.execv(sys.executable, [sys.executable] + sys.argv)

    return True

ensure_dependencies()

STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_GAME_OVER = "game_over"

GAME_MODE_NORMAL = "normal"
GAME_MODE_HARDCORE = "hardcore"  # No minimap or enemy indicator

DIFFICULTY_EASY = "easy"
DIFFICULTY_MEDIUM = "medium"
DIFFICULTY_HARD = "hard"

DIFFICULTY_SETTINGS = {
    DIFFICULTY_EASY: {
        "health": 500,
        "max_mana": 5000,
        "mana_regen_rate": 75,
    },
    DIFFICULTY_MEDIUM: {
        "health": 100,
        "max_mana": 2000,
        "mana_regen_rate": 50,
    },
    DIFFICULTY_HARD: {
        "health": 50,
        "max_mana": 1000,
        "mana_regen_rate": 37.5,
    },
}

def load_textures():
    wall_texture = pygame.image.load(WALL_TEXTURE_PATH).convert()
    poster_texture = pygame.image.load(POSTER_TEXTURE_PATH).convert()
    hexstorm_texture = pygame.image.load(HEXSTORM_TEXTURE_PATH).convert()
    sky_texture = pygame.image.load(SKY_TEXTURE_PATH).convert()
    grass_texture = pygame.image.load(GRASS_TEXTURE_PATH).convert()

    textures = {
        1: wall_texture,
        2: poster_texture,
        3: hexstorm_texture,
    }

    return textures, sky_texture, grass_texture

def load_menu_background():
    menu_path = os.path.join("assets", "textures", "menu.png")
    image = pygame.image.load(menu_path).convert()
    return pygame.transform.scale(image, (SCREEN_WIDTH, SCREEN_HEIGHT))

def create_decor_sprites(amount=30, used_tiles=None):
    if used_tiles is None:
        used_tiles = set()

    sprites = []
    textures = []

    try:
        plant_tex = pygame.image.load("assets/textures/sprites/plant_fern.png").convert_alpha()
        plant_tex = plant_tex.subsurface((253, 232, 502, 512)).copy()
        textures.append(plant_tex)
    except Exception as e:
        print("Could not load plant_fern.png", e)

    try:
        bones_tex = pygame.image.load("assets/textures/sprites/bones.png").convert_alpha()
        textures.append(bones_tex)
    except Exception as e:
        print("Could not load bones.png", e)

    try:
        pillar_tex = pygame.image.load(
            "assets/textures/sprites/1be9878e-3402-47ee-8f09-652e9bf05780.png"
        ).convert_alpha()
        textures.append(pillar_tex)
    except Exception as e:
        print("Could not load pillar texture", e)

    if not textures:
        fallback = pygame.Surface((64, 64))
        fallback.fill((0, 255, 0))
        textures.append(fallback)

    for _ in range(amount):
        while True:
            sx = random.randint(1, len(game_map[0]) - 2)
            sy = random.randint(1, len(game_map) - 2)

            if game_map[sy][sx] == 0 and (sx, sy) not in used_tiles:
                used_tiles.add((sx, sy))
                sprite_x = sx * TILE_SIZE + TILE_SIZE // 2
                sprite_y = sy * TILE_SIZE + TILE_SIZE // 2
                tex = random.choice(textures)
                sprites.append(Sprite(sprite_x, sprite_y, tex))
                break

    return sprites

def create_enemies(player=None, amount=8, used_tiles=None, wave=1):
    if used_tiles is None:
        used_tiles = set()

    enemies = []
    num_necromancers = 0

    if wave > 4:
        num_necromancers = 2
        amount = max(0, amount - 2)

    for _ in range(amount):
        while True:
            sx = random.randint(1, len(game_map[0]) - 2)
            sy = random.randint(1, len(game_map) - 2)

            if game_map[sy][sx] == 0 and (sx, sy) not in used_tiles:
                enemy_x = sx * TILE_SIZE + TILE_SIZE // 2
                enemy_y = sy * TILE_SIZE + TILE_SIZE // 2

                if player:
                    dx = enemy_x - player.x
                    dy = enemy_y - player.y
                    dist = math.hypot(dx, dy)
                    if dist < 200 or dist > 1000:
                        continue

                used_tiles.add((sx, sy))
                enemy_types = [Bat, Skeleton, Slime, Wolf]
                enemies.append(random.choice(enemy_types)(enemy_x, enemy_y))
                break

    for _ in range(num_necromancers):
        while True:
            sx = random.randint(1, len(game_map[0]) - 2)
            sy = random.randint(1, len(game_map) - 2)

            if game_map[sy][sx] == 0 and (sx, sy) not in used_tiles:
                enemy_x = sx * TILE_SIZE + TILE_SIZE // 2
                enemy_y = sy * TILE_SIZE + TILE_SIZE // 2

                if player:
                    dx = enemy_x - player.x
                    dy = enemy_y - player.y
                    dist = math.hypot(dx, dy)
                    if dist < 400 or dist > 1200:
                        continue

                used_tiles.add((sx, sy))
                enemies.append(Necromancer(enemy_x, enemy_y))
                break

    return enemies

def draw_game_over(screen):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    font_big = pygame.font.SysFont("Arial", 80, bold=True)
    font_small = pygame.font.SysFont("Arial", 28)

    game_over_text = font_big.render("GAME OVER", True, (255, 50, 50))
    restart_text = font_small.render("Press R to restart", True, (255, 255, 255))

    game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
    restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))

    screen.blit(game_over_text, game_over_rect)
    screen.blit(restart_text, restart_rect)

def draw_menu(screen, background, selected_option, menu_options, menu_level="main", selected_difficulty_option=1):
    screen.blit(background, (0, 0))

    title_font = pygame.font.SysFont("Times New Roman", 84, bold=True)
    option_font = pygame.font.SysFont("Arial", 42, bold=True)
    small_font = pygame.font.SysFont("Arial", 24)

    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 70))
    screen.blit(overlay, (0, 0))

    title_text = title_font.render("HEXSTORM", True, (255, 230, 180))
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 140))
    screen.blit(title_text, title_rect)

    if menu_level == "main":
        start_y = SCREEN_HEIGHT // 2 + 30
        spacing = 80

        for i, option in enumerate(menu_options):
            color = (255, 210, 100) if i == selected_option else (230, 230, 230)
            text = option_font.render(option, True, color)
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, start_y + i * spacing))
            screen.blit(text, rect)

        hint_text = small_font.render("Use UP / DOWN and ENTER", True, (220, 220, 220))
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60))
        screen.blit(hint_text, hint_rect)

    elif menu_level == "difficulty":
        difficulty_options = ["EASY", "MEDIUM", "HARD"]
        difficulty_descriptions = [
            "500 HP, 5000 Mana, 1.5x Regen",
            "100 HP, 2000 Mana, Normal Regen",
            "50 HP, 1000 Mana, 0.75x Regen",
        ]

        start_y = SCREEN_HEIGHT // 2 - 50
        spacing = 60

        diff_title = option_font.render("SELECT DIFFICULTY", True, (255, 255, 255))
        diff_title_rect = diff_title.get_rect(center=(SCREEN_WIDTH // 2, start_y - 80))
        screen.blit(diff_title, diff_title_rect)

        for i, (option, description) in enumerate(zip(difficulty_options, difficulty_descriptions)):
            if i == selected_difficulty_option:
                color = (255, 210, 100)
                box_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, start_y + i * spacing - 10, 400, 50)
                pygame.draw.rect(screen, color, box_rect, 2)
            else:
                color = (230, 230, 230)

            text = option_font.render(option, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, start_y + i * spacing))
            screen.blit(text, text_rect)

            desc_text = small_font.render(description, True, color)
            desc_rect = desc_text.get_rect(center=(SCREEN_WIDTH // 2, start_y + i * spacing + 25))
            screen.blit(desc_text, desc_rect)

        hint_text = small_font.render(
            "Use UP / DOWN to select, ENTER to confirm, ESC to go back",
            True,
            (220, 220, 220),
        )
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60))
        screen.blit(hint_text, hint_rect)

def draw_controls_rebinding(
    screen,
    background,
    selected_control_index=0,
    rebinding_active=False,
    rebinding_control=None,
):
    screen.blit(background, (0, 0))

    title_font = pygame.font.Font(None, 48)
    option_font = pygame.font.Font(None, 32)
    small_font = pygame.font.Font(None, 24)

    title_text = title_font.render("REBIND CONTROLS", True, (255, 255, 255))
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
    screen.blit(title_text, title_rect)

    controls_list = [
        ("Move Forward", "move_forward"),
        ("Move Backward", "move_backward"),
        ("Move Left", "move_left"),
        ("Move Right", "move_right"),
        ("Turn Left", "turn_left"),
        ("Turn Right", "turn_right"),
        ("Shoot Gun", "shoot"),
    ]

    start_y = 200
    spacing = 50

    for i, (display_name, control_key) in enumerate(controls_list):
        if i == selected_control_index:
            color = (255, 210, 100)
            box_rect = pygame.Rect(SCREEN_WIDTH // 2 - 250, start_y + i * spacing - 10, 500, 45)
            pygame.draw.rect(screen, color, box_rect, 2)
        else:
            color = (230, 230, 230)

        current_key = CONTROLS[control_key]
        key_name = pygame.key.name(current_key).upper() if current_key else "NONE"

        text = option_font.render(f"{display_name}: {key_name}", True, color)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, start_y + i * spacing))
        screen.blit(text, text_rect)

    if rebinding_active:
        instruction_text = small_font.render(
            f"Press new key for {rebinding_control[0] if rebinding_control else 'selected control'} (ESC to cancel)",
            True,
            (255, 255, 100),
        )
    else:
        instruction_text = small_font.render(
            "Use UP/DOWN to select, ENTER to rebind, ESC to go back",
            True,
            (220, 220, 220),
        )

    instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
    screen.blit(instruction_text, instruction_rect)

def reset_game(game_mode=GAME_MODE_NORMAL, difficulty=DIFFICULTY_MEDIUM):
    start_x, start_y = get_free_pos()
    diff_settings = DIFFICULTY_SETTINGS[difficulty]

    player = Player(
        start_x,
        start_y,
        PLAYER_ANGLE,
        PLAYER_SPEED,
        PLAYER_ROT_SPEED,
        diff_settings["health"],
        diff_settings["max_mana"],
        diff_settings["mana_regen_rate"],
    )

    used_tiles = set()
    sprites = create_decor_sprites(30, used_tiles=used_tiles)
    wave = 1
    enemies = create_enemies(player, 8, used_tiles=used_tiles, wave=wave)
    explosions = []
    weapon = Weapon()
    staff = Staff()
    projectiles = []
    kills = 0

    return (
        player,
        sprites,
        enemies,
        explosions,
        weapon,
        staff,
        projectiles,
        wave,
        kills,
        game_mode,
        difficulty,
    )

def toggle_fullscreen(screen):
    if screen.get_flags() & pygame.FULLSCREEN:
        return pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SCALED)
    return pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SCALED | pygame.FULLSCREEN)

def read_webcam_output(process, q):
    """Reads stdout from the webcam subprocess and puts results in a queue."""
    try:
        for line in iter(process.stdout.readline, ""):
            decoded_line = line.strip()

            if "+++ GAME_RESULT:" in decoded_line:
                spell_name = decoded_line.split("+++ GAME_RESULT:")[1].split("+++")[0].strip()
                q.put(spell_name)
            elif decoded_line.startswith("ERROR:"):
                print(f"WEBCAM ERROR: {decoded_line}")
            elif (
                decoded_line.startswith("AI DETECTION:")
                or decoded_line.startswith("Detected")
                or "Confidence dropped" in decoded_line
            ):
                print(f"WEBCAM: {decoded_line}")
    except Exception as e:
        print(f"DEBUG: Webcam reader error: {e}")
    finally:
        process.stdout.close()

def main():
    pygame.init()

    soundtrack_path = os.path.join("assets", "textures", "sounds", "soundtrack.wav")
    no_mercy_path = os.path.join("assets", "textures", "sounds", "no-mercy.wav")

    try:
        if os.path.exists(soundtrack_path):
            pygame.mixer.music.load(soundtrack_path)
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(-1)
        else:
            print(f"DEBUG: Soundtrack NOT FOUND at {soundtrack_path}")
    except Exception as e:
        print(f"DEBUG: Could not load soundtrack: {e}")

    no_mercy_sound = None
    game_over_sound = None

    try:
        if os.path.exists(no_mercy_path):
            no_mercy_sound = pygame.mixer.Sound(no_mercy_path)
            no_mercy_sound.set_volume(0.65)

        game_over_path = os.path.join("assets", "textures", "sounds", "player_game_over.mp3")
        if os.path.exists(game_over_path):
            game_over_sound = pygame.mixer.Sound(game_over_path)
            game_over_sound.set_volume(0.8)
    except Exception as e:
        print(f"DEBUG: Sound loading failed: {e}")

    flags = pygame.SCALED
    if FULLSCREEN:
        flags |= pygame.FULLSCREEN

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
    pygame.display.set_caption("HEXSTORM - Raycasting Prototype")
    clock = pygame.time.Clock()

    hud_image = load_hud()
    textures, sky_texture, grass_texture = load_textures()
    menu_background = load_menu_background()

    (
        player,
        sprites,
        enemies,
        explosions,
        weapon,
        staff,
        projectiles,
        wave,
        kills,
        game_mode,
        difficulty,
    ) = reset_game()

    game_state = STATE_MENU
    menu_level = "main"
    selected_main_option = 0
    selected_difficulty_option = 1
    selected_control_index = 0
    rebinding_active = False
    rebinding_control = None
    main_options = ["PLAY", "HARDCORE", "REBIND CONTROLS", "QUIT"]
    difficulty_options = ["EASY", "MEDIUM", "HARD"]
    selected_option = 0

    running = True

    webcam_process = None
    webcam_queue = queue.Queue()

    try:
        venv311_python = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            ".venv311",
            "Scripts",
            "python.exe",
        )
        webcam_python = venv311_python if os.path.exists(venv311_python) else sys.executable
        print(f"DEBUG: Using Python for webcam: {webcam_python}")

        webcam_process = subprocess.Popen(
            [webcam_python, "webcam_classifier.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            cwd=os.path.dirname(os.path.abspath(__file__)),
        )

        webcam_thread = threading.Thread(
            target=read_webcam_output,
            args=(webcam_process, webcam_queue),
            daemon=True,
        )
        webcam_thread.start()
        print("DEBUG: Webcam subprocess started.")
    except Exception as e:
        print(f"DEBUG: Could not start webcam subprocess: {e}")

    while running:
        dt = clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and game_state == STATE_PLAYING:
                    if get_fullscreen_button_rect().collidepoint(event.pos):
                        screen = toggle_fullscreen(screen)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    screen = toggle_fullscreen(screen)

                elif game_state == STATE_MENU:
                    if menu_level == "main":
                        if event.key == pygame.K_UP:
                            selected_main_option = (selected_main_option - 1) % len(main_options)
                            selected_option = selected_main_option

                        elif event.key == pygame.K_DOWN:
                            selected_main_option = (selected_main_option + 1) % len(main_options)
                            selected_option = selected_main_option

                        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                            choice = main_options[selected_main_option]

                            if choice in ("PLAY", "HARDCORE"):
                                menu_level = "difficulty"
                                selected_option = selected_difficulty_option

                            elif choice == "REBIND CONTROLS":
                                menu_level = "rebinding"
                                selected_control_index = 0
                                rebinding_active = False
                                rebinding_control = None

                            elif choice == "QUIT":
                                running = False

                    elif menu_level == "rebinding":
                        controls_list = [
                            ("Move Forward", "move_forward"),
                            ("Move Backward", "move_backward"),
                            ("Move Left", "move_left"),
                            ("Move Right", "move_right"),
                            ("Turn Left", "turn_left"),
                            ("Turn Right", "turn_right"),
                            ("Shoot Gun", "shoot"),
                        ]

                        if rebinding_active:
                            if event.key != pygame.K_ESCAPE:
                                if selected_control_index < len(controls_list):
                                    control_name, control_key = controls_list[selected_control_index]
                                    CONTROLS[control_key] = event.key
                                    print(f"Rebound {control_name} to {pygame.key.name(event.key).upper()}")
                                    print(
                                        f"DEBUG: CONTROLS['{control_key}'] is now "
                                        f"{pygame.key.name(CONTROLS[control_key])}"
                                    )
                                rebinding_active = False
                                rebinding_control = None
                        else:
                            if event.key == pygame.K_UP:
                                selected_control_index = (selected_control_index - 1) % len(controls_list)
                            elif event.key == pygame.K_DOWN:
                                selected_control_index = (selected_control_index + 1) % len(controls_list)
                            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                                if selected_control_index < len(controls_list):
                                    rebinding_active = True
                                    rebinding_control = controls_list[selected_control_index]
                            elif event.key == pygame.K_ESCAPE:
                                menu_level = "main"
                                selected_option = selected_main_option

                    elif menu_level == "difficulty":
                        if event.key == pygame.K_UP:
                            selected_difficulty_option = (
                                selected_difficulty_option - 1
                            ) % len(difficulty_options)
                            selected_option = selected_difficulty_option

                        elif event.key == pygame.K_DOWN:
                            selected_difficulty_option = (
                                selected_difficulty_option + 1
                            ) % len(difficulty_options)
                            selected_option = selected_difficulty_option

                        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                            difficulty_name = difficulty_options[selected_difficulty_option]
                            difficulty_map = {
                                "EASY": DIFFICULTY_EASY,
                                "MEDIUM": DIFFICULTY_MEDIUM,
                                "HARD": DIFFICULTY_HARD,
                            }
                            selected_difficulty = difficulty_map[difficulty_name]

                            game_mode = (
                                GAME_MODE_NORMAL
                                if selected_main_option == 0
                                else GAME_MODE_HARDCORE
                            )

                            (
                                player,
                                sprites,
                                enemies,
                                explosions,
                                weapon,
                                staff,
                                projectiles,
                                wave,
                                kills,
                                game_mode,
                                difficulty,
                            ) = reset_game(game_mode, selected_difficulty)

                            game_state = STATE_PLAYING

                            if no_mercy_sound:
                                no_mercy_sound.play()

                        elif event.key == pygame.K_ESCAPE:
                            menu_level = "main"
                            selected_option = selected_main_option

                elif game_state == STATE_PLAYING:
                    pass

        if game_state == STATE_PLAYING:
            try:
                while not webcam_queue.empty():
                    spell_detected = webcam_queue.get_nowait()
                    print(f"DEBUG: Webcam triggered: {spell_detected}")

                    if spell_detected == "Ice shards":
                        staff.current_spell = "Ice shards"
                        mana_cost = staff.get_mana_cost()
                        if player.mana >= mana_cost:
                            player.mana -= mana_cost
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
                            staff.spawn_data = (spawn_x, spawn_y, player.angle)
                            projectile = staff._spawn_projectile(player)
                            if projectile:
                                projectiles.append(projectile)

                    elif spell_detected == "Inferno burst":
                        staff.current_spell = "Inferno burst"
                        mana_cost = staff.get_mana_cost()
                        if player.mana >= mana_cost:
                            player.mana -= mana_cost
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
                            staff.spawn_data = (spawn_x, spawn_y, player.angle)
                            projectile = staff._spawn_projectile(player)
                            if projectile:
                                projectiles.append(projectile)

                    elif spell_detected == "Healing touch":
                        staff.current_spell = "Healing touch"
                        mana_cost = staff.get_mana_cost()
                        if player.mana >= mana_cost:
                            player.mana -= mana_cost
                            player.health = (
                                player.max_health
                                if hasattr(player, "max_health")
                                else DIFFICULTY_SETTINGS[difficulty]["health"]
                            )
                            player.heal_time = get_time()
                            print("Healing touch: Restored to full health!")

                    elif spell_detected == "Void bulwark":
                        staff.current_spell = "Void bulwark"
                        mana_cost = staff.get_mana_cost()
                        if player.mana >= mana_cost:
                            player.mana -= mana_cost
                            player.damage_reduction = 1.0
                            player.damage_reduction_end_time = get_time() + 7.5
                            print("Void bulwark: Immune to damage for 7.5 seconds")

                    elif spell_detected == "Arcane bulwark":
                        staff.current_spell = "Arcane bulwark"
                        mana_cost = staff.get_mana_cost()
                        if player.mana >= mana_cost:
                            player.mana -= mana_cost
                            player.damage_reduction = 0.5
                            player.damage_reduction_end_time = get_time() + 5.0
                            print("Arcane bulwark: 50% damage reduction for 5 seconds")
            except queue.Empty:
                pass

        if game_state == STATE_PLAYING:
            for explosion in explosions:
                explosion.update(dt)
            explosions = [e for e in explosions if e.alive]

            player.movement()
            player.update(get_time())
            player.regenerate_mana(dt)
            weapon.update(dt, player, enemies)

            new_projectile = staff.update(dt, player)
            if new_projectile:
                projectiles.append(new_projectile)

            for projectile in projectiles:
                projectile.update(dt)

                if is_wall(projectile.x, projectile.y):
                    if hasattr(projectile, "aoe_radius"):
                        explosions.append(Explosion(projectile.x, projectile.y))
                    projectile.alive = False

            for enemy in enemies:
                enemy.update(player, dt)

            for projectile in projectiles:
                if not projectile.alive:
                    continue

                for enemy in enemies:
                    if not enemy.alive:
                        continue

                    dx = enemy.x - projectile.x
                    dy = enemy.y - projectile.y
                    distance = math.hypot(dx, dy)

                    if distance < (projectile.hit_radius + enemy.hit_radius):
                        if hasattr(projectile, "aoe_radius"):
                            explosions.append(Explosion(projectile.x, projectile.y))

                            for splash_enemy in enemies:
                                if not splash_enemy.alive:
                                    continue

                                s_dx = splash_enemy.x - projectile.x
                                s_dy = splash_enemy.y - projectile.y
                                s_dist = math.hypot(s_dx, s_dy)

                                if s_dist < projectile.aoe_radius:
                                    splash_enemy.take_damage(projectile.damage)
                        else:
                            enemy.take_damage(projectile.damage)

                            if hasattr(projectile, "slow_factor"):
                                enemy.apply_slow(
                                    projectile.slow_factor,
                                    projectile.slow_duration,
                                )

                        projectile.alive = False
                        break

            projectiles = [projectile for projectile in projectiles if projectile.alive]

            dead_enemies = [enemy for enemy in enemies if not enemy.alive and enemy.animation_finished]
            kills += len(dead_enemies)

            enemies = [enemy for enemy in enemies if enemy.alive or not enemy.animation_finished]
            alive_count = sum(1 for e in enemies if e.alive)

            if alive_count == 0:
                wave += 1
                enemies.extend(create_enemies(player, 5 + wave * 2, wave=wave))

            if player.health <= 0:
                if game_state != STATE_GAME_OVER:
                    game_state = STATE_GAME_OVER
                    if game_over_sound:
                        game_over_sound.play()

        if game_state == STATE_MENU:
            if menu_level == "rebinding":
                draw_controls_rebinding(
                    screen,
                    menu_background,
                    selected_control_index,
                    rebinding_active,
                    rebinding_control,
                )
            else:
                draw_menu(
                    screen,
                    menu_background,
                    selected_option,
                    main_options,
                    menu_level,
                    selected_difficulty_option,
                )

        elif game_state == STATE_PLAYING:
            draw_background(screen, sky_texture, grass_texture, player)

            depth_buffer = ray_casting(screen, player, textures)
            render_sprites(screen, player, sprites + projectiles, depth_buffer)

            for explosion in explosions:
                explosion.draw(screen, player, depth_buffer)

            for enemy in enemies:
                enemy.draw(screen, player, depth_buffer)

            weapon.draw(screen)
            staff.draw(screen)
            draw_hud(
                screen,
                player,
                hud_image,
                wave=wave,
                kills=kills,
                game_over=False,
                enemies=enemies,
                game_mode=game_mode,
            )

        elif game_state == STATE_GAME_OVER:
            draw_background(screen, sky_texture, grass_texture, player)

            depth_buffer = ray_casting(screen, player, textures)
            render_sprites(screen, player, sprites + projectiles, depth_buffer)

            for explosion in explosions:
                explosion.draw(screen, player, depth_buffer)

            for enemy in enemies:
                enemy.draw(screen, player, depth_buffer)

            weapon.draw(screen)
            staff.draw(screen)
            draw_hud(
                screen,
                player,
                hud_image,
                wave=wave,
                kills=kills,
                game_over=True,
                enemies=enemies,
                game_mode=game_mode,
            )
            draw_game_over(screen)

        pygame.display.flip()

    if webcam_process:
        print("DEBUG: Terminating webcam subprocess...")
        webcam_process.terminate()
        try:
            webcam_process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            webcam_process.kill()

    pygame.quit()

if __name__ == "__main__":
    main()