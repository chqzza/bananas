import json
from classes import *
pygame.init()

items = []
img_folder = "assets/items/"

with open("config/items.json", "r") as f:
    data = json.load(f)

# --- Weapons ---
for w in data["weapons"]:
    items.append(
        Weapon(
            w["name"],
            w["category"],
            w["description"],    
            w["value"],
            w["power"],   
            w["range"],
            f"{img_folder}/{w['name']}.png"
        )
    )

# --- Armour ---
for a in data["armour"]:
    items.append(
        Armour(
            a["name"],
            a["category"],
            a["description"],    
            a["value"],
            a["defence"],      
            f"{img_folder}/{a['name']}.png"
        )
    )

# --- Consumables ---
for c in data["consumables"]:
    items.append(
        Consumable(
            c["name"],
            c["category"],
            c["effect"],
            c["value"],
            c["strength"],
            f"{img_folder}/{c['name']}.png"
        )
    )

# --- Quest Items ---
for q in data["quest_items"]:
    items.append(
        QuestItem(
            q["name"],
            q["category"],
            q["description"],
            q["quest"],
            f"{img_folder}/{q['name']}.png"
        )
    )



