#!/usr/bin/env python3
"""
Demon bartender sprite generator.

Produces a 128×640 spritesheet in the same layout as char_*.png, using the
character engine with a demon palette (red skin, dark vest, ivory horns,
glowing orange eyes).  Horns are post-processed onto every frame so they
appear consistently across all animations and directions.

Usage:
    python generate_demon.py            # saves generated/demon_bartender.png
    python generate_demon.py --out /path/to/output.png
"""

import argparse
import os
import sys

_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _DIR)

import generate_character as gc
from PIL import Image

OUTPUT_DIR = os.path.join(_DIR, "generated")
OUT_FILE   = "demon_bartender.png"

# ---------------------------------------------------------------------------
# DEMON PALETTE
# ---------------------------------------------------------------------------
DEMON_PALETTE: dict = {
    "name":           "Demon bartender",
    "skin":           (195,  70,  70, 255),   # red demon skin
    "skin_shade":     (152,  46,  46, 255),   # deeper red (hue-shifted)
    "hair":           ( 35,   8,   8, 255),   # near-black dark red
    "hair_shade":     ( 18,   4,   4, 255),
    "hair_highlight": ( 68,  18,  18, 255),
    # Dark bartender vest/apron
    "shirt":          ( 28,  28,  34, 255),
    "shirt_shade":    ( 16,  16,  22, 255),
    # Dark trousers
    "pants":          ( 38,  22,  22, 255),
    "pants_shade":    ( 22,  12,  12, 255),
    # Dark shoes
    "shoes":          ( 22,  16,  16, 255),
    "shoes_shade":    ( 14,  10,  10, 255),
    # Near-black red outline
    "outline":        ( 12,   6,   6, 255),
    # Orange glowing eyes (iris/pupil)
    "eye":            (255, 120,  30, 255),
}

# ---------------------------------------------------------------------------
# HORN PIXEL DATA — (x, y, color_key) per facing direction
# ---------------------------------------------------------------------------
# Short hair for "down": highlights at y=2 (x 12-18), base at y=3 (x 10-20).
# y=0-1 are transparent above the hair → clean horn placement.
#
# Horn design: two small curved horns, ivory-tipped, pointing slightly outward.
#   horn_light = ivory tip
#   horn_mid   = bone mid-tone
#   horn_dark  = base / shadow

HORN_PIXELS: dict[str, list[tuple[int, int, str]]] = {
    "down": [
        # ── Left horn (curves left/up) ────────────────────────────────
        (11,  0, "horn_light"),   # ivory tip
        (10,  1, "horn_dark"),    # outer curve
        (11,  1, "horn_mid"),
        (10,  2, "horn_dark"),    # base shadow
        # ── Right horn (curves right/up) ─────────────────────────────
        (20,  0, "horn_light"),
        (21,  1, "horn_dark"),
        (20,  1, "horn_mid"),
        (21,  2, "horn_dark"),
    ],
    "up": [
        # Back-of-head view — horns still visible from behind
        (11,  0, "horn_light"),
        (10,  1, "horn_dark"),
        (11,  1, "horn_mid"),
        (10,  2, "horn_dark"),
        (20,  0, "horn_light"),
        (21,  1, "horn_dark"),
        (20,  1, "horn_mid"),
        (21,  2, "horn_dark"),
    ],
    "left": [
        # Side view: near horn (right/forward side) prominent, far horn dimmer
        # Near horn — forward-top, curves outward
        (17,  0, "horn_light"),
        (17,  1, "horn_mid"),
        (18,  1, "horn_dark"),
        (17,  2, "horn_dark"),
        # Far horn — behind head, barely visible
        (11,  0, "horn_dark"),
        (11,  1, "horn_dark"),
    ],
    "right": [
        # Mirror of left (FRAME_W=32, so x → 31-x)
        (14,  0, "horn_light"),   # 31-17=14
        (14,  1, "horn_mid"),
        (13,  1, "horn_dark"),    # 31-18=13
        (14,  2, "horn_dark"),
        (20,  0, "horn_dark"),    # 31-11=20
        (20,  1, "horn_dark"),
    ],
}


def generate() -> Image.Image:
    """Build the demon spritesheet and return it as a Pillow Image."""
    # Build base sheet using the character engine (calls _derive_palette internally)
    sheet, _ = gc.build_spritesheet(DEMON_PALETTE, hair_style="short")

    # Derive the extended palette ourselves so we can look up horn colours
    pal = gc._derive_palette(DEMON_PALETTE)
    pal["horn_light"] = (218, 188, 145, 255)   # ivory tip
    pal["horn_mid"]   = (178, 148, 108, 255)   # bone mid
    pal["horn_dark"]  = (128, 100,  68, 255)   # base shadow

    cols = gc.FRAMES_PER_DIR   # 4 frames per animation-direction row
    for anim_idx, anim in enumerate(gc.ANIMATIONS):
        for dir_idx, direction in enumerate(gc.DIRECTIONS):
            row_idx = anim_idx * len(gc.DIRECTIONS) + dir_idx
            horn_list = HORN_PIXELS.get(direction, [])
            for col in range(cols):
                fx = col * gc.FRAME_W   # left edge of this frame in sheet
                fy = row_idx * gc.FRAME_H   # top edge of this frame in sheet
                for hx, hy, color_key in horn_list:
                    if 0 <= hx < gc.FRAME_W and 0 <= hy < gc.FRAME_H:
                        sheet.putpixel((fx + hx, fy + hy), pal[color_key])

    return sheet


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate demon bartender spritesheet")
    parser.add_argument("--out", default=None, help="Output PNG path")
    args = parser.parse_args()

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = args.out or os.path.join(OUTPUT_DIR, OUT_FILE)
    sheet = generate()
    sheet.save(out_path)
    print(f"Saved {out_path}  ({sheet.width}×{sheet.height})")


if __name__ == "__main__":
    main()
