import pygame
import math
import random
global settings
pygame.init()



class Character:
    def __init__(self, name, x, y, hp_max, attack, defence, speed, spritesheet_path):
        self.name = name
        self.x = float(x)
        self.y = float(y)  ## used float for smooth movement, stopping movement being choppy 

        self.hp_max = int(hp_max)
        self.hp = int(hp_max)
        self.attack = int(attack)
        self.defence = int(defence) 
        self.speed = int(speed) ## used int for easier balancing and making performing calculations easier

        self.direction = "down" 
        self.frames = self._load_frames(spritesheet_path) ## starts with a default downwards facing character
                                                          ## and loads all the frames from the spritesheet

        self.anim_time = 0.0
        self.anim_frame = 1  ## there is 3 different frames, 1 is the standing frame, 0 and 2 are the walking frames

        self.pet = None ## the pet is stored here as it is defined seperately for the player and the enemy if it has one

    def _load_frames(self, path):
        ## expects 4 rows (down, left, right, up) and 3 cols
        sheet = pygame.image.load(path).convert_alpha()
        frames = {"down": [], "left": [], "right": [], "up": []}
        rows = ["down", "left", "right", "up"]

        for r, d in enumerate(rows): ## loops through the rows of the spreadsheet
            for c in range(3): ## each row has 3 frames - 0 to 2
                frame = sheet.subsurface(pygame.Rect(c*32, r*32, 32, 32)) ## the spritesheet is in 32x32 for every character
                frame = pygame.transform.scale(frame, (64, 64)) ## enlarge the frame to 64x64 for better visibility
                frames[d].append(frame)
        return frames
    


    def rect(self):
        
        return pygame.Rect(int(self.x -24), int(self.y - 30), 48, 60) ## the characters x and y is from center

    def update_anim(self, dt, moving):
        if not moving:
            self.anim_frame = 1 ## when the player isn't moving, the frame is the standing frame
            self.anim_time = 0.0
            return 

        self.anim_time += dt ## changes according to frame rate, so the animation speed is consistent regardless of fps
        if self.anim_time >= 0.15:
            self.anim_time = 0.0
            self.anim_frame = (self.anim_frame + 1) % 3 ## keeps in the limit of the 3 frames, and loops through them when moving
    
    def is_dead(self):

        return self.hp <= 0 ## returns true if hp <=0
    
    def draw(self, surf, cam_x=0, cam_y=0):
        if self.is_dead():
            return  # Don't draw if dead
        img = self.frames[self.direction][self.anim_frame] ## gets correct frame
        surf.blit(img, (int(self.x - 32 - cam_x), int(self.y - 32 - cam_y))) ## drawn from top left so adjusted for camera and x,y
        pygame.draw.rect(surf, (255,0,0), self.rect().move(-cam_x, -cam_y), 2)                                                             ## but pygame draws from top left so it is offset by half the size



class Player(Character):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) ## uses **kwargs to allow for more flexible arguments, passing as a dict

        self.attacking = False
        self.attack_frame = 0  ## sets the attacking frames to 0 - the neutral position
        self.attack_timer = 0
        self.attack_frames = []

        self.last_portal = None
        self.teleport_cooldown = 0 ## neutral cooldown for teleporting, so the player doesn't immediately teleport back after going through a portal


        self.projectiles = [] ## empty array for the projectiles on the map
        

        for i in range(5):
            img = pygame.image.load(f"assets/weapons/sprites/sword_{i}.png").convert_alpha()
            self.attack_frames.append(img)  ## every time the player attacks, it will loop through these frames for the animation

        self.inventory = Inventory() ## makes and empy inventory for the player to store items in
        self.hand = self.inventory.items[0] if self.inventory.items else None ## if there is an item in there somehow, it is held



    def move(self, dt, keys, controls, collides_fn, settings):
        dash_mult = settings["gameplay"]["player_dash_multiplier"] if keys[controls["dash"]] else 1.0 ## changes speed if player is sprinting

        vx, vy = 0, 0
        if keys[controls["move_left"]]:  vx -= 1
        if keys[controls["move_right"]]: vx += 1
        if keys[controls["move_up"]]:    vy -= 1
        if keys[controls["move_down"]]:  vy += 1 ## gets movement vector from keys pressed, passed in from a json

        moving = (vx != 0 or vy != 0) ## of there is any velocity, the player is moving

        if moving: ## only enters if moving
            ## Direction handling for animations
            if abs(vx) > abs(vy):
                self.direction = "right" if vx > 0 else "left"
            else:
                self.direction = "down" if vy > 0 else "up"

            ## Normalize vector using math function for diagonal movement
            length = math.hypot(vx, vy)
            if length > 0:
                vx /= length
                vy /= length

            speed = self.speed * dash_mult
            old_x, old_y = self.x, self.y ## stores old position for collision handling

            ## Movement with collision detection
            self.x += vx * speed * dt
            if collides_fn(self.rect()):
                self.x = old_x

            self.y += vy * speed * dt
            if collides_fn(self.rect()):
                self.y = old_y

        ## Update animation frame
        self.update_anim(dt, moving)
        
    def to_dict(self):
        return {
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "hp": self.hp,
            "hp_max": self.hp_max,
            "attack": self.attack,
            "defence": self.defence,
            "speed": self.speed,
            "gold": self.gold,
            "level": self.level,

            "inventory": [item.name for item in self.inventory.items]  ## takes all the data from the savegame json and turns it into a player
        }
    def from_dict(self, data):
        self.name = data.get("name", self.name)
        self.x = data.get("x", self.x)
        self.y = data.get("y", self.y)
        self.hp = data.get("hp", self.hp)
        self.hp_max = data.get("hp_max", self.hp_max)
        self.attack = data.get("attack", self.attack)
        self.defence = data.get("defence", self.defence)
        self.speed = data.get("speed", self.speed)
        self.gold = data.get("gold", getattr(self, "gold", 0))
        self.level = data.get("level", getattr(self, "level", 1))
        self.xp_next = int(100 * 1.12**self.level)
        inventory_names = data.get("inventory", []) ## writes all the data from the player back into the json
        
        return inventory_names ## returns just the names so they can be turned into the actual items in game loop
        
    def heal(self, keys, controls):
        if keys[controls["heal"]]:
            if self.inventory.items and self.hand.name == "Health Potion":
                self.hp = min(self.hp_max, self.hp + self.hand.strength) ## heals if health potion
                self.inventory.drop_item(self.inventory.items[0])
            if self.inventory.items and self.hand.name == "Strength Elixir":
                self.attack += self.hand.strength ## adds strength permanently
                self.inventory.drop_item(self.inventory.items[0])
        

    def take_damage(self, damage):
        reduction = self.defence / (self.defence + 100) ## simple formula for damage reduction, gives diminishing returns on defence for better balancing
        final_damage = damage * (1 - reduction)
        self.hp = max(0, self.hp - final_damage)

    def melee(self, keys, controls, enemies=None):

        if keys[controls["attack"]] and not self.attacking and self.hand and self.hand.item_type == "weapon" and self.hand.range == "melee":
            ## ensures it only enters if holding a melee weapon
            self.attacking = True
            self.attack_frame = 0
            self.attack_timer = 0
            
            ## Do hit detection immediately when attack starts
            radius = 32  ## melee range in pixels
            hit_rect = pygame.Rect(self.x, self.y, radius, radius)
            
            if enemies:
                for enemy in enemies:
                    if hit_rect.colliderect(enemy.rect()):
                        enemy.take_damage(self)

    def ranged(self, keys, controls):
        if keys[controls["attack"]] and not self.attacking and self.hand and self.hand.item_type == "weapon" and self.hand.range == "ranged":
            ## ensures it only enters if holding a ranged weapon
            self.attacking = True
            self.attack_frame = 0
            self.attack_timer = 0

            projectile = {
                "rect": pygame.Rect(self.x, self.y, 10, 10),
                "direction": self.direction,
                "speed": 600  # pixels per second
            }
            ## creates a projectile with a rect for collision detection with enemies and adds it to the players projectiles
            self.projectiles.append(projectile)
    def update_projectiles(self, dt, enemies):
        for projectile in self.projectiles[:]:  ## copy list to safely remove
        
            move_amount = projectile["speed"] * dt

            if projectile["direction"] == "up":
                projectile["rect"].y -= move_amount
            elif projectile["direction"] == "down":
                projectile["rect"].y += move_amount
            elif projectile["direction"] == "left":
                projectile["rect"].x -= move_amount
            elif projectile["direction"] == "right":
                projectile["rect"].x += move_amount

        ## Remove if off screen
            if (projectile["rect"].x < 0 or
                projectile["rect"].x > 10000 or
                projectile["rect"].y < 0 or
                projectile["rect"].y > 20000):
                self.projectiles.remove(projectile)
                continue

            ## Collision check with enemies
            if enemies:
                for enemy in enemies:
                    if projectile["rect"].colliderect(enemy.rect()):
                        enemy.take_damage(self)
                        self.projectiles.remove(projectile)
                        break
    def draw_projectiles(self, screen, cam_x, cam_y):
        for projectile in self.projectiles:
            draw_rect = pygame.Rect(
                projectile["rect"].x - cam_x,
                projectile["rect"].y - cam_y,
                projectile["rect"].width,
                projectile["rect"].height
            ) ## centers the projectile rect on the projectile and adjusts accordinglt for camera
            pygame.draw.rect(screen, (255, 0, 0), draw_rect)
    def update_attack(self, dt):

        if self.attacking:
            self.attack_timer += dt
            frame_duration = 0.03  # 30ms per frame
            
            if self.attack_timer >= frame_duration:
                self.attack_timer = 0
                self.attack_frame += 1
                
                if self.attack_frame >= len(self.attack_frames):
                    self.attacking = False
                    self.attack_frame = 0 ## returns back to first frame of attacking
    
    def draw(self, surf, cam_x, cam_y):

        ## Draw player sprite (call parent class draw if it exists)
        super().draw(surf, cam_x, cam_y)
        
        ## Draw attack animation if attacking
        if self.attacking and self.attack_frame < len(self.attack_frames):
            frame = self.attack_frames[self.attack_frame]
            cx = int(self.x - cam_x)
            cy = int(self.y - cam_y)
            surf.blit(frame, (cx - frame.get_width()//2, cy - frame.get_height()//2))

    def level_up(self, items):
        self.level += 1
        self.xp = 0
        self.xp_next = int(self.xp_next * 1.12**self.level) ## uses exponential growth for xp to make levelling harder
        self.hp_max += 10
        self.attack += 10
        self.defence += 50
        self.hp = min(self.hp_max, self.hp + 15) ## updates all stats to give clear progression through leveling
        if self.level % 5 == 0:
            number = random.randint(1, 100)
            if number <= 70:
                self.inventory.add_item(items[7])
            elif number >= 80:
                self.inventory.add_item(items[9]) ## adds either a health potion or strength elixir every 5th level

    def equip_armour(self, keys, controls):
        if keys[controls["use"]]:
            if self.hand and self.hand.item_type == "armour":
                self.defence += self.hand.defence
                self.inventory.drop_item(self.hand)
                ##simple method for equipping armour, adds defence and stacks onto past armour
class Enemy(Character):
    def __init__(self, *args):
        super().__init__(*args)
        self.tracking = False
        self.range = 40                 ## Attack reach distance (pixels)
        self.attack_damage = 8          ## Damage per hit
        self.attack_cooldown = 1.0      ## Seconds between attacks
        self.attack_timer = 0.0         ## Tracks cooldown timer

    def take_damage(self, player):
        ##scales damage based off players attack and enemy defence
        amount = max(5, (2*player.attack + player.hand.power - self.defence)/10) ## basic damage formula, can be improved with different enemy types and weaknesses

        if player.hand and player.hand.item_type == "weapon" and player.hand.range == "melee":
            amount *= (1 + player.hand.power / 100) ## melee weapons increase damage

        elif player.hand and player.hand.item_type == "weapon" and player.hand.range == "ranged":
            amount *= (1 - player.hand.power / 200)   ## ranged weapons do less damage but have more utility

        if amount > 0:
            self.hp = min(self.hp - amount, self.hp_max) ## reduces hp by the damage amount, ensuring it doesn't go below 0


    def perform_attack(self, player, dt, distance):
        
        self.attack_timer -= dt ## reduces attack timer by the time since last frame
        if distance <= self.range and self.attack_timer <= 0: 
            player.take_damage(self.attack_damage)
            self.attack_timer = self.attack_cooldown ## resets attack timer after attacking

    def draw_health_bar(self, surf, cam_x=0, cam_y=0):
        if not self.is_dead():
            ##Displays small HP bar above the enemy.
            bar_width = 30
            bar_height = 5
            x = int(self.x - cam_x - bar_width / 2)
            y = int(self.y - cam_y - 40)

            ratio = self.hp / self.hp_max if self.hp_max > 0 else 0
            fill_width = int(bar_width * ratio) ## scales the fill width according to the hp ratio

            pygame.draw.rect(surf, (150, 0, 0), (x, y, bar_width, bar_height))      ## background
            pygame.draw.rect(surf, (0, 255, 0), (x, y, fill_width, bar_height))    ## green fill
            pygame.draw.rect(surf, (255, 255, 255), (x, y, bar_width, bar_height), 1)  ## outline

    def track(self, player, dt, enemies,collides_fn, tracking_range=400, min_range=50):
        ##Basic enemy tracking ai
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)

        ## Attack when in range
        self.perform_attack(player, dt, dist)

        self.tracking = (min_range < dist < tracking_range)
        if not self.tracking:
            self.update_anim(dt, False)
            return

        nx = dx / dist
        ny = dy / dist ## normalized vectors for movement

        ## seperation from other enemies to prevent stacking
        sep_x, sep_y = 0.0, 0.0
        for other in enemies:
            if other is self:
                continue
            ox = self.x - other.x
            oy = self.y - other.y ## distances to other enemies
            d2 = ox ** 2 + oy ** 2
            if 0 < d2 < 8100:  ## if they are closer than 90 pixels, apply separation
                d = math.sqrt(d2)
                strength = 1 - (d / 90.0)
                sep_x += (ox / d) * strength
                sep_y += (oy / d) * strength

        move_x = nx + sep_x
        move_y = ny + sep_y ## combines the tracking vector and separation vector

        mag = math.hypot(move_x, move_y)
        if mag > 0:
            move_x /= mag
            move_y /= mag ## re normalizes the movement vector

        ## Direction for animation
        if abs(move_x) > abs(move_y):
            self.direction = "right" if move_x > 0 else "left"
        else:
            self.direction = "down" if move_y > 0 else "up"
        ## Movement speed factor (slower when far)

        speed_factor = max(0.2, min(1.0, (tracking_range - dist) / tracking_range))


        old_x, old_y = self.x, self.y ## stores old position for collision handling
        self.x += move_x * self.speed * speed_factor * dt
        if collides_fn(self.rect()):
            self.x = old_x 

        self.y += move_y * self.speed * speed_factor * dt
        if collides_fn(self.rect()):
            self.y = old_y
            self.update_anim(dt, True)
            ## can move horizontally and vertically separately to prevent getting stuck on corners

class Boss(Enemy):
    def __init__(self, name, x, y, hp_max, attack, defence, speed, spritesheet_path, boss_index):
        super().__init__(name, x, y, hp_max, attack, defence, speed, spritesheet_path)

        self.boss_index = boss_index  # 0, 1, or 2
        self.frames = self.load_boss_frames(spritesheet_path)
        self.anim_time = 0.0
        self.anim_frame = 0

    def load_boss_frames(self, path):
        sheet = pygame.image.load(path).convert_alpha()
        frames = []

        frame_size = 96  # change if needed

        row = self.boss_index  # which boss row to use

        for col in range(3):  # 3 frames
            frame = sheet.subsurface(
                pygame.Rect(col * frame_size, row * frame_size, frame_size, frame_size)
            )
            if self.name == "Mini Boss":
                frame = pygame.transform.scale(frame, (120, 120))  # bosses bigger
            else:
                frame = pygame.transform.scale(frame, (150, 150))  # bosses bigger
            frames.append(frame)

        return frames
    def rect(self):
        width = 140
        height = 160
    
        return pygame.Rect(
            int(self.x - width // 2),
            int(self.y - height // 2),
            width,
            height
        )
    def update_anim(self, dt, is_moving):
        self.anim_time += dt
        if self.anim_time >= 0.2:
            self.anim_time = 0
            self.anim_frame = (self.anim_frame + 1) % 3

    def boss_draw(self, surf, cam_x=0, cam_y=0):
        if self.is_dead():
            return

        img = self.frames[self.anim_frame]
        surf.blit(
            img,
            (int(self.x - img.get_width()//2 - cam_x),
             int(self.y - img.get_height()//2 - cam_y))
        )
class Item:
    def __init__(self, name, item_type, sub_type, effect, value, image_path):
        self.name = name
        self.item_type = item_type
        self.sub_type = sub_type
        self.effect = effect
        self.value = value ## when items are defined in the json, all of these attributes are passed in
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (64, 64)) ## all items are scaled to 64x64 for consistency and visibility

    def draw(self, surf, x, y, cam_x, cam_y):
        surf.blit(self.image, (x - cam_x, y - cam_y)) ## simple drawing for items on the ground

    def pickup(self, player, location, items, locations, keys, controls): ##location is the items location, locations stores all places they spawn
        region = pygame.Rect(location[0], location[1] , 64, 64)
        if keys[controls["use"]]:
            if region.collidepoint(player.x, player.y): ## checks if player is over the item
                if  player.inventory.add_item(self):
                    items.remove(self)
                    locations.remove(location)
                    return items, locations
        return items, locations ## if an item is picked up the items and locations arrays are updated

class Weapon(Item):
    def __init__(self, name, sub_type, effect, value, power, range_weapon, image_path):
        super().__init__(name, "weapon", sub_type, effect, value, image_path)
        self.power = power
        self.range = range_weapon

class Armour(Item):
    def __init__(self, name, sub_type, effect, value, defence, image_path):
        super().__init__(name, "armour", sub_type, effect, value, image_path)
        self.defence = defence

class Consumable(Item):
    def __init__(self, name, sub_type, effect, value, strength, image_path):
        super().__init__(name, "consumable", sub_type, effect, value, image_path)
        self.strength = strength

class QuestItem(Item):
    def __init__(self, name, sub_type, effect, quest, image_path):
        super().__init__(name, "quest_item", sub_type, effect, 0, image_path)
        self.quest = quest
## all items have one or more extra attributes depending on the type

class Pet:
    def __init__(self, player, name):
        self.x, self.y = self.update_position(player)
        self.frames, self.up_frames, self.left_frames, self.down_frames, self.right_frames = self.load_frames(name) ## to match how the sprite folder is built
        self.name = name
        self.direction = "down" ## starts default facing down as the player does also
        self.anim_frame = 0
        self.anim_time = 0.0
        self.effect = None ## the effect of the pet is defined when it is summoned, and can be changed by different pets,
                           ##such as healing or attacking with the player
        self.strength = None ## the strength of the pets effect, for example how much it heals or how much damage it does,
                             ##is defined here and can be changed by different pets

    def load_frames(self, name):
        path = f"assets/pets/pokemon_slices/{name}" ## used a set asset folder full of downloaded sprites
        frames = []


        for i in range(8): ## each pokemon folder has 8 frames, 4 directions
            img = pygame.image.load(f"{path}/frame_{i}.png").convert_alpha()
            frames.append(img)
        return frames, (frames[0], frames[2]), (frames[1], frames[3]), (frames[4], frames[6]), (frames[5], frames[7]) 
    ## in 2x4 grid going across it goes, up  left up left down right down right 

    
    def update_position(self, player):
        if player.direction == "down":
            x = player.x
            y = player.y - 50
            self.direction = "down"
        elif player.direction == "up":
            x = player.x
            y = player.y + 50
            self.direction = "up"
        elif player.direction == "left":
            x = player.x + 50
            y = player.y
            self.direction = "left"
        elif player.direction == "right":
            x = player.x - 50
            y = player.y
            self.direction = "right"
            ## uses 50 to stop the player and pet sprites from overlapping
        return (x, y)
    
    def draw(self, surf, cam_x, cam_y):
        if self.direction == "down":
            frames = self.down_frames
        elif self.direction == "up":
            frames = self.up_frames
        elif self.direction == "left":
            frames = self.left_frames
        elif self.direction == "right":
            frames = self.right_frames

        img = frames[self.anim_frame // 10 % 2]
        img = pygame.transform.scale(img, (64, 64))
        surf.blit(img, (int(self.x - cam_x - img.get_width()//2), int(self.y - cam_y - img.get_height()//2))) ## same way all other sprites are displayed

    def update_pet(self, player, surf, cam_x, cam_y):
        
        self.x, self.y = self.update_position(player)
        self.draw(surf, cam_x, cam_y)
        self.anim_frame+=1
        ##grouped update method

class Region:
    def __init__(self, x1, x2, y1, y2):
        self.rect = (x1, x2, y1, y2)

    def contains(self, x, y):
        x1, x2, y1, y2 = self.rect
        return x1 <= x <= x2 and y1 <= y <= y2
    ## defines the basic region class which is applied for anything interactable


class Portal(Region):
    def __init__(self, portal_id, x1, x2, y1, y2, target_x, target_y, key):
        super().__init__(x1, x2, y1, y2)
        self.id = portal_id
        self.target = (target_x, target_y)
        self.key = key
## portal class telports the player to a target location, handled in game loop
class Sign(Region):
    def __init__(self, x1, x2, y1, y2, message):
        super().__init__(x1, x2, y1, y2)
        self.message = message ## simple message
        
    def write_message(self, screen, font):
        sw, sh = screen.get_size()

        ## message box settings
        box_width = 800
        box_height = 400
        padding = 20

        box_x = (sw - box_width) // 2
        box_y = sh - box_height - 40

        ## Semi-transparent background
        box_surface = pygame.Surface((box_width, box_height))
        box_surface.set_alpha(220)
        box_surface.fill((30, 30, 30))

        screen.blit(box_surface, (box_x, box_y))

        ## Border
        pygame.draw.rect(screen, (255, 255, 255), (box_x, box_y, box_width, box_height), 3)

        ## Warping text to fit in the box
        words = self.message.split(" ")
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + word + " "
            if font.size(test_line)[0] < box_width - padding * 2:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "

        lines.append(current_line)

        ## Render lines centered
        y_offset = box_y + padding
        for line in lines:
            text_surface = font.render(line.strip(), True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(sw // 2, y_offset + text_surface.get_height() // 2))
            screen.blit(text_surface, text_rect)
            y_offset += text_surface.get_height() + 5

class NPC(Sign):
    def __init__(self, x1, x2, y1, y2, message, image_path, name):
        super().__init__(x1, x2, y1, y2, message)
        self.name = name
        self.image = pygame.image.load(image_path).convert_alpha() ## NPC is a sublass of sign as they only differ in that they have a sprite

    def draw(self, surf, cam_x, cam_y):
        surf.blit(self.image, (self.rect[0] - cam_x, self.rect[2] - cam_y)) ## draws the npc sprite at its location


class Inventory:
    def __init__(self):
        self.items = []
        self.capacity = 20 ## the players inventory has a max of 20

    def add_item(self, item):
        if len(self.items) < self.capacity:
            self.items.append(item)
            return True
        return False ## simple method for adding items, checks if there is space in the inventory first
    
    def drop_item(self, item):
        if item in self.items:
            self.items.remove(item)
            return True
        return False ## simple method for dropping items, checks if the item is in the inventory first
    