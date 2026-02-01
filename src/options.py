import pygame
from ui import draw_title, clamp, DARK, WHITE, GREEN

def options_screen(screen, font, settings, save_settings_fn):
    items = ["Difficulty", "Fullscreen", "Back"]
    sel = 0
    diffs = ["Easy", "Normal", "Hard"]

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "quit"
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    return "back"
                if e.key == pygame.K_w:
                    sel = clamp(sel-1, 0, len(items)-1)
                if e.key == pygame.K_s:
                    sel = clamp(sel+1, 0, len(items)-1)

                if e.key == pygame.K_SPACE:
                    if items[sel] == "Difficulty":
                        cur = settings["gameplay"]["difficulty"]
                        idx = diffs.index(cur) if cur in diffs else 1
                        settings["gameplay"]["difficulty"] = diffs[(idx+1) % len(diffs)]
                        save_settings_fn(settings)

                    elif items[sel] == "Fullscreen":
                        settings["video"]["fullscreen"] = not settings["video"]["fullscreen"]
                        save_settings_fn(settings)

                    else:
                        return "back"

        screen.fill(DARK)
        draw_title(screen, font, "Options")

        info = f'Difficulty: {settings["gameplay"]["difficulty"]}   Fullscreen: {settings["video"]["fullscreen"]}'
        screen.blit(font.render(info, True, WHITE), (40, 90))

        for i, name in enumerate(items):
            color = GREEN if i == sel else WHITE
            screen.blit(font.render(name, True, color), (520, 200 + i*90))

        pygame.display.flip()
