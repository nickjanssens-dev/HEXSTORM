import pygame

from settings import SCREEN_WIDTH, SCREEN_HEIGHT, CROSSHAIR_COLOR


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


def draw_hud(screen, player):
    hud_height = 80
    hud_rect = pygame.Rect(0, SCREEN_HEIGHT - hud_height, SCREEN_WIDTH, hud_height)

    pygame.draw.rect(screen, (30, 30, 30), hud_rect)

    font = pygame.font.SysFont("consolas", 24)

    health_text = font.render(f"HP: {player.health}", True, (255, 50, 50))
    mana_text = font.render(f"MP: {player.mana}", True, (50, 150, 255))
    spell_text = font.render(f"Spell: {player.current_spell}", True, (255, 255, 100))

    screen.blit(health_text, (20, SCREEN_HEIGHT - 60))
    screen.blit(mana_text, (150, SCREEN_HEIGHT - 60))
    screen.blit(spell_text, (300, SCREEN_HEIGHT - 60))