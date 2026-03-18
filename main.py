import pygame
import random
import math
import sys
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

def show_game_over(screen, kills):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Semi-transparent black
    screen.blit(overlay, (0, 0))

    font_large = pygame.font.SysFont("Arial", 80, bold=True)
    font_small = pygame.font.SysFont("Arial", 40)

    text_game_over = font_large.render("GAME OVER", True, (255, 0, 0))
    text_kills = font_small.render(f"BATS EXTERMINATED: {kills}", True, (255, 255, 255))
    text_restart = font_small.render("PRESS 'R' TO RESTART", True, (200, 200, 200))

    screen.blit(text_game_over, (SCREEN_WIDTH // 2 - text_game_over.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
    screen.blit(text_kills, (SCREEN_WIDTH // 2 - text_kills.get_width() // 2, SCREEN_HEIGHT // 2))
    screen.blit(text_restart, (SCREEN_WIDTH // 2 - text_restart.get_width() // 2, SCREEN_HEIGHT // 2 + 100))

def main():
    try:
        pygame.init()
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
                "enemies": spawn_enemies(8), # Spawn 8 bats for more challenge
                "weapon": Weapon(),
                "kills": 0,
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
                # Update everything
                player = game["player"]
                player.movement()
                game["weapon"].update(dt, player)
                
                # Update enemies and handle cleanup/respawn
                new_enemies = []
                for enemy in game["enemies"]:
                    enemy.update(player, dt)
                    if not enemy.alive and enemy.animation_finished:
                        game["kills"] += 1
                        # We don't add dead and finished enemies back
                        continue
                    new_enemies.append(enemy)
                
                # Respawn logic: if we have few bats left, spawn more
                if len(new_enemies) < 3:
                     game["enemies"] = new_enemies + spawn_enemies(5)
                else:
                     game["enemies"] = new_enemies

                if player.health <= 0:
                    game["game_over"] = True

            # --- Drawing ---
            # 1. Background
            draw_background(screen, sky_texture, grass_texture)
            
            # 2. Walls
            ray_casting(screen, game["player"], wall_texture)
            
            # 3. Enemies
            game["enemies"].sort(key=lambda e: math.hypot(e.x - game["player"].x, e.y - game["player"].y), reverse=True)
            for enemy in game["enemies"]:
                enemy.draw(screen, game["player"])
                
            # 4. Weapon & UI
            game["weapon"].draw(screen)
            draw_crosshair(screen)
            draw_hud(screen, game["player"])

            # 5. Game Over Overlay
            if game["game_over"]:
                show_game_over(screen, game["kills"])

            pygame.display.flip()

        pygame.quit()
    except Exception as e:
        print(f"FATAL ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        pygame.quit()

if __name__ == "__main__":
    main()