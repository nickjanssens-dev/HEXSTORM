import os
import pygame

from settings import SCREEN_WIDTH, SCREEN_HEIGHT, CROSSHAIR_COLOR

HUD_IMAGE = None
HUD_HEIGHT = 100


def load_hud():
    global HUD_IMAGE

    base_dir = os.path.dirname(__file__)
    path = os.path.join(base_dir, "assets", "textures", "misc", "HUD.png")

    raw = pygame.image.load(path).convert_alpha()

    bounds = raw.get_bounding_rect()
    raw = raw.subsurface(bounds).copy()

    HUD_IMAGE = pygame.transform.smoothscale(raw, (SCREEN_WIDTH, HUD_HEIGHT))


def draw_crosshair(screen):
    center_x = SCREEN_WIDTH // 2
    center_y = SCREEN_HEIGHT // 2
    size = 8

    pygame.draw.line(
        screen,
        CROSSHAIR_COLOR,
        (center_x - size, center_y),
        (center_x + size, center_y),
        2
    )
    pygame.draw.line(
        screen,
        CROSSHAIR_COLOR,
        (center_x, center_y - size),
        (center_x, center_y + size),
        2
    )


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