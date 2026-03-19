import math
import os
import random

import pygame

from background import draw_background
from hud import draw_hud, load_hud, get_fullscreen_button_rect
from player import Player
from raycasting import ray_casting
from weapon import Weapon
from staff import Staff
from enemy import Bat, Skeleton, Slime
from explosion import Explosion
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
from map import get_free_pos, game_map, TILE_SIZE, is_wall
from sprite import Sprite, render_sprites


STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_GAME_OVER = "game_over"


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


def create_plant_sprites(amount=15):
    sprites = []

    plant_texture = pygame.image.load(
        "assets/textures/sprites/plant_fern.png"
    ).convert_alpha()

    plant_texture = plant_texture.subsurface((253, 232, 502, 512)).copy()

    for _ in range(amount):
        while True:
            sx = random.randint(1, len(game_map[0]) - 2)
            sy = random.randint(1, len(game_map) - 2)

            if game_map[sy][sx] == 0:
                sprite_x = sx * TILE_SIZE + TILE_SIZE // 2
                sprite_y = sy * TILE_SIZE + TILE_SIZE // 2
                sprites.append(Sprite(sprite_x, sprite_y, plant_texture))
                break

    return sprites


def create_enemies(player=None, amount=3):
    enemies = []

    for _ in range(amount):
        while True:
            sx = random.randint(1, len(game_map[0]) - 2)
            sy = random.randint(1, len(game_map) - 2)

            if game_map[sy][sx] == 0:
                enemy_x = sx * TILE_SIZE + TILE_SIZE // 2
                enemy_y = sy * TILE_SIZE + TILE_SIZE // 2

                if player:
                    dx = enemy_x - player.x
                    dy = enemy_y - player.y
                    dist = math.hypot(dx, dy)
                    if dist < 200 or dist > 1000:
                        continue

                enemies.append(random.choice([Bat, Skeleton, Slime])(enemy_x, enemy_y))
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

    game_over_rect = game_over_text.get_rect(
        center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30)
    )
    restart_rect = restart_text.get_rect(
        center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40)
    )

    screen.blit(game_over_text, game_over_rect)
    screen.blit(restart_text, restart_rect)


def draw_menu(screen, background, selected_option, menu_options):
    screen.blit(background, (0, 0))

    title_font = pygame.font.SysFont("Times New Roman", 84, bold=True)
    option_font = pygame.font.SysFont("Arial", 42, bold=True)

    # Optional dark overlay to make text easier to read
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 70))
    screen.blit(overlay, (0, 0))

    title_text = title_font.render("HEXSTORM", True, (255, 230, 180))
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 140))
    screen.blit(title_text, title_rect)

    start_y = SCREEN_HEIGHT // 2 + 30
    spacing = 80

    for i, option in enumerate(menu_options):
        if i == selected_option:
            color = (255, 210, 100)
        else:
            color = (230, 230, 230)

        text = option_font.render(option, True, color)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, start_y + i * spacing))
        screen.blit(text, rect)

    hint_font = pygame.font.SysFont("Arial", 22)
    hint_text = hint_font.render("Use UP / DOWN and ENTER", True, (220, 220, 220))
    hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60))
    screen.blit(hint_text, hint_rect)


def reset_game():
    start_x, start_y = get_free_pos()

    player = Player(
        start_x,
        start_y,
        PLAYER_ANGLE,
        PLAYER_SPEED,
        PLAYER_ROT_SPEED
    )

    sprites = create_plant_sprites(15)
    enemies = create_enemies(player, 3)
    explosions = []

    weapon = Weapon()
    staff = Staff()
    projectiles = []

    wave = 1
    kills = 0

    return player, sprites, enemies, explosions, weapon, staff, projectiles, wave, kills


def toggle_fullscreen(screen):
    if screen.get_flags() & pygame.FULLSCREEN:
        return pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT),
            pygame.SCALED
        )
    return pygame.display.set_mode(
        (SCREEN_WIDTH, SCREEN_HEIGHT),
        pygame.SCALED | pygame.FULLSCREEN
    )


def main():
    pygame.init()

    try:
        music_path = os.path.join("assets", "textures", "sounds", "soundtrack.wav")
        if os.path.exists(music_path):
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(-1)
        else:
            print(f"DEBUG: Soundtrack NOT FOUND at {music_path}")
    except Exception as e:
        print(f"DEBUG: Could not load soundtrack: {e}")

    flags = pygame.SCALED
    if FULLSCREEN:
        flags |= pygame.FULLSCREEN

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
    pygame.display.set_caption("HEXSTORM - Raycasting Prototype")
    clock = pygame.time.Clock()

    load_hud()
    textures, sky_texture, grass_texture = load_textures()
    menu_background = load_menu_background()

    player, sprites, enemies, explosions, weapon, staff, projectiles, wave, kills = reset_game()

    game_state = STATE_MENU
    menu_options = ["PLAY", "QUIT"]
    selected_option = 0

    running = True
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
                    if event.key == pygame.K_UP:
                        selected_option = (selected_option - 1) % len(menu_options)

                    elif event.key == pygame.K_DOWN:
                        selected_option = (selected_option + 1) % len(menu_options)

                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        choice = menu_options[selected_option]

                        if choice == "PLAY":
                            player, sprites, enemies, explosions, weapon, staff, projectiles, wave, kills = reset_game()
                            game_state = STATE_PLAYING

                        elif choice == "QUIT":
                            running = False

                elif game_state == STATE_PLAYING:
                    if event.key == pygame.K_1:
                        staff.current_spell = "fireball"

                    elif event.key == pygame.K_2:
                        staff.current_spell = "ice"

                    elif event.key == pygame.K_f:
                        staff.cast(player)

                elif game_state == STATE_GAME_OVER:
                    if event.key == pygame.K_r:
                        player, sprites, enemies, explosions, weapon, staff, projectiles, wave, kills = reset_game()
                        game_state = STATE_PLAYING

        if game_state == STATE_PLAYING:
            for explosion in explosions:
                explosion.update(dt)
            explosions = [e for e in explosions if e.alive]

            player.movement()
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

            # Projectile vs bat collision
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
                        # Fireball / AoE projectile
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
                            # Single target projectile
                            enemy.take_damage(projectile.damage)

                            if hasattr(projectile, "slow_factor"):
                                enemy.apply_slow(
                                    projectile.slow_factor,
                                    projectile.slow_duration
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
                enemies.extend(create_enemies(player, 2 + wave))

            if player.health <= 0:
                game_state = STATE_GAME_OVER

        if game_state == STATE_MENU:
            draw_menu(screen, menu_background, selected_option, menu_options)

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
            draw_hud(screen, player, wave=wave, kills=kills, game_over=False, enemies=enemies)

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
            draw_hud(screen, player, wave=wave, kills=kills, game_over=True, enemies=enemies)
            draw_game_over(screen)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()