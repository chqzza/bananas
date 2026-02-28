import os
import random
import pygame

from world import World
from classes import *
from settings import ap
from save_system import write_save, load_save
from options import options_screen
from items import items


WHITE = (255,255,255)
GREEN = (0,255,0)
PURPLE = (255,0,255) ## some basic colours for hp and xp bars

def draw_health_bar(surf, x, y, hp, hp_max):
    w, h = 250, 28
    fill = int((hp / hp_max) * w) if hp_max > 0 else 0
    pygame.draw.rect(surf, GREEN, (x, y, fill, h))
    pygame.draw.rect(surf, WHITE, (x, y, w, h), 2) ## draws the players hp bar scalling the bar to the players hp

def draw_xp_bar(surf, x, y, xp, xp_next, level, font):
    w, h = 250, 15
    fill = int((xp / xp_next) * w) if xp_next > 0 else 0
    pygame.draw.rect(surf, PURPLE, (x, y, fill, h))
    pygame.draw.rect(surf, WHITE, (x, y, w, h), 2)
    ## write level and xp text
    text = font.render(f"Level {level} - XP: {xp}/{xp_next}", True, WHITE)
    ## scale down to fit below the bar
    text = pygame.transform.scale(text, (text.get_width() * 0.3, text.get_height() * 0.3))
    surf.blit(text, (x, y + 15))

    



def make_player(settings):
    selected = settings["player"].get("selected_character")

    sprite = None

    ## load the selected character sprite if it exists, otherwise player will be a blank square
    if isinstance(selected, dict):
        gender = selected.get("gender", "Male") ## defaults to male
        filename = selected.get("file")

        char_dir = ap("characters", gender) ## gets directory of the gender folder attaching to assets via ap
        if filename and os.path.exists(os.path.join(char_dir, filename)):
            sprite = os.path.join(char_dir, filename)

    speed = settings["gameplay"].get("player_speed", 250)

    p = Player(
        "Player",
        settings["player"]["x"],
        settings["player"]["y"],
        100, 100, 40,
        speed,
        sprite
    ) ## basic definition of a player before a save file is made

    p.gold = settings["player"].get("starting_gold", 0)
    p.level = settings["player"].get("starting_level", 1)
    p.xp = 0
    p.xp_next = 100 ## initial xp needed for level up, can be scaled in the future for higher levels
    return p


def make_enemies():
    enemy_dir = ap("characters", "Enemy")
    files = [os.path.join(enemy_dir, f)
             for f in os.listdir(enemy_dir)
             if f.lower().endswith(".png")]

    if not files:
        raise FileNotFoundError("No enemy sprites in assets/characters/Enemy")

    # All spawn positions
    positions = [
        (600, 100), (600, 100), (600, 100),
        (1100, 500), (1100, 500),
        (2000, 1000), (2000, 1000), (2000, 1000), (2000, 1000),
        (2445, 232),
        (800, 2300), (800, 2300), (800, 2300),
        (400, 3000), (400, 3000), (400, 3000),
        (2250, 3200), (2250, 3200),
        (1191, 2111), (1191, 2111),
        (3595, 3241),
        (3709, 3217),
        (3962, 3340),
        (3607, 3643),
        (3861, 3778),
        (3993, 3626),
        (4222, 3517),
        (4516, 3490),
    ]

    # Add 10 random region enemies
    for _ in range(10):
        positions.append((
            random.randint(1900, 2300),
            random.randint(1800, 2200)
        ))

    enemies = []

    # Create Enemy objects
    for i, (x, y) in enumerate(positions):
        sprite = files[i % len(files)]
        enemy = Enemy(f"Enemy {i+1}", x, y, 300, 5, 2, 200, sprite)
        enemies.append(enemy)

    return enemies

