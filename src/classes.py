import pygame
import math

class Character:
    def __init__(self, name, x, y, hp_max, attack, defence, speed, spritesheet_path):
        self.name = name
        self.x = float(x)
        self.y = float(y)

        self.hp_max = int(hp_max)
        self.hp = int(hp_max)
        self.attack = int(attack)
        self.defence = int(defence)
        self.speed = float(speed)

        self.direction = "down"
        self.frames = self._load_frames(spritesheet_path)

        self.anim_time = 0.0
        self.anim_frame = 1  # standing frame (middle)

    def _load_frames(self, path):
        # expects 4 rows (down, left, right, up) and 3 cols
        sheet = pygame.image.load(path).convert_alpha()
        frames = {"down": [], "left": [], "right": [], "up": []}
        rows = ["down", "left", "right", "up"]

        for r, d in enumerate(rows):
            for c in range(3):
                frame = sheet.subsurface(pygame.Rect(c*32, r*32, 32, 32))
                frame = pygame.transform.scale(frame, (64, 64))
                frames[d].append(frame)
        return frames

    def rect(self):
        # smaller collision box (fits inside sprite)
        return pygame.Rect(int(self.x - 16), int(self.y - 16), 32, 32)

    def update_anim(self, dt, moving):
        if not moving:
            self.anim_frame = 1
            self.anim_time = 0.0
            return

        self.anim_time += dt
        if self.anim_time >= 0.15:
            self.anim_time = 0.0
            self.anim_frame = (self.anim_frame + 1) % 3

    def draw(self, surf, cam_x=0, cam_y=0):
        img = self.frames[self.direction][self.anim_frame]
        surf.blit(img, (int(self.x - 32 - cam_x), int(self.y - 32 - cam_y)))


class Player(Character):
    def move(self, dt, keys, controls, collides_fn):
        dash_mult = 2.0 if keys[controls["dash"]] else 1.0

        vx = 0
        vy = 0
        if keys[controls["move_left"]]:  vx -= 1
        if keys[controls["move_right"]]: vx += 1
        if keys[controls["move_up"]]:    vy -= 1
        if keys[controls["move_down"]]:  vy += 1

        moving = (vx != 0 or vy != 0)

        if moving:
            # direction selection for animation
            if abs(vx) > abs(vy):
                self.direction = "right" if vx > 0 else "left"
            else:
                self.direction = "down" if vy > 0 else "up"

            # normalize
            length = math.hypot(vx, vy)
            vx /= length
            vy /= length

            speed = self.speed * dash_mult

            old_x, old_y = self.x, self.y

            self.x += vx * speed * dt
            if collides_fn(self.rect()):
                self.x = old_x

            self.y += vy * speed * dt
            if collides_fn(self.rect()):
                self.y = old_y

        self.update_anim(dt, moving)

    def melee(self, keys, controls, surf, cam_x=0, cam_y=0):
        if keys[controls["attack"]]:
            pygame.draw.circle(
                surf, (255,255,0),
                (int(self.x - cam_x), int(self.y - cam_y)),
                20, 2
            )


class Enemy(Character):
    def __init__(self, *args):
        super().__init__(*args)
        self.tracking = False

    def track(self, player, dt, enemies, tracking_range=400, min_range=50):
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)

        self.tracking = (min_range < dist < tracking_range)
        if not self.tracking:
            self.update_anim(dt, False)
            return

        nx = dx / dist
        ny = dy / dist

        # separation (avoid stacking)
        sep_x, sep_y = 0.0, 0.0
        for other in enemies:
            if other is self:
                continue
            ox = self.x - other.x
            oy = self.y - other.y
            d2 = ox*ox + oy*oy
            if 0 < d2 < 90*90:
                d = math.sqrt(d2)
                strength = 1 - (d / 90.0)
                sep_x += (ox / d) * strength
                sep_y += (oy / d) * strength

        move_x = nx + sep_x
        move_y = ny + sep_y

        mag = math.hypot(move_x, move_y)
        if mag > 0:
            move_x /= mag
            move_y /= mag

        if abs(move_x) > abs(move_y):
            self.direction = "right" if move_x > 0 else "left"
        else:
            self.direction = "down" if move_y > 0 else "up"

        speed_factor = max(0.2, min(1.0, (tracking_range - dist) / tracking_range))

        self.x += move_x * self.speed * speed_factor * dt
        self.y += move_y * self.speed * speed_factor * dt

        self.update_anim(dt, True)
