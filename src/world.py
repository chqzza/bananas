import pygame
import pytmx
from classes import Character
class World:
    def __init__(self, tmx_path):
        self.tmx = pytmx.load_pygame(tmx_path)
        self.tile_w = self.tmx.tilewidth
        self.tile_h = self.tmx.tileheight

        self.width_px = self.tmx.width * self.tile_w
        self.height_px = self.tmx.height * self.tile_h

        self.collision_rects = []
        self._load_collisions()

    def _load_collisions(self):
        for layer in self.tmx.layers:
            if getattr(layer, "name", None) == "Collisions":
                for obj in layer:
                    # These attributes only exist on Object Layers
                    x = int(obj.x)
                    y = int(obj.y)
                    w = int(obj.width)
                    h = int(obj.height)

                    if w > 0 and h > 0:
                        self.collision_rects.append(pygame.Rect(x, y, w, h))



    def draw(self, surf, cam_x=0, cam_y=0, player=None):
        sw, sh = surf.get_size()

        start_x = max(0, cam_x // self.tile_w)
        start_y = max(0, cam_y // self.tile_h)

        end_x = min(self.tmx.width, (cam_x + sw) // self.tile_w + 2)
        end_y = min(self.tmx.height, (cam_y + sh) // self.tile_h + 2)

        for layer in self.tmx.visible_layers:
            if 'bg' in getattr(layer, "name", "").lower():
                if isinstance(layer, pytmx.TiledTileLayer):
                    for y in range(start_y, end_y):
                        for x in range(start_x, end_x):
                            gid = layer.data[y][x]
                            if gid:
                                tile = self.tmx.get_tile_image_by_gid(gid)
                                if tile:
                                    surf.blit(tile, (x*self.tile_w - cam_x, y*self.tile_h - cam_y))

        player.draw(surf, cam_x, cam_y)
        player.pet.update_pet(player, surf, cam_x, cam_y)      
        
        for layer in self.tmx.visible_layers:
            if 'fg' in getattr(layer, "name", "").lower():
                if isinstance(layer, pytmx.TiledTileLayer):
                    for y in range(start_y, end_y):
                        for x in range(start_x, end_x):
                            gid = layer.data[y][x]
                            if gid:
                                tile = self.tmx.get_tile_image_by_gid(gid)
                                if tile:
                                    surf.blit(tile, (x*self.tile_w - cam_x, y*self.tile_h - cam_y))

    def collides(self, rect: pygame.Rect):
        
        if not self.collision_rects:
            return False
        return any(rect.colliderect(c) for c in self.collision_rects)
