#!/usr/bin/env python3
"""
Tiled JSON map exporter for the BarScene.

Exports the BarScene MAP array as a Tiled-compatible .tmj file that can be
opened and edited in the Tiled map editor (https://www.mapeditor.org/).

The map uses three tile layers and a Tiled external tileset reference:
  - "Floor"  — wood floor (tile 0 in game = GID 1)
  - "Walls"  — brick walls (tile 1 in game = GID 2)
  - "Props"  — bar counter (tile 2 in game = GID 3) + prop object layer

Tile GIDs (1-based, Tiled convention):
    1 → wood_floor
    2 → brick_wall
    3 → wooden_bar  (bar counter top)

An embedded tileset is written into the TMJ so Tiled can resolve tile images
without needing a separate .tsx file.  The tile images are expected at
  ../../public/assets/sprites/<name>.png
relative to this script.

Output:
    ../../public/assets/maps/bar_scene.tmj   (Tiled map file)

Usage:
    python export_tiled_map.py
"""

import json
import os

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT   = os.path.abspath(os.path.join(_SCRIPT_DIR, "..", ".."))
MAPS_DIR     = os.path.join(_REPO_ROOT, "public", "assets", "maps")

OUTPUT_FILE = os.path.join(MAPS_DIR, "bar_scene.tmj")

# ---------------------------------------------------------------------------
# MAP DATA  (mirrors BarScene.ts MAP constant exactly)
# 0 = wood floor  |  1 = brick wall  |  2 = bar counter
# ---------------------------------------------------------------------------
MAP_W = 11
MAP_H = 20
TILE_W = 32
TILE_H = 32

MAP: list[list[int]] = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # row  0 — north wall
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # row  1 — behind-bar floor (N)
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # row  2 — bartender zone
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # row  3 — walkthrough to/from bar ends
    [1, 0, 2, 2, 2, 2, 2, 2, 2, 0, 1],  # row  4 — bar counter (cols 2-8)
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # row  5 — bar front-face zone
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # row  6
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # row  7
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # row  8  ← bat pickup
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # row  9
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # row 10
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # row 11
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # row 12 ← player start
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # row 13
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # row 14
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # row 15
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # row 16
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # row 17
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # row 18
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # row 19 — south wall
]

# Tile value → Tiled GID mapping (GIDs are 1-based)
GAME_TILE_TO_GID = {
    0: 1,   # wood floor  → GID 1
    1: 2,   # brick wall  → GID 2
    2: 3,   # bar counter → GID 3
}

# ---------------------------------------------------------------------------
# TILESET DEFINITION (embedded in the TMJ)
# Relative path from the TMJ file location to the sprite PNGs.
# ---------------------------------------------------------------------------
SPRITE_REL = "../../public/assets/sprites"
# Path from the maps/ directory back to sprites/
IMG_PATH_REL = "../sprites"

EMBEDDED_TILESET = {
    "columns":     3,
    "firstgid":    1,
    "image":       f"{IMG_PATH_REL}/bar_tileset.png",
    "imageheight": 32,
    "imagewidth":  96,
    "margin":      0,
    "name":        "BarTiles",
    "spacing":     0,
    "tilecount":   3,
    "tileheight":  TILE_H,
    "tilewidth":   TILE_W,
    # Tile properties: individual source images for reference
    "tiles": [
        {
            "id": 0,
            "image": f"{IMG_PATH_REL}/wood_floor.png",
            "imageheight": 32,
            "imagewidth": 32,
            "properties": [
                {"name": "collision", "type": "bool", "value": False},
                {"name": "game_tile_id", "type": "int", "value": 0},
                {"name": "texture_key", "type": "string", "value": "wood_floor"},
            ]
        },
        {
            "id": 1,
            "image": f"{IMG_PATH_REL}/brick_wall.png",
            "imageheight": 32,
            "imagewidth": 32,
            "properties": [
                {"name": "collision", "type": "bool", "value": True},
                {"name": "game_tile_id", "type": "int", "value": 1},
                {"name": "texture_key", "type": "string", "value": "brick_wall"},
            ]
        },
        {
            "id": 2,
            "image": f"{IMG_PATH_REL}/wooden_bar.png",
            "imageheight": 32,
            "imagewidth": 32,
            "properties": [
                {"name": "collision", "type": "bool", "value": True},
                {"name": "game_tile_id", "type": "int", "value": 2},
                {"name": "texture_key", "type": "string", "value": "wooden_bar"},
            ]
        },
    ],
    "type": "tileset",
}

