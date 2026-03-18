import os
import pygame

from settings import SCREEN_WIDTH, SCREEN_HEIGHT, CROSSHAIR_COLOR

HUD_IMAGE = None
HUD_HEIGHT = 100

def get_fullscreen_button_rect():
    return pygame.Rect(SCREEN_WIDTH - 50, 10, 40, 40)

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

    base_dir = os.path.dirname(__file__)
    path = os.path.join(base_dir, "assets", "textures", "misc", "HUD.png")

    raw = pygame.image.load(path).convert_alpha()

    bounds = raw.get_bounding_rect()
    raw = raw.subsurface(bounds).copy()

    HUD_IMAGE = pygame.transform.smoothscale(raw, (SCREEN_WIDTH, HUD_HEIGHT))

def draw_text(screen, font, text, color, x, y):
    shadow = font.render(text, True, (0, 0, 0))
    screen.blit(shadow, (x + 2, y + 2))

    main = font.render(text, True, color)
    screen.blit(main, (x, y))
    screen.blit(main, (x + 1, y))
    screen.blit(main, (x, y + 1))


def draw_hud(screen, player):
    hud_x = 0
    hud_y = SCREEN_HEIGHT - HUD_HEIGHT

    screen.blit(HUD_IMAGE, (hud_x, hud_y))

    font = pygame.font.SysFont("consolas", 20, bold=True)

    text_y = hud_y - 30

    draw_text(screen, font, f"HP: {player.health}", (255, 70, 70), 80, text_y)
    draw_text(screen, font, f"MP: {player.mana}", (80, 170, 255), 300, text_y)
    draw_text(screen, font, f"Spell: {player.current_spell}", (255, 245, 140), 720, text_y)

    draw_fullscreen_button(screen)