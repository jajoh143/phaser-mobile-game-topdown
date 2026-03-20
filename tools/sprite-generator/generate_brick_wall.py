#!/usr/bin/env python3
"""
Brick wall tile generator for Phaser 3.

Generates a 32x32 seamlessly tileable pixel-art brick wall texture
with a dark, moody bar-scene aesthetic. Single static frame.

Output:
    generated/brick_wall.png
    generated/brick_wall.json
    public/assets/sprites/brick_wall.png

Usage:
    python generate_brick_wall.py
"""

import json
import os
from PIL import Image

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT   = os.path.abspath(os.path.join(_SCRIPT_DIR, "..", ".."))

OUTPUT_DIR  = os.path.join(_SCRIPT_DIR, "generated")
PUBLIC_DIR  = os.path.join(_REPO_ROOT, "public", "assets", "sprites")

IMAGE_FILE = "brick_wall.png"
JSON_FILE  = "brick_wall.json"

SIZE = 32

# ---------------------------------------------------------------------------
# PALETTE  — dark, moody bar-scene brick
# ---------------------------------------------------------------------------
MORTAR       = (28, 22, 20, 255)   # very dark grout between bricks
BRICK_BASE   = (98, 42, 30, 255)   # deep red-brown brick face
BRICK_DARK   = (72, 28, 18, 255)   # shadow face / lower brick edge
BRICK_MID    = (115, 52, 36, 255)  # mid tone variation
BRICK_LIGHT  = (138, 68, 46, 255)  # highlight face / upper brick edge
BRICK_SPECK  = (82, 36, 24, 255)   # subtle surface variation speck

# ---------------------------------------------------------------------------
# BRICK LAYOUT  (staggered 2-row repeat, seamless on 32px)
#
#  Each brick is  8px wide × 4px tall (face only, mortar included).
#  Mortar thickness: 1px on bottom, 1px on right side.
#  Row height: 4px  (3px face + 1px mortar below)
#  Brick width: 8px (7px face + 1px mortar right)
#
#  32 / 4 = 8 rows
#  Even rows offset = 0, odd rows offset = 4 (half-brick stagger)
#
#  This tiles seamlessly because:
#   - 8 rows × 4px = 32px height (exact fit)
#   - 4 bricks × 8px = 32px width (exact fit, offsets wrap cleanly)
# ---------------------------------------------------------------------------

def _brick_color(bx: int, by: int, px: int, py: int) -> tuple:
    """
    Return the RGBA colour for pixel (px, py) within a brick cell whose
    top-left corner in tile space is (bx, by).

    px, py are local coordinates inside the 8x4 brick cell.
    The cell includes 1px mortar on the right (px == 7) and
    1px mortar on the bottom (py == 3).
    """
    # Mortar pixels
    if px == 7 or py == 3:
        return MORTAR

    # Face: py is 0-2, px is 0-6
    # Top highlight row (py == 0)
    if py == 0:
        # left corner highlight pixel
        if px == 0:
            return BRICK_LIGHT
        return BRICK_LIGHT

    # Bottom shadow row (py == 2)
    if py == 2:
        if px == 6:
            return BRICK_DARK
        return BRICK_DARK

    # Middle row (py == 1) — main face colour with subtle variation
    # Use brick position hash for surface variation
    variation = (bx * 7 + by * 13) % 5
    if variation == 0:
        return BRICK_MID
    elif variation == 1:
        # small speckling on mid-right area
        if px in (3, 4):
            return BRICK_SPECK
        return BRICK_BASE
    elif variation == 2:
        return BRICK_BASE
    elif variation == 3:
        if px == 2:
            return BRICK_MID
        return BRICK_BASE
    else:
        return BRICK_BASE


def generate() -> Image.Image:
    """Generate and return the 32x32 brick wall tile as a PIL RGBA Image."""
    img = Image.new("RGBA", (SIZE, SIZE), MORTAR)
    pix = img.load()

    for row in range(8):          # 8 brick rows  (row * 4 pixels tall)
        offset = 4 if (row % 2 == 1) else 0   # half-brick horizontal stagger

        for col in range(5):      # 5 cells wide covers 32px with offset wrapping
            # Brick top-left in tile space
            tile_x = (col * 8 - offset) % SIZE
            tile_y = row * 4

            for local_y in range(4):
                for local_x in range(8):
                    screen_x = (tile_x + local_x) % SIZE
                    screen_y = tile_y + local_y

                    if screen_y >= SIZE:
                        continue

                    # Identify which logical brick this belongs to so the
                    # colour hash is stable under wrapping.
                    brick_col_id = col if (tile_x + local_x) < SIZE else col + 1
                    color = _brick_color(brick_col_id, row, local_x, local_y)
                    pix[screen_x, screen_y] = color

    # Second pass: add subtle vertical crack lines on a couple of bricks
    # for extra surface detail.  Placed deterministically so tiling is clean.
    # Crack positions chosen so they don't land on mortar and stay inside one brick.
    crack_positions = [
        # (tile_x, tile_y) of the pixel — absolute within the 32px tile
        (2,  1), (3,  1),          # row 0 brick crack
        (19, 5), (19, 6),          # row 1 brick crack (offset row)
        (9,  9), (9, 10),          # row 2
        (25, 13), (26, 13),        # row 3 (offset row)
        (5,  17), (5, 18),         # row 4
        (21, 21), (21, 22),        # row 5 (offset row)
        (13, 25), (14, 25),        # row 6
        (29, 29), (29, 30 % SIZE), # row 7 (offset row) — wraps
    ]
    for (cx, cy) in crack_positions:
        cx = cx % SIZE
        cy = cy % SIZE
        # Only darken if it's not mortar
        existing = pix[cx, cy]
        if existing != MORTAR:
            # Darken by ~20% to simulate a surface crack
            r, g, b, a = existing
            pix[cx, cy] = (max(0, r - 20), max(0, g - 12), max(0, b - 10), a)

    return img


# ---------------------------------------------------------------------------
# ATLAS JSON  (Phaser-compatible, single frame)
# ---------------------------------------------------------------------------

def build_atlas() -> dict:
    """Return a Phaser-compatible texture atlas dict for the brick wall tile."""
    return {
        "meta": {
            "image": IMAGE_FILE,
            "size": {"w": SIZE, "h": SIZE},
            "scale": "1",
        },
        "frames": {
            "brick_wall": {
                "frame":             {"x": 0, "y": 0, "w": SIZE, "h": SIZE},
                "rotated":           False,
                "trimmed":           False,
                "spriteSourceSize":  {"x": 0, "y": 0, "w": SIZE, "h": SIZE},
                "sourceSize":        {"w": SIZE, "h": SIZE},
            }
        },
        "animations": {
            "brick_wall": ["brick_wall"]
        },
    }


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(PUBLIC_DIR,  exist_ok=True)

    img = generate()

    # Save to generated/
    png_path  = os.path.join(OUTPUT_DIR, IMAGE_FILE)
    json_path = os.path.join(OUTPUT_DIR, JSON_FILE)
    img.save(png_path)
    print(f"  Tile image : {png_path}  ({SIZE}x{SIZE})")

    atlas = build_atlas()
    with open(json_path, "w") as f:
        json.dump(atlas, f, indent=2)
    print(f"  Atlas JSON : {json_path}")

    # Export copy to public/assets/sprites/
    pub_path = os.path.join(PUBLIC_DIR, IMAGE_FILE)
    img.save(pub_path)
    print(f"  Public     : {pub_path}")
