import pygame

def make_sprite(color, size):
    surf = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.rect(surf, color, surf.get_rect(), border_radius=6)
    return surf

def load_sprites():
    return {
        "player": make_sprite((80, 200, 255), (60, 30)),
        "alien": make_sprite((255, 80, 200), (40, 30)),
        "boss": make_sprite((255, 80, 80), (240, 80)),
        "bullet": make_sprite((80, 255, 160), (8, 16)),
        "enemy_bullet": make_sprite((255, 100, 100), (8, 14)),
    }