def open_inventory(player, screen, font, keys):
    inventory_open = True
    item_selected = None
    item_held = False
    space_hovered = 0

    while inventory_open:
        # --- CLEAR SCREEN AREA ---
        pygame.draw.rect(screen, (50, 50, 50), (100, 100, 1000, 500))
        pygame.draw.rect(screen, WHITE, (100, 100, 1000, 500), 2)
        screen.blit(font.render("Inventory (Press I to close)", True, WHITE), (120, 120))

        # --- HANDLE EVENTS (ONLY ONCE PER FRAME) ---
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                inventory_open = False

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_i:
                    inventory_open = False

                elif e.key == pygame.K_w:
                    space_hovered = max(0, space_hovered - 1)

                elif e.key == pygame.K_s:
                    space_hovered = min(len(player.inventory.items) - 1, space_hovered + 1)

                elif e.key == pygame.K_SPACE:
                    if not item_held:
                        # Pick up item
                        if space_hovered < len(player.inventory.items):
                            item_selected = player.inventory.items[space_hovered]
                            start_pos = space_hovered
                            item_held = True
                    else:
                        # Swap items
                        if space_hovered < len(player.inventory.items):
                            player.inventory.items[start_pos], player.inventory.items[space_hovered] = \
                                player.inventory.items[space_hovered], player.inventory.items[start_pos]
                        item_held = False

        # --- DRAW ITEMS ---
        y_offset = 200
        for item in player.inventory.items:
            screen.blit(item.image, (120, y_offset))
            screen.blit(font.render(item.name, True, WHITE), (190, y_offset + 10))
            y_offset += 100

        # --- DRAW SELECTOR CIRCLE (ALIGNED PROPERLY) ---
        circle_y = 200 + space_hovered * 100 + 50
        pygame.draw.circle(screen, (0, 255, 0), (100, circle_y), 10, 2)

        pygame.display.flip()



def handle_portals(player, portals, keys, controls):

    ## Reduce cooldown
    if player.teleport_cooldown > 0:
        player.teleport_cooldown -= 1

    for portal in portals:
        if (
            portal.contains(player.x, player.y)
            and keys[controls["use"]]
            and player.teleport_cooldown == 0
            and player.last_portal != portal.id
            and (portal.key is None or portal.key in player.inventory.items) ## teleport only works under all conditions
        ):
            player.x, player.y = portal.target
            player.last_portal = portal.id
            player.teleport_cooldown = 100 ## resets cooldown to prevent immediate re-teleporting, can be adjusted for better feel
            break

    ## Reset lock when outside all portals
    if not any(portal.contains(player.x, player.y) for portal in portals):
        player.last_portal = None



def draw_items_ground(player, screen, ground_items, locations, cam_x, cam_y):
    i = 0
    while i < len(ground_items): ## used while over for loop because we might remove items while iterating

        if ground_items[i] in player.inventory.items:
            ground_items.pop(i)
            locations.pop(i) ## removes items from arrays if the player has them
        else:
            x, y = locations[i]
            ground_items[i].draw(screen, x, y, cam_x, cam_y)
            i += 1 ## increments if an item isnt removed, otherwise the next item will be skipped

    return ground_items, locations 



