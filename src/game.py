import os
import random
import pygame

from world import World
from classes import Player, Enemy
from settings import ap

WHITE = (255,255,255)

def draw_health_bar(surf, x, y, hp, hp_max):
    w, h = 250, 28
    fill = int((hp / hp_max) * w) if hp_max > 0 else 0
    pygame.draw.rect(surf, (0,255,0), (x, y, fill, h))
    pygame.draw.rect(surf, WHITE, (x, y, w, h), 2)

def pick_random_png(folder_path):
    files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith(".png")]
    if not files:
        raise FileNotFoundError(f"No .png files in {folder_path}")
    return random.choice(files)

def make_player(settings):
    # character select can store either a filename or a tag
    selected = settings["player"].get("selected_character", "")

    male_dir = ap("characters", "Male")
    if selected and os.path.exists(os.path.join(male_dir, selected)):
        sprite = os.path.join(male_dir, selected)
    else:
        sprite = pick_random_png(male_dir)

    speed = settings["gameplay"].get("player_speed", 250)
    p = Player("Player", 640, 360, 100, 10, 5, speed, sprite)
    p.gold = settings["player"].get("starting_gold", 0)
    p.level = settings["player"].get("starting_level", 1)
    return p

def make_enemies(count=3):
    enemy_dir = ap("characters", "Enemy")
    files = [os.path.join(enemy_dir, f) for f in os.listdir(enemy_dir) if f.lower().endswith(".png")]
    if not files:
        raise FileNotFoundError("No enemy sprites in assets/characters/Enemy")

    enemies = []
    for i in range(count):
        sprite = random.choice(files)
        enemies.append(Enemy(f"Enemy {i+1}", random.randint(120, 1160), random.randint(120, 600),
                             50, 5, 2, 200, sprite))
    return enemies

def play(screen, clock, font, settings, controls):
    world = World(ap("maps", "bananas_map.tmx"))
    player = make_player(settings)
    enemies = make_enemies(count=3)

    tracking_range = settings["gameplay"].get("enemy_tracking_range", 400)
    min_range = settings["gameplay"].get("enemy_min_range", 50)

    cam_x, cam_y = 0, 0

    while True:
        dt = clock.tick(120) / 1000.0

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "quit"
            if e.type == pygame.KEYDOWN and e.key == controls["pause"]:
                return "menu"

        keys = pygame.key.get_pressed()

        player.move(dt, keys, controls, world.collides)
        for enemy in enemies:
            enemy.track(player, dt, enemies, tracking_range=tracking_range, min_range=min_range)

        # camera follows player, clamped
        sw, sh = screen.get_size()
        cam_x = int(player.x - sw/2)
        cam_y = int(player.y - sh/2)

        cam_x = max(0, min(cam_x, max(0, world.width_px - sw)))
        cam_y = max(0, min(cam_y, max(0, world.height_px - sh)))

        world.draw(screen, cam_x, cam_y)
        player.draw(screen, cam_x, cam_y)
        for enemy in enemies:
            enemy.draw(screen, cam_x, cam_y)

        player.melee(keys, controls, screen, cam_x, cam_y)

        draw_health_bar(screen, sw - 270, 20, player.hp, player.hp_max)
        screen.blit(font.render("ESC = Menu", True, WHITE), (20, 20))

        pygame.display.flip()