# ---------------------------------------------------------------------------
# LAYER BUILDERS
# ---------------------------------------------------------------------------

def _flat_gid_data(tile_value: int | None) -> list[int]:
    """
    Build a flat row-major list of GIDs for a layer that only contains one
    tile type.  Pass None to get an all-zero (empty) layer.
    """
    gid = GAME_TILE_TO_GID.get(tile_value, 0) if tile_value is not None else 0
    return [gid] * (MAP_W * MAP_H)


def _floor_layer_data() -> list[int]:
    """GID map: every cell = wood_floor (GID 1) — serves as the base layer."""
    return [GAME_TILE_TO_GID[0]] * (MAP_W * MAP_H)


def _wall_layer_data() -> list[int]:
    """GID map: brick wall tiles only; 0 elsewhere."""
    data = []
    for row in MAP:
        for cell in row:
            data.append(GAME_TILE_TO_GID[1] if cell == 1 else 0)
    return data


def _bar_layer_data() -> list[int]:
    """GID map: bar counter tiles only; 0 elsewhere."""
    data = []
    for row in MAP:
        for cell in row:
            data.append(GAME_TILE_TO_GID[2] if cell == 2 else 0)
    return data


def _make_tile_layer(name: str, layer_id: int, data: list[int]) -> dict:
    return {
        "data":    data,
        "height":  MAP_H,
        "id":      layer_id,
        "name":    name,
        "opacity": 1,
        "type":    "tilelayer",
        "visible": True,
        "width":   MAP_W,
        "x":       0,
        "y":       0,
    }


# ---------------------------------------------------------------------------
# OBJECT LAYER  (spawn points, interaction zones)
# ---------------------------------------------------------------------------

def _make_object_layer() -> dict:
    """Return a Tiled object layer with spawn/prop markers."""
    objects = [
        {
            "id":     1,
            "name":   "PlayerStart",
            "type":   "spawn",
            "x":      5 * TILE_W,
            "y":      12 * TILE_H,
            "width":  TILE_W,
            "height": TILE_H,
            "visible": True,
            "rotation": 0,
            "properties": [
                {"name": "entity", "type": "string", "value": "player"}
            ]
        },
        {
            "id":     2,
            "name":   "BartenderSpawn",
            "type":   "spawn",
            "x":      5 * TILE_W,
            "y":      2 * TILE_H,
            "width":  TILE_W,
            "height": TILE_H,
            "visible": True,
            "rotation": 0,
            "properties": [
                {"name": "entity", "type": "string", "value": "demon_bartender"}
            ]
        },
        {
            "id":     3,
            "name":   "BatPickup",
            "type":   "pickup",
            "x":      5 * TILE_W,
            "y":      8 * TILE_H,
            "width":  TILE_W,
            "height": TILE_H,
            "visible": True,
            "rotation": 0,
            "properties": [
                {"name": "item", "type": "string", "value": "weapon_bat"}
            ]
        },
        # Bottle decorations on bar counter
        {
            "id":     4,
            "name":   "Bottle_Whiskey",
            "type":   "prop",
            "x":      3 * TILE_W,
            "y":      4 * TILE_H,
            "width":  TILE_W,
            "height": TILE_H,
            "visible": True,
            "rotation": 0,
            "properties": [
                {"name": "sprite", "type": "string", "value": "alcohol_bottles"},
                {"name": "frame",  "type": "int",    "value": 0}
            ]
        },
        {
            "id":     5,
            "name":   "Bottle_Beer",
            "type":   "prop",
            "x":      4 * TILE_W,
            "y":      4 * TILE_H,
            "width":  TILE_W,
            "height": TILE_H,
            "visible": True,
            "rotation": 0,
            "properties": [
                {"name": "sprite", "type": "string", "value": "alcohol_bottles"},
                {"name": "frame",  "type": "int",    "value": 3}
            ]
        },
        {
            "id":     6,
            "name":   "Bottle_Wine",
            "type":   "prop",
            "x":      6 * TILE_W,
            "y":      4 * TILE_H,
            "width":  TILE_W,
            "height": TILE_H,
            "visible": True,
            "rotation": 0,
            "properties": [
                {"name": "sprite", "type": "string", "value": "alcohol_bottles"},
                {"name": "frame",  "type": "int",    "value": 1}
            ]
        },
        {
            "id":     7,
            "name":   "Bottle_Gin",
            "type":   "prop",
            "x":      7 * TILE_W,
            "y":      4 * TILE_H,
            "width":  TILE_W,
            "height": TILE_H,
            "visible": True,
            "rotation": 0,
            "properties": [
                {"name": "sprite", "type": "string", "value": "alcohol_bottles"},
                {"name": "frame",  "type": "int",    "value": 2}
            ]
        },
    ]

    return {
        "draworder": "topdown",
        "id":        10,
        "name":      "Objects",
        "objects":   objects,
        "opacity":   1,
        "type":      "objectgroup",
        "visible":   True,
        "x":         0,
        "y":         0,
    }


# ---------------------------------------------------------------------------
# FULL TMJ DOCUMENT
# ---------------------------------------------------------------------------

def build_tmj() -> dict:
    floor_layer = _make_tile_layer("Floor", 1, _floor_layer_data())
    wall_layer  = _make_tile_layer("Walls", 2, _wall_layer_data())
    bar_layer   = _make_tile_layer("Props", 3, _bar_layer_data())
    obj_layer   = _make_object_layer()

    return {
        "compressionlevel": -1,
        "editorsettings": {
            "export": {
                "format": "json",
                "target": "bar_scene.tmj"
            }
        },
        "height":      MAP_H,
        "infinite":    False,
        "layers":      [floor_layer, wall_layer, bar_layer, obj_layer],
        "nextlayerid": 11,
        "nextobjectid": 20,
        "orientation": "orthogonal",
        "renderorder": "right-down",
        "tiledversion": "1.10.2",
        "tileheight":  TILE_H,
        "tilesets":    [EMBEDDED_TILESET],
        "tilewidth":   TILE_W,
        "type":        "map",
        "version":     "1.10",
        "width":       MAP_W,
        # Map-level custom properties
        "properties": [
            {"name": "scene",         "type": "string", "value": "BarScene"},
            {"name": "cam_zoom",      "type": "float",  "value": 2.0},
            {"name": "room_offset_x", "type": "int",    "value": 0,
             "comment": "Set to ROOM_X computed from GAME_WIDTH at runtime"},
        ],
    }


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    os.makedirs(MAPS_DIR, exist_ok=True)

    tmj = build_tmj()

    with open(OUTPUT_FILE, "w") as f:
        json.dump(tmj, f, indent=2)

    print(f"  Tiled map  : {OUTPUT_FILE}")
    print(f"  Map size   : {MAP_W}×{MAP_H} tiles  ({MAP_W*TILE_W}×{MAP_H*TILE_H} px)")
    print(f"  Layers     : Floor, Walls, Props, Objects")
    print()
    print("  Open bar_scene.tmj in Tiled (https://www.mapeditor.org/) to edit the map.")
    print("  Tile GIDs: 1=wood_floor  2=brick_wall  3=wooden_bar")
    print()
    print("  NOTE: The tileset references individual tile images via the 'tiles'")
    print("  property list.  If Tiled asks for a combined tileset image, run:")
    print("    python export_tiled_map.py --make-tileset")
    print("  to generate bar_tileset.png (96×32, 3 tiles side by side).")
    print()

    # ------------------------------------------------------------------
    # Optional: generate a combined tileset PNG so Tiled has a single
    # image to display in its tileset panel.
    # ------------------------------------------------------------------
    import sys
    if "--make-tileset" in sys.argv:
        try:
            from PIL import Image as _Image
            import generate_brick_wall, generate_wood_floor, generate_wooden_bar  # type: ignore

            ts = _Image.new("RGBA", (96, 32), (0, 0, 0, 0))
            ts.paste(generate_wood_floor.generate(),  (0,  0))
            ts.paste(generate_brick_wall.generate(),  (32, 0))
            ts.paste(generate_wooden_bar.generate(),  (64, 0))

            tileset_path = os.path.join(
                _REPO_ROOT, "public", "assets", "sprites", "bar_tileset.png"
            )
            ts.save(tileset_path)
            print(f"  Tileset PNG: {tileset_path}  (96×32)")
        except ImportError as e:
            print(f"  Warning: could not generate tileset PNG — {e}")
