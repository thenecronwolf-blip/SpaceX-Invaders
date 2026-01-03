import pygame
import random

pygame.font.init()

TITLE_FONT = pygame.font.SysFont("consolas", 64)
BTN_FONT = pygame.font.SysFont("consolas", 28)
SMALL_FONT = pygame.font.SysFont("consolas", 18)

NEON_PINK = (255, 80, 200)
NEON_BLUE = (80, 200, 255)
WHITE = (240, 240, 240)

def generate_stars(width, height, count=120):
    return [
        (random.randint(0, width), random.randint(0, height))
        for _ in range(count)
    ]

def draw_stars(surface, stars):
    for x, y in stars:
        surface.fill((255,255,255), ((x, y), (2,2)))

def neon_text(text, font, color):
    base = font.render(text, True, color)
    glow = pygame.Surface(
        (base.get_width()+8, base.get_height()+8),
        pygame.SRCALPHA
    )
    pygame.draw.rect(glow, (*color, 80), glow.get_rect(), border_radius=12)
    glow.blit(base, (4,4))
    return glow

def button(rect, text, mouse_pos, clicked):
    hover = rect.collidepoint(mouse_pos)
    color = NEON_BLUE if hover else NEON_PINK

    surf = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(surf, (*color, 120), surf.get_rect(), border_radius=10)
    pygame.draw.rect(surf, color, surf.get_rect(), 2, border_radius=10)

    label = BTN_FONT.render(text, True, WHITE)
    surf.blit(
        label,
        (
            rect.width//2 - label.get_width()//2,
            rect.height//2 - label.get_height()//2
        )
    )

    return surf, hover and clicked
