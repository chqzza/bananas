import pygame
from ui import draw_title, clamp, DARK, WHITE, GREEN


def options_screen(screen, font, settings, save_settings_fn):
    ## options menu allowing the player to:
    ## - change difficulty
    ## - toggle fullscreen
    ## - go back to main menu

    items = ["Difficulty", "Fullscreen", "Back"]
    sel = 0  ## keeps track of which option is currently selected
    diffs = ["Easy", "Normal", "Hard"]  ## possible difficulty values

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "quit"

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    return "back"  ## allows quick exit from options

                if e.key == pygame.K_w:
                    sel = clamp(sel-1, 0, len(items)-1)  ## moves selection up safely

                if e.key == pygame.K_s:
                    sel = clamp(sel+1, 0, len(items)-1)  ## moves selection down safely

                if e.key == pygame.K_SPACE:
                    if items[sel] == "Difficulty":
                        cur = settings["gameplay"]["difficulty"]
                        idx = diffs.index(cur) if cur in diffs else 1
                        ## cycles to next difficulty in list
                        settings["gameplay"]["difficulty"] = diffs[(idx+1) % len(diffs)]
                        save_settings_fn(settings)  ## saves immediately so change persists

                    elif items[sel] == "Fullscreen":
                        settings["video"]["fullscreen"] = not settings["video"]["fullscreen"]
                        ## toggles fullscreen boolean value
                        save_settings_fn(settings)

                    else:
                        return "back"  ## if "Back" selected, exit options screen

        screen.fill(DARK)
        draw_title(screen, font, "Options")

        ## displays current settings at top for clarity
        info = f'Difficulty: {settings["gameplay"]["difficulty"]}   Fullscreen: {settings["video"]["fullscreen"]}'
        screen.blit(font.render(info, True, WHITE), (40, 90))

        ## draws selectable menu items
        for i, name in enumerate(items):
            color = GREEN if i == sel else WHITE  ## highlights selected item
            screen.blit(font.render(name, True, color), (520, 200 + i*90))

        pygame.display.flip()