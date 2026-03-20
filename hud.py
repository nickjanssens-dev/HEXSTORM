import os
import pygame
import math
import settings
from map import game_map, TILE_SIZE

HUD_IMAGE = None
HUD_HEIGHT = 100

def get_fullscreen_button_rect():
    import settings
    return pygame.Rect(settings.SCREEN_WIDTH - 50, 10, 40, 40)

def draw_fullscreen_button(screen):
    rect = get_fullscreen_button_rect()
    
    # Button background (semi-transparent)
    bg_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(bg_surface, (0, 0, 0, 150), (0, 0, rect.width, rect.height), border_radius=8)
    screen.blit(bg_surface, rect.topleft)
    
    # Border
    pygame.draw.rect(screen, (220, 220, 220), rect, 2, border_radius=8)
    
    # Fullscreen Icon (4 corners)
    m = 10 # margin
    l = 8  # line length
    # Top-left corner
    pygame.draw.lines(screen, (255, 255, 255), False, [(rect.x + m, rect.y + m + l), (rect.x + m, rect.y + m), (rect.x + m + l, rect.y + m)], 2)
    # Top-right corner
    pygame.draw.lines(screen, (255, 255, 255), False, [(rect.right - m - l, rect.y + m), (rect.right - m, rect.y + m), (rect.right - m, rect.y + m + l)], 2)
    # Bottom-left corner
    pygame.draw.lines(screen, (255, 255, 255), False, [(rect.x + m, rect.bottom - m - l), (rect.x + m, rect.bottom - m), (rect.x + m + l, rect.bottom - m)], 2)
    # Bottom-right corner
    pygame.draw.lines(screen, (255, 255, 255), False, [(rect.right - m - l, rect.bottom - m), (rect.right - m, rect.bottom - m), (rect.right - m, rect.bottom - m - l)], 2)

def load_hud():
    global HUD_IMAGE
    import settings

    base_dir = os.path.dirname(__file__)
    path = os.path.join(base_dir, "assets", "textures", "misc", "HUD.png")

    raw = pygame.image.load(path).convert_alpha()

    bounds = raw.get_bounding_rect()
    raw = raw.subsurface(bounds).copy()

    HUD_IMAGE = pygame.transform.smoothscale(raw, (settings.SCREEN_WIDTH, HUD_HEIGHT))

def draw_text(screen, font, text, color, x, y):
    shadow = font.render(text, True, (0, 0, 0))
    screen.blit(shadow, (x + 2, y + 2))

    main = font.render(text, True, color)
    screen.blit(main, (x, y))
    screen.blit(main, (x + 1, y))
    screen.blit(main, (x, y + 1))


def draw_minimap(screen, player, enemies):
    # Positioning
    map_x, map_y = 20, 100
    tile_size = 4
    
    # Mini-map background
    minimap_width = len(game_map[0]) * tile_size
    minimap_height = len(game_map) * tile_size
    
    # Draw background/frame
    pygame.draw.rect(screen, (50, 50, 50), (map_x - 2, map_y - 2, minimap_width + 4, minimap_height + 4))
    
    bg_surface = pygame.Surface((minimap_width, minimap_height), pygame.SRCALPHA)
    bg_surface.fill((0, 0, 0, 180))
    screen.blit(bg_surface, (map_x, map_y))
    
    # Draw walls
    for y, row in enumerate(game_map):
        for x, tile in enumerate(row):
            if tile > 0: # 1, 2, 3 are walls
                color = (120, 120, 120) if tile == 1 else (160, 140, 100) # Poster/HEXSTORM walls slightly different
                pygame.draw.rect(screen, color, (map_x + x * tile_size, map_y + y * tile_size, tile_size, tile_size))
                
    # Draw enemies
    if enemies:
        for enemy in enemies:
            if enemy.alive:
                ex = int(enemy.x / TILE_SIZE)
                ey = int(enemy.y / TILE_SIZE)
                # Ensure within bounds
                if 0 <= ex < len(game_map[0]) and 0 <= ey < len(game_map):
                    pygame.draw.rect(screen, (255, 50, 50), (map_x + ex * tile_size, map_y + ey * tile_size, tile_size, tile_size))
                
    # Draw player
    px = int(player.x / TILE_SIZE)
    py = int(player.y / TILE_SIZE)
    if 0 <= px < len(game_map[0]) and 0 <= py < len(game_map):
        pygame.draw.rect(screen, (50, 255, 50), (map_x + px * tile_size, map_y + py * tile_size, tile_size, tile_size))
        
        # Draw player direction
        line_len = 8
        dir_x = map_x + px * tile_size + tile_size // 2 + math.cos(player.angle) * line_len
        dir_y = map_y + py * tile_size + tile_size // 2 + math.sin(player.angle) * line_len
        pygame.draw.line(screen, (50, 255, 50), (map_x + px * tile_size + tile_size // 2, map_y + py * tile_size + tile_size // 2), (dir_x, dir_y), 2)

def draw_hud(screen, player, wave=None, kills=None, game_over=False, enemies=None, game_mode="normal"):
    import settings
    import math
    import time
    hud_x = 0
    hud_y = settings.SCREEN_HEIGHT - HUD_HEIGHT

    # Only draw minimap in normal mode
    if game_mode == "normal":
        draw_minimap(screen, player, enemies)

    screen.blit(HUD_IMAGE, (hud_x, hud_y))

    font = pygame.font.SysFont("consolas", 20, bold=True)

    text_y = hud_y - 30

    draw_text(screen, font, f"HP: {player.health}", (255, 70, 70), 80, text_y)
    draw_text(screen, font, f"MP: {int(player.mana)}", (80, 170, 255), 200, text_y)
    #draw_text(screen, font, f"Spell: {player.current_spell}", (255, 245, 140), 720, text_y)

    # Draw colored effects when damage reduction or healing is active
    current_time = time.time()
    if hasattr(player, 'damage_reduction_end_time') and player.damage_reduction_end_time > current_time:
        if player.damage_reduction == 0.5:  # Arcane bulwark (50% reduction)
            # Pulsing purple glow effect
            pulse = abs(math.sin(current_time * 3))  # Pulse speed
            alpha = int(50 + pulse * 30)  # Alpha between 20-50
            
            # Create purple glow overlay
            glow_surface = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
            glow_surface.fill((128, 0, 128, alpha))  # Purple color with alpha
            screen.blit(glow_surface, (0, 0))
        elif player.damage_reduction == 1.0:  # Void bulwark (100% immunity)
            # Pulsing gold glow effect
            pulse = abs(math.sin(current_time * 3))  # Pulse speed
            alpha = int(50 + pulse * 30)  # Alpha between 20-50
            
            # Create gold glow overlay
            glow_surface = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
            glow_surface.fill((255, 215, 0, alpha))  # Gold color with alpha
            screen.blit(glow_surface, (0, 0))

    # Check for recent healing (green flash for 1 second)
    if hasattr(player, 'heal_time') and current_time - player.heal_time < 1.0:
        alpha = int(100 * (1.0 - (current_time - player.heal_time)))  # Fade out over 1 second
        green_surface = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
        green_surface.fill((0, 255, 0, alpha))  # Green color with alpha
        screen.blit(green_surface, (0, 0))

    draw_fullscreen_button(screen)

    # --- Draw Compass to Closest Enemy ---
    # Only show in normal mode
    if game_mode == "normal" and enemies:
        closest_enemy = None
        min_dist = float('inf')
        for e in enemies:
            dx = e.x - player.x
            dy = e.y - player.y
            dist = math.hypot(dx, dy)
            if dist < min_dist:
                min_dist = dist
                closest_enemy = e

        if closest_enemy:
            dx = closest_enemy.x - player.x
            dy = closest_enemy.y - player.y
            
            # Angle relative to player's looking direction
            # If enemy is straight ahead, angle_diff = 0
            angle_diff = math.atan2(dy, dx) - player.angle
            
            # To draw on screen, 0 should point UP.
            # On screen Y axis is down. So UP is angle -pi/2
            display_angle = angle_diff - math.pi / 2
            
            cx = settings.SCREEN_WIDTH // 2 + 7
            cy = settings.SCREEN_HEIGHT - HUD_HEIGHT // 2 -80
            
            size = 20
            tip_x = cx + math.cos(display_angle) * size
            tip_y = cy + math.sin(display_angle) * size
            
            base_angle1 = display_angle + math.pi * 0.8
            base_angle2 = display_angle - math.pi * 0.8
            
            base1_x = cx + math.cos(base_angle1) * size * 0.7
            base1_y = cy + math.sin(base_angle1) * size * 0.7
            base2_x = cx + math.cos(base_angle2) * size * 0.7
            base2_y = cy + math.sin(base_angle2) * size * 0.7
            
            points = [(tip_x, tip_y), (base1_x, base1_y), (base2_x, base2_y)]
            pygame.draw.polygon(screen, (255, 50, 50), points)
            pygame.draw.polygon(screen, (255, 200, 200), points, 2)

    # --- Draw wave/kills if provided ---
    if wave is not None and kills is not None:
        wave_text = font.render(f"WAVE: {wave}", True, (255, 255, 255))
        kills_text = font.render(f"KILLS: {kills}", True, (255, 255, 255))
        screen.blit(wave_text, (20, 20))
        screen.blit(kills_text, (20, 50))
        
        # Draw game mode indicator
        mode_text = "HARDCORE" if game_mode == "hardcore" else "NORMAL"
        mode_color = (255, 100, 100) if game_mode == "hardcore" else (100, 255, 100)
        mode_display = font.render(f"MODE: {mode_text}", True, mode_color)
        screen.blit(mode_display, (20, 80))

    # --- Game Over Overlay ---
    if game_over:
        overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        font_large = pygame.font.SysFont("Arial", 80, bold=True)
        font_small = pygame.font.SysFont("Arial", 40)

        text_game_over = font_large.render("GAME OVER", True, (255, 0, 0))
        text_stats = font_small.render(f"WAVE: {wave} | KILLS: {kills}", True, (255, 255, 255))
        text_restart = font_small.render("PRESS 'R' TO RESTART", True, (200, 200, 200))

        screen.blit(
            text_game_over,
            (settings.SCREEN_WIDTH // 2 - text_game_over.get_width() // 2, settings.SCREEN_HEIGHT // 2 - 100)
        )
        screen.blit(
            text_stats,
            (settings.SCREEN_WIDTH // 2 - text_stats.get_width() // 2, settings.SCREEN_HEIGHT // 2)
        )
        screen.blit(
            text_restart,
            (settings.SCREEN_WIDTH // 2 - text_restart.get_width() // 2, settings.SCREEN_HEIGHT // 2 + 100)
        )