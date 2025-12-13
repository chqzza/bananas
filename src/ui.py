import pygame

WHITE = (255,255,255)
DARK  = (30,30,30)
BTN   = (50,50,80)
GREEN = (0,255,0)

def draw_title(surf, font, text, y=20):
    label = font.render(text, True, WHITE)
    surf.blit(label, label.get_rect(midtop=(surf.get_width()//2, y)))

def clamp(n, lo, hi):
    return max(lo, min(hi, n))

class Button:
    def __init__(self, x, y, w, h, text, font):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = font

    def draw(self, surf, selected=False):
        color = GREEN if selected else BTN
        pygame.draw.rect(surf, color, self.rect, border_radius=10)
        label = self.font.render(self.text, True, WHITE)
        surf.blit(label, label.get_rect(center=self.rect.center))
