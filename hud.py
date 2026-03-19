import os
import pygame

import settings

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

def draw_hud(screen, player, wave=None, kills=None, game_over=False):
    import settings
    hud_x = 0
    hud_y = settings.SCREEN_HEIGHT - HUD_HEIGHT

    screen.blit(HUD_IMAGE, (hud_x, hud_y))

    font = pygame.font.SysFont("consolas", 20, bold=True)

    text_y = hud_y - 30

    draw_text(screen, font, f"HP: {player.health}", (255, 70, 70), 80, text_y)
    draw_text(screen, font, f"MP: {int(player.mana)}", (80, 170, 255), 200, text_y)
    draw_text(screen, font, f"Spell: {player.current_spell}", (255, 245, 140), 720, text_y)

    draw_fullscreen_button(screen)

    # --- Draw wave/kills if provided ---
    if wave is not None and kills is not None:
        wave_text = font.render(f"WAVE: {wave}", True, (255, 255, 255))
        kills_text = font.render(f"KILLS: {kills}", True, (255, 255, 255))
        screen.blit(wave_text, (20, 20))
        screen.blit(kills_text, (20, 50))

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