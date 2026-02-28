import pygame
import os

# =========================
# CONFIG
# =========================
IMAGE_PATH = "assets/pets/gen1 sprites.png"

TILE_SIZE = 32
COLS_PER_POKEMON = 2
ROWS_PER_POKEMON = 4

BLOCK_WIDTH = TILE_SIZE * COLS_PER_POKEMON      # 64
BLOCK_HEIGHT = TILE_SIZE * ROWS_PER_POKEMON     # 128

OUTPUT_FOLDER = "pokemon_slices"

# =========================
# GEN 1 NATIONAL DEX ORDER
# =========================
pokemon_names = [
"Bulbasaur","Ivysaur","Venusaur - Male","Venusaur - Female", 
"Charmander","Charmeleon","Charizard",
"Squirtle","Wartortle","Blastoise",
"Caterpie","Metapod","Butterfree",
"Weedle","Kakuna","Beedrill",
"Pidgey","Pidgeotto","Pidgeot",
"Rattata","Raticate",
"Spearow","Fearow",
"Ekans","Arbok",
"Pikachu - Male", "Pikachu - Female","Raichu",
"Sandshrew","Sandslash",
"Nidoran_F","Nidorina","Nidoqueen",
"Nidoran_M","Nidorino","Nidoking",
"Clefairy","Clefable",
"Vulpix","Ninetales",
"Jigglypuff","Wigglytuff",
"Zubat","Golbat",
"Oddish","Gloom","Vileplume",
"Paras","Parasect",
"Venonat","Venomoth",
"Diglett","Dugtrio",
"Meowth","Persian",
"Psyduck","Golduck",
"Mankey","Primeape",
"Growlithe","Arcanine",
"Poliwag","Poliwhirl","Poliwrath",
"Abra","Kadabra","Alakazam",
"Machop","Machoke","Machamp",
"Bellsprout","Weepinbell","Victreebel",
"Tentacool","Tentacruel",
"Geodude","Graveler","Golem",
"Ponyta","Rapidash",
"Slowpoke","Slowbro",
"Magnemite","Magneton",
"Farfetchd",
"Doduo","Dodrio",
"Seel","Dewgong",
"Grimer","Muk",
"Shellder","Cloyster",
"Gastly","Haunter","Gengar",
"Onix",
"Drowzee","Hypno",
"Krabby","Kingler",
"Voltorb","Electrode",
"Exeggcute","Exeggutor",
"Cubone","Marowak",
"Hitmonlee","Hitmonchan",
"Lickitung",
"Koffing","Weezing",
"Rhyhorn","Rhydon",
"Chansey",
"Tangela",
"Kangaskhan",
"Horsea","Seadra",
"Goldeen","Seaking",
"Staryu","Starmie",
"MrMime",
"Scyther",
"Jynx",
"Electabuzz",
"Magmar",
"Pinsir",
"Tauros",
"Magikarp","Gyarados",
"Lapras",
"Ditto",
"Eevee","Vaporeon","Jolteon","Flareon",
"Porygon",
"Omanyte","Omastar",
"Kabuto","Kabutops",
"Aerodactyl",
"Snorlax",
"Articuno","Zapdos","Moltres",
"Dratini","Dragonair","Dragonite",
"Mewtwo","Mew"
]

# =========================

pygame.init()

sheet = pygame.image.load(IMAGE_PATH)
sheet_width, sheet_height = sheet.get_size()

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

pokemon_index = 0

for block_y in range(0, sheet_height, BLOCK_HEIGHT):
    for block_x in range(0, sheet_width, BLOCK_WIDTH):

        if pokemon_index >= len(pokemon_names):
            break

        block = pygame.Surface((BLOCK_WIDTH, BLOCK_HEIGHT), pygame.SRCALPHA)
        block.blit(sheet, (0, 0), (block_x, block_y, BLOCK_WIDTH, BLOCK_HEIGHT))

        if not block.get_bounding_rect().width:
            continue

        folder_name = pokemon_names[pokemon_index]
        poke_folder = os.path.join(OUTPUT_FOLDER, folder_name)
        os.makedirs(poke_folder, exist_ok=True)

        frame = 0

        for row in range(ROWS_PER_POKEMON):
            for col in range(COLS_PER_POKEMON):

                x = block_x + col * TILE_SIZE
                y = block_y + row * TILE_SIZE

                tile = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                tile.blit(sheet, (0, 0), (x, y, TILE_SIZE, TILE_SIZE))

                pygame.image.save(tile, os.path.join(poke_folder, f"frame_{frame}.png"))
                frame += 1

        pokemon_index += 1

print(f"Done. Extracted {pokemon_index} Pokémon.")