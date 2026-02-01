import json
import os
import pygame

SETTINGS_PATH = "config/settings.json"
ASSETS = "assets"

def ap(*parts):
    return os.path.join(ASSETS, *parts)

def load_settings():
    with open(SETTINGS_PATH, "r") as f:
        return json.load(f)

def save_settings(settings):
    with open(SETTINGS_PATH, "w") as f:
        json.dump(settings, f, indent=2)

def key_from_string(key_name: str):
    return getattr(pygame, key_name)

def build_controls(settings: dict):
    c = settings["controls"]
    return {name: key_from_string(value) for name, value in c.items()}

def make_screen(settings):
    w, h = settings["video"]["resolution"]
    fullscreen = settings["video"].get("fullscreen", False)
    flags = pygame.FULLSCREEN if fullscreen else 0
    return pygame.display.set_mode((w, h), flags)
