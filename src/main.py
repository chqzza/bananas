import json
import pygame
import sys
import os

from settings import load_settings, save_settings, build_controls, make_screen, ap
from options import options_screen
from game import play
from ui import draw_title, clamp, DARK, WHITE, GREEN


def start_screen(screen, font):
    ## simple start screen that waits until player presses space
    ## returns True to continue or False to exit game
    start_img = pygame.image.load(ap("screens", "screen saver.png"))
    start_img = pygame.transform.scale(start_img, screen.get_size())
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return False
            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                return True

        screen.fill(DARK)
        screen.blit(start_img, (0, 0))

        pygame.display.flip()


def main_menu(screen, font):
    ## main menu with basic vertical selection system
    ## W/S moves selector, SPACE confirms choice

    options = ["Play", "Options", "Character Select", "Pick Save File", "Quit"]
    sel = 0  ## keeps track of currently selected option

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "quit"
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_w:
                    sel = clamp(sel-1, 0, len(options)-1)  ## prevents going above first option
                if e.key == pygame.K_s:
                    sel = clamp(sel+1, 0, len(options)-1)  ## prevents going below last option
                if e.key == pygame.K_SPACE:
                    return options[sel].lower()  ## returns selected option as lowercase string

        screen.fill(DARK)
        draw_title(screen, font, "Main Menu")

        for i, name in enumerate(options):
            color = GREEN if i == sel else WHITE  ## highlights selected option
            screen.blit(font.render(name, True, color), (520, 200 + i*90))

        pygame.display.flip()


def character_select(screen, font, settings, save_settings_fn):
    ## allows player to choose character sprite
    ## supports switching between male and female folders using TAB

    genders = ["Male", "Female"]
    gender_id = 0

    TILE_W, TILE_H = 192, 192
    START_X, START_Y = 260, 140
    GAP_X, GAP_Y = 200, 200  ## controls layout spacing of grid

    def load_characters(gender):
        ## loads all .png sprites from the gender folder
        char_dir = ap("characters", gender)
        files = [f for f in os.listdir(char_dir) if f.lower().endswith(".png")]
        files.sort()
        return char_dir, files

    char_dir, characters = load_characters(genders[gender_id])

    if not characters:
        return  ## safety check if folder empty

    sel = 0  ## currently selected character index

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    return  ## exits character select

                if e.key == pygame.K_TAB:
                    gender_id = (gender_id + 1) % len(genders)  ## swaps gender folder
                    char_dir, characters = load_characters(genders[gender_id])
                    sel = 0  ## resets selection

                if e.key == pygame.K_a:
                    sel = clamp(sel - 1, 0, len(characters) - 1)

                if e.key == pygame.K_d:
                    sel = clamp(sel + 1, 0, len(characters) - 1)

                if e.key == pygame.K_w:
                    sel = clamp(sel - 4, 0, len(characters) - 1)

                if e.key == pygame.K_s:
                    sel = clamp(sel + 4, 0, len(characters) - 1)
                    ## grid navigation in 4 columns

                if e.key == pygame.K_SPACE:
                    settings["player"]["selected_character"] = {
                        "gender": genders[gender_id],
                        "file": characters[sel]
                    }
                    save_settings_fn(settings)
                    return  ## saves selection and exits

        ## paging logic so only 8 characters are shown at once
        page = sel // 8
        tailPoint = page * 8
        headPoint = min(tailPoint + 8, len(characters))

        screen.fill(DARK)
        draw_title(screen,font,f"Character Select — {genders[gender_id]} (TAB to switch)")

        name = os.path.splitext(characters[sel])[0]
        screen.blit(font.render(f"Selected: {name}", True, WHITE),(60, 120))

        for idx, filename in enumerate(characters[tailPoint:headPoint]):
            col = idx % 4
            row = idx // 4

            x = START_X + col * GAP_X
            y = START_Y + row * GAP_Y + 100

            img = pygame.image.load(os.path.join(char_dir, filename)).convert_alpha()
            img = pygame.transform.scale(img, (TILE_W, TILE_H))
            screen.blit(img, (x, y))

            if tailPoint + idx == sel:
                pygame.draw.rect(
                    screen,
                    GREEN,
                    (x - 6, y - 6, TILE_W + 12, TILE_H + 12),
                    4
                )  ## draws highlight box around selected sprite

        pygame.display.flip()


def pick_save_file():
    ## allows player to choose between:
    ## N = New Game (clears save file)
    ## L = Load existing save file

    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    font = pygame.font.Font(ap("fonts", "path.ttf"), 40)

    file = "config/savegame"

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return None
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_n:
                    with open(file + ".json", "w") as f:
                        json.dump({}, f)  ## wipes save file completely
                    return file + ".json"

                if e.key == pygame.K_l:
                    if os.path.exists(file + ".json"):
                        return file + ".json"
                    else:
                        return None  ## prevents loading non-existent file

        screen.fill(DARK)
        draw_title(screen, font, "Press N for New Game or L to Load Game")
        pygame.display.flip()


def main():
    ## main entry point of the entire game
    ## handles:
    ## - loading settings
    ## - screen creation
    ## - main menu loop
    ## - launching play loop

    pygame.init()

    settings = load_settings()
    controls = build_controls(settings)

    screen = make_screen(settings)
    clock = pygame.time.Clock()

    font = pygame.font.Font(ap("fonts", "path.ttf"), 40)

    if not start_screen(screen, font):
        pygame.quit()
        sys.exit()  ## exits cleanly if player closes at start screen

    running = True

    while running:
        screen = make_screen(settings)  ## refresh display in case fullscreen changed

        choice = main_menu(screen, font)

        if choice == "play":
            result = play(screen, clock, font, settings, controls)
            if result == "quit":
                running = False

        elif choice == "options":
            result = options_screen(screen, font, settings, save_settings)
            controls = build_controls(settings)  ## rebuild controls if changed
            if result == "quit":
                running = False

        elif choice == "character select":
            result = character_select(screen, font, settings, save_settings)

        elif choice == "pick save file":
            result = pick_save_file()
            if result == "quit":
                running = False

        else:
            running = False  ## handles "quit" option

    pygame.quit()
    sys.exit()  ## ensures pygame closes properly


if __name__ == "__main__":
    main()