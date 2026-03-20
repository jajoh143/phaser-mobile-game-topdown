#!/usr/bin/env python3
"""
Dance floor tile generator for Phaser 3.

Generates a 32x32 seamlessly tileable pixel-art disco dance-floor tile.
Classic 4×4 checkerboard of glowing coloured panels separated by dark metal
grout lines.  The tile is designed to be used as a repeating floor beneath
the dance area of the bar scene.

Output:
    generated/dance_floor.png
    generated/dance_floor.json
    public/assets/sprites/dance_floor.png

Usage:
    python generate_dance_floor.py
"""

import json
import os
from PIL import Image

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT   = os.path.abspath(os.path.join(_SCRIPT_DIR, "..", ".."))

OUTPUT_DIR  = os.path.join(_SCRIPT_DIR, "generated")
PUBLIC_DIR  = os.path.join(_REPO_ROOT, "public", "assets", "sprites")

IMAGE_FILE = "dance_floor.png"
JSON_FILE  = "dance_floor.json"

SIZE = 32   # output tile dimensions

# ---------------------------------------------------------------------------
# PALETTE
# ---------------------------------------------------------------------------
GROUT       = (14, 12, 18, 255)   # dark metal gap between panels
GROUT_INNER = (22, 18, 28, 255)   # slightly lighter interior grout cross

# Four panel colours – vivid neon hues for the disco aesthetic.
# Each 8×8 cell uses one base colour (face) + a brighter highlight for the
# inner glow and a darker edge for the bevel shadow.
PANELS = [
    # (base,             glow,              edge,              highlight)
    ((180,  40, 200, 255), (220,  80, 240, 255), (100, 20, 120, 255), (240, 140, 255, 255)),  # magenta
    ((40,  180, 220, 255), ( 80, 220, 255, 255), ( 20, 100, 140, 255), (160, 240, 255, 255)),  # cyan
    (( 60, 200,  60, 255), (100, 240, 100, 255), ( 30, 120,  30, 255), (180, 255, 180, 255)),  # green
    ((220, 180,  20, 255), (255, 220,  60, 255), (140, 110,  10, 255), (255, 240, 160, 255)),  # yellow
]

# Checkerboard pattern: which PANELS index does cell (col, row) use?
# Alternating so adjacent cells always contrast.
# 4×4 grid of 8×8 cells (including 1px grout separators at cell boundaries)
# Layout (col 0-3, row 0-3):
CHECKER = [
    [0, 1, 0, 1],
    [2, 3, 2, 3],
    [0, 1, 0, 1],
    [2, 3, 2, 3],
]


def _panel_pixel(local_x: int, local_y: int, panel_idx: int) -> tuple:
    """
    Return RGBA for pixel (local_x, local_y) inside a 7×7 panel face
    (the 8×8 cell minus the 1-px grout border on right and bottom).

    local_x, local_y are 0-6.
    """
    base, glow, edge, highlight = PANELS[panel_idx]

    # 1-px bevel: top-left = bright, bottom-right = dark edge
    if local_x == 0 or local_y == 0:
        # top / left bevel — brighter
        return highlight
    if local_x == 6 or local_y == 6:
        # bottom / right bevel — darker edge
        return edge

    # Inner face: small glow spot near top-left of panel
    # Creates the impression of a light source behind the panel.
    gx = local_x - 1   # 0-4 in glow zone
    gy = local_y - 1
    dist_sq = gx * gx + gy * gy

    if dist_sq <= 2:
        return glow
    if dist_sq <= 5:
        # blend glow → base
        t = (dist_sq - 2) / 3.0
        r = int(glow[0] * (1 - t) + base[0] * t)
        g = int(glow[1] * (1 - t) + base[1] * t)
        b = int(glow[2] * (1 - t) + base[2] * t)
        return (r, g, b, 255)

    # Subtle radial darkening toward bottom-right corner
    fade = (local_x + local_y) / 12.0   # 0 → 1
    r = int(base[0] * (1 - fade * 0.25))
    g = int(base[1] * (1 - fade * 0.25))
    b = int(base[2] * (1 - fade * 0.25))
    return (r, g, b, 255)


def generate() -> Image.Image:
    """Generate and return the 32×32 dance floor tile."""
    img = Image.new("RGBA", (SIZE, SIZE), GROUT)
    pix = img.load()

    # Draw 4×4 grid of 8×8 cells.
    # Each cell occupies columns [cx*8 .. cx*8+7], rows [cy*8 .. cy*8+7].
    # Last pixel of each cell (local_x==7 or local_y==7) is grout.
    for cy in range(4):
        for cx in range(4):
            panel_idx = CHECKER[cy][cx]
            cell_x0 = cx * 8
            cell_y0 = cy * 8

            for local_y in range(8):
                for local_x in range(8):
                    px = cell_x0 + local_x
                    py = cell_y0 + local_y

                    if px >= SIZE or py >= SIZE:
                        continue

                    if local_x == 7 or local_y == 7:
                        # Grout line
                        # The inner cross is slightly lighter than the outer edge
                        pix[px, py] = GROUT_INNER if (local_x == 7 and local_y == 7) else GROUT
                    else:
                        pix[px, py] = _panel_pixel(local_x, local_y, panel_idx)

    # Add a subtle specular glint on each panel: single bright pixel near top-left
    for cy in range(4):
        for cx in range(4):
            glint_x = cx * 8 + 2
            glint_y = cy * 8 + 2
            if glint_x < SIZE and glint_y < SIZE:
                pix[glint_x, glint_y] = (255, 255, 255, 200)

    return img


# ---------------------------------------------------------------------------
# ATLAS JSON
# ---------------------------------------------------------------------------

def build_atlas() -> dict:
    return {
        "meta": {
            "image": IMAGE_FILE,
            "size": {"w": SIZE, "h": SIZE},
            "scale": "1",
        },
        "frames": {
            "dance_floor": {
                "frame":            {"x": 0, "y": 0, "w": SIZE, "h": SIZE},
                "rotated":          False,
                "trimmed":          False,
                "spriteSourceSize": {"x": 0, "y": 0, "w": SIZE, "h": SIZE},
                "sourceSize":       {"w": SIZE, "h": SIZE},
            }
        },
        "animations": {
            "dance_floor": ["dance_floor"]
        },
    }


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(PUBLIC_DIR,  exist_ok=True)

    img = generate()

    png_path  = os.path.join(OUTPUT_DIR, IMAGE_FILE)
    json_path = os.path.join(OUTPUT_DIR, JSON_FILE)
    img.save(png_path)
    print(f"  Tile image : {png_path}  ({SIZE}x{SIZE})")

    atlas = build_atlas()
    with open(json_path, "w") as f:
        json.dump(atlas, f, indent=2)
    print(f"  Atlas JSON : {json_path}")

    pub_path = os.path.join(PUBLIC_DIR, IMAGE_FILE)
    img.save(pub_path)
    print(f"  Public     : {pub_path}")