def play(screen, clock, font, settings, controls):
    world = World(ap("maps", "bananas_map.tmx")) ## loads the map from assets/maps, using ap function
    mini_boss_defeated = False
    boss_defeated = False
    mini_made, boss_made = False, False ## starting conditions for bosses

    player_data = load_save()
    if player_data:
        player = make_player(settings)
        items_to_remove = player.from_dict(player_data) ## if theres a save file load player data from it
    else:
        player = make_player(settings)
        items_to_remove = player.from_dict(player_data)
    pet = Pet(player, "MrMime")    
    player.pet = pet    ## hardcodes what pet the player has, can be expanded to have a choice


    enemies = make_enemies() ## spawns 10 enemies at spawn will be adjusted for better pacing once map is made and playtested
    
    tracking_range = settings["gameplay"].get("enemy_tracking_range", 400)
    min_range = settings["gameplay"].get("enemy_min_range", 50) ## parts of enemy settings is loaded, 400 and 50 for backups if there is an error

    cam_x, cam_y = 0, 0
    small_font = pygame.font.Font("assets/fonts/path.ttf", 20) ## smaller font for inventory text and other small text on screen

    item_spawns = [(380, 150), (1750, 80), (2300, 1080), (2400, 1080), (4250, 750)]
    ground_items = [items[0], items[4], items[2], items[10], items[1]] ## arrays for defining item spawns and what items thet are

    for item in items_to_remove:
        for item2 in items:
            if item2.name == item:
                player.inventory.add_item(item2)
        
        if item in ground_items:
            idx = ground_items.index(item)
            ground_items.remove(item)
            item_spawns.pop(idx)
    player.hand = player.inventory.items[0] if player.inventory.items else None
    ##removes items from the ground if they are in the inventory and sets the players hand to first item in inventory

    portals = [
        Portal("A", 2456, 2495, 956, 1013, 305, 1845, None),
        Portal("B", 281, 321, 1807, 1887, 2458, 958, None),
        Portal("C", 20, 50, 2361, 2414, 480, 3441, items[11]),
        Portal("D", 2248, 2315, 2975, 2990, 4200, 700, items[10]),
        Portal("E", 1030, 1075 , 1820, 1875, 3530, 3085, items[1])]    

    signs = [
        Sign(425, 450, 100, 125, "Press [E] to pick up weapon"), #first spawn
        Sign(1725, 1750, 50, 75, "Press [I] for the inventory and press [E] to equip the armour"),#on bridge
        Sign(460, 490, 1810, 1830, "Beware of the mini boss ahead!"),#start of cave sequence
        Sign(1040, 1060, 2400, 2435, "The mini boss drops a powerful item, but is very strong!"), # before mini boss room
        Sign(2145, 2170, 3020, 3050, "You must grab the ancient artifact to enter the mini boss room!"), # before cave
        Sign(2525, 2550, 2790, 2815, "To defeat the final boss, you must first defeat the mini boss"),#in coridoor
        Sign(1150, 1175, 1760, 1780, "The boss is even stronger, but drops the key to finish the game!"), # final cave door
        Sign(100, 125, 2325, 2350, "You need to get the royal seal to open the final door!")]
## definnitions of all regions in the game --- portals and destinations along with all the signs
    while True and not player.is_dead(): ## only runs if player is alive, otherwise goes back to menu
        player.hand = player.inventory.items[0] if player.inventory.items else None ## always updates player hand first
        dt = clock.tick(120) / 1000.0 ## starts the clock tick for smooth fps movement

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "quit"
            if e.type == pygame.KEYDOWN and e.key == controls["pause"]:
                dict = player.to_dict()
                write_save(dict)
                return "menu"
            if e.type == pygame.KEYDOWN and e.key == controls["options"]:
                result = options_screen(screen, font, settings, write_save)
                if result == "quit":
                    return "quit"
                elif result == "back":
                    dict = player.to_dict()
                    write_save(dict)
            if e.type == pygame.KEYDOWN and e.key == controls["inventory"]:
                open_inventory(player, screen, font, keys)

                pygame.display.flip()
## all options for exiting the game loop temportarily or permanently, saving the game, and opening the inventory

                    
        keys = pygame.key.get_pressed() ## used for all actions after

        player.ranged(keys, controls)
        player.update_projectiles(dt, enemies)
        player.melee(keys, controls, enemies)  # Check for attack input

        player.update_attack(dt)  # Update attack animation
        player.move(dt, keys, controls, world.collides, settings)
        player.heal(keys, controls)
        player.equip_armour(keys, controls) ## entire player update handling all methods in player class that are needed
    
       
        ## camera follows player, clamped
        sw, sh = screen.get_size()
        cam_x = int(player.x - sw/2)
        cam_y = int(player.y - sh/2)

        cam_x = max(0, min(cam_x, max(0, world.width_px - sw)))
        cam_y = max(0, min(cam_y, max(0, world.height_px - sh)))



        world.draw(screen, cam_x, cam_y, player) ## player is drawn in world draw to allow for foreground and background layers
  
        for enemy in enemies:
            enemy.track(player, dt, enemies,world.collides, tracking_range, min_range)
            if isinstance(enemy, Boss):
                enemy.boss_draw(screen, cam_x, cam_y)
            else:
                enemy.draw(screen, cam_x, cam_y)
            enemy.draw_health_bar(screen, cam_x, cam_y) ## basic checking for enemy tracking and drawing, along with hp bars for enemies
            if enemy.is_dead():
                enemies.remove(enemy)
                player.xp += 100
                if player.xp >= player.xp_next:
                    player.level_up(items) ## gives xp for leveling up 
        
        screen.blit(font.render("ESC = Menu", True, WHITE), (20, 20))
        screen.blit(font.render(f"Player: ({int(player.x)}, {int(player.y)})", True, WHITE), (20, 50))
        backpack_img = pygame.image.load("assets/general png/backpack1.png").convert_alpha()

        screen.blit(backpack_img, (1200, 600))
        screen.blit(small_font.render("[I] Inventory", True, WHITE), (1100, 670))
        draw_health_bar(screen, 1000, 20, player.hp, player.hp_max)
        draw_xp_bar(screen, 1000, 50, player.xp, player.xp_next, player.level, font)

        draw_items_ground(player, screen, ground_items, item_spawns, cam_x, cam_y)
        player.draw_projectiles(screen, cam_x, cam_y) 
        ##draws all these parts above the world draw so they remain visible and on top of the world and enemies

        for item in ground_items:
            ground_items, item_spawns = item.pickup(player, item_spawns[ground_items.index(item)], ground_items, item_spawns, keys, controls)

        handle_portals(player, portals, keys, controls)
        for sign in signs:
            if sign.contains(player.x, player.y) and keys[controls["use"]]:
                sign.write_message(screen,font)
        ## handles all interactions with signs and portals 

        Mini_boss_region = Region(4000,5000, 500, 1500)
        ##defining area where mini boss spawns
        if Mini_boss_region.contains(player.x, player.y) and not mini_boss_defeated:
            mini_sprite = ap("characters", "Boss", "Boss 01.png")

            if not mini_made:

                mini_boss = Boss("Mini Boss", 4500, 1000, 2000, 100, 90, 175, mini_sprite,0)
                enemies.append(mini_boss) ## the boss will only spawn when the player enters the regions and will only spawn once
                mini_made = True
            if mini_boss.is_dead():
                mini_boss_defeated = True

                player.level_up(items)
                player.level_up(items)
                player.level_up(items)
                player.inventory.add_item(items[6])
        
        Boss_region = Region(4178, 4592, 3625, 4005)
        if Boss_region.contains(player.x, player.y) and not boss_defeated:
            boss_sprite = ap("characters", "Boss", "Boss 01.png")

            enemy_sprite = ap("characters", "Enemy", "Enemy 16-2.png")
            if not boss_made:

                boss = Boss("Boss", 4500, 3800, 3000, 150, 80, 175, boss_sprite,3)
                enemies.append(boss)
                boss_made = True
            if boss.is_dead():
                boss_defeated = True
                player.level_up(items)
                player.level_up(items)
                player.level_up(items)
                player.inventory.add_item(items[11]) ## same framework used for boss as miniboss just changed the stats and item added
            boss_num = random.randint(1, 100)
            if boss_num == 67:
                random_enemy = Enemy("support", random.randint(4178,4592), random.randint(3625, 4005), 500, 20, 10, 200, enemy_sprite)
                enemies.append(random_enemy) ## gives the boss a 1% chance to spawn a support enemy to make the fight more dynamic and interesting

        pygame.display.flip()