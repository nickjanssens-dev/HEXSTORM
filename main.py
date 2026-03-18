import pygame
import random
import math
import sys
import os
from enemy import Enemy
from background import draw_background
from hud import draw_crosshair, draw_hud
from player import Player
from raycasting import ray_casting
from weapon import Weapon
from map import game_map
from settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
    PLAYER_POS_X,
    PLAYER_POS_Y,
    PLAYER_ANGLE,
    PLAYER_SPEED,
    PLAYER_ROT_SPEED,
    WALL_TEXTURE_PATH,
    SKY_TEXTURE_PATH,
    GRASS_TEXTURE_PATH,
    TILE_SIZE,
)

def spawn_enemies(count):
    enemies = []
    empty_cells = []
    
    for y, row in enumerate(game_map):
        for x, cell in enumerate(row):
            if cell == 0:
                px = int(PLAYER_POS_X // TILE_SIZE)
                py = int(PLAYER_POS_Y // TILE_SIZE)
                if not (x == px and y == py):
                    # Safety buffer: 3 tiles
                    if abs(x - px) > 2 or abs(y - py) > 2:
                        empty_cells.append((x, y))
    
    if count > len(empty_cells):
        count = len(empty_cells)
        
    spawn_cells = random.sample(empty_cells, count)
    
    for cx, cy in spawn_cells:
        ex = cx * TILE_SIZE + TILE_SIZE // 2
        ey = cy * TILE_SIZE + TILE_SIZE // 2
        enemies.append(Enemy(ex, ey))
        
    return enemies

def show_game_over(screen, kills, wave):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Semi-transparent black
    screen.blit(overlay, (0, 0))

    font_large = pygame.font.SysFont("Arial", 80, bold=True)
    font_small = pygame.font.SysFont("Arial", 40)

    text_game_over = font_large.render("GAME OVER", True, (255, 0, 0))
    text_stats = font_small.render(f"WAVE: {wave} | KILLS: {kills}", True, (255, 255, 255))
    text_restart = font_small.render("PRESS 'R' TO RESTART", True, (200, 200, 200))

    screen.blit(text_game_over, (SCREEN_WIDTH // 2 - text_game_over.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
    screen.blit(text_stats, (SCREEN_WIDTH // 2 - text_stats.get_width() // 2, SCREEN_HEIGHT // 2))
    screen.blit(text_restart, (SCREEN_WIDTH // 2 - text_restart.get_width() // 2, SCREEN_HEIGHT // 2 + 100))

def main():
    try:
        pygame.init()
        # Ensure mixer is definitely up
        if not pygame.mixer.get_init():
            pygame.mixer.init()
            
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("HEXSTORM")
        clock = pygame.time.Clock()

        # Load textures once
        wall_texture = pygame.image.load(WALL_TEXTURE_PATH).convert()
        sky_texture = pygame.image.load(SKY_TEXTURE_PATH).convert()
        grass_texture = pygame.image.load(GRASS_TEXTURE_PATH).convert()

        def init_game():
            return {
                "player": Player(PLAYER_POS_X, PLAYER_POS_Y, PLAYER_ANGLE, PLAYER_SPEED, PLAYER_ROT_SPEED),
                "enemies": spawn_enemies(3), # Start Wave 1 with 3 bats
                "weapon": Weapon(),
                "kills": 0,
                "wave": 1,
                "game_over": False
            }

        game = init_game()
        running = True
        
        while running:
            dt = clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if game["game_over"] and event.key == pygame.K_r:
                        game = init_game()

            if not game["game_over"]:
                # Update player and weapon
                player = game["player"]
                player.movement()
                game["weapon"].update(dt, player)
                
                # Update enemies and cleanup dead ones
                new_enemies = []
                for enemy in game["enemies"]:
                    enemy.update(player, dt)
                    if not enemy.alive and enemy.animation_finished:
                        game["kills"] += 1
                        continue
                    new_enemies.append(enemy)
                
                # Check for wave completion
                if not new_enemies:
                    game["wave"] += 1
                    # Scaling: Wave 1=3, 2=4, 3=5, etc.
                    game["enemies"] = spawn_enemies(game["wave"] + 2)
                else:
                    # Sort for layered rendering
                    new_enemies.sort(key=lambda e: math.hypot(e.x - player.x, e.y - player.y), reverse=True)
                    game["enemies"] = new_enemies

                if player.health <= 0:
                    game["game_over"] = True

            # --- Drawing ---
            draw_background(screen, sky_texture, grass_texture)
            ray_casting(screen, game["player"], wall_texture)
            
            # Draw enemies (behind weapon and HUD)
            for enemy in game["enemies"]:
                enemy.draw(screen, game["player"])
                
            game["weapon"].draw(screen)
            draw_crosshair(screen)
            draw_hud(screen, game["player"], game["wave"])

            if game["game_over"]:
                show_game_over(screen, game["kills"], game["wave"])

            pygame.display.flip()

        pygame.quit()
    except Exception as e:
        print(f"FATAL ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        pygame.quit()

if __name__ == "__main__":
    main()