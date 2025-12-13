import pygame
import sys
import os

from settings import load_settings, save_settings, build_controls, make_screen, ap
from options import options_screen
from game import play
from ui import draw_title, clamp, DARK, WHITE, GREEN

def start_screen(screen, font):
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return False
            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                return True

        screen.fill(DARK)
        draw_title(screen, font, "Press SPACE to start", y=300)
        pygame.display.flip()

def main_menu(screen, font):
    options = ["Play", "Options", "Character Select", "Quit"]
    sel = 0

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "quit"
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_w:
                    sel = clamp(sel-1, 0, len(options)-1)
                if e.key == pygame.K_s:
                    sel = clamp(sel+1, 0, len(options)-1)
                if e.key == pygame.K_SPACE:
                    return options[sel].lower()

        screen.fill(DARK)
        draw_title(screen, font, "Main Menu")

        for i, name in enumerate(options):
            color = GREEN if i == sel else WHITE
            screen.blit(font.render(name, True, color), (520, 200 + i*90))

        pygame.display.flip()

def character_select(screen, font, settings, save_settings_fn):
    male_dir = ap("characters", "Male")
    males = [f for f in os.listdir(male_dir) if f.lower().endswith(".png")]
    males.sort()

    if not males:
        return
    sel = 0
    
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    return
                if e.key == pygame.K_a:
                    sel = clamp(sel-1, 0, len(males)-1)
                if e.key == pygame.K_d:
                    sel = clamp(sel+1, 0, len(males)-1)
                if e.key == pygame.K_SPACE:
                    # store filename (simple + reliable)
                    settings["player"]["selected_character"] = males[sel]
                    save_settings_fn(settings)
                    return

        screen.fill(DARK)
        draw_title(screen, font, "Character Select (A/D, SPACE choose, ESC back)")

        name = males[sel]
        screen.blit(font.render(f"Selected: {name}", True, WHITE), (60, 120))

        img = pygame.image.load(os.path.join(male_dir, name)).convert_alpha()
        img = pygame.transform.scale(img, (192, 192))
        screen.blit(img, (540, 260))

        pygame.display.flip()

def main():
    pygame.init()

    settings = load_settings()
    controls = build_controls(settings)

    screen = make_screen(settings)
    clock = pygame.time.Clock()

    font = pygame.font.Font(ap("fonts", "path.ttf"), 40)

    if not start_screen(screen, font):
        pygame.quit()
        sys.exit()

    running = True
    while running:
        # if fullscreen option changed, refresh display mode
        screen = make_screen(settings)

        choice = main_menu(screen, font)

        if choice == "play":
            result = play(screen, clock, font, settings, controls)
            if result == "quit":
                running = False

        elif choice == "options":
            result = options_screen(screen, font, settings, save_settings)
            controls = build_controls(settings) 
            if result == "quit":
                running = False

        elif choice == "character select":
            sel = character_select(screen, font, settings, save_settings)

        else:
            running = False

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
