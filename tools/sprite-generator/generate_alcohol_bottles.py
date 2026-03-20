#!/usr/bin/env python3
"""
Glass alcohol bottle spritesheet generator for Phaser 3.

Generates a 128x32 PNG with 4 bottle sprites side-by-side (each 32x32).
Top-down RPG perspective: bottles viewed from slightly above.

Bottle lineup (left to right, x offsets 0/32/64/96):
  0 – Whiskey : square/angular amber bottle, cork, label
  1 – Wine    : tall narrow dark bottle, cork, long neck
  2 – Gin     : shorter wide bottle, pale blue-green tint
  3 – Beer    : classic dark-brown beer bottle, cap

Output:
    generated/alcohol_bottles.png
    generated/alcohol_bottles.json
    public/assets/sprites/alcohol_bottles.png

Usage:
    python generate_alcohol_bottles.py
"""

import json
import os
import shutil

from PIL import Image

# ---------------------------------------------------------------------------
# OUTPUT CONFIG
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(__file__)
OUTPUT_DIR = os.path.join(_HERE, "generated")
PUBLIC_DIR = os.path.join(_HERE, "..", "..", "public", "assets", "sprites")

BOTTLE_W = 32
BOTTLE_H = 32
NUM_BOTTLES = 4
SHEET_W = BOTTLE_W * NUM_BOTTLES  # 128
SHEET_H = BOTTLE_H                # 32

# ---------------------------------------------------------------------------
# HELPER
# ---------------------------------------------------------------------------

def _px(img, x, y, color):
    """Set pixel if within bounds."""
    if 0 <= x < img.width and 0 <= y < img.height:
        img.putpixel((x, y), color)


def _rect(img, x0, y0, x1, y1, color):
    """Fill inclusive rectangle."""
    for yy in range(y0, y1 + 1):
        for xx in range(x0, x1 + 1):
            _px(img, xx, yy, color)


def _hline(img, y, x0, x1, color):
    for xx in range(x0, x1 + 1):
        _px(img, xx, y, color)


def _vline(img, x, y0, y1, color):
    for yy in range(y0, y1 + 1):
        _px(img, x, yy, color)


# ---------------------------------------------------------------------------
# BOTTLE PAINTERS  (each draws into the 32x32 cell at offset ox, oy=0)
# ---------------------------------------------------------------------------

def _draw_whiskey(img, ox):
    """Angular amber whiskey bottle. Top-down: we see the square cap + shoulder + body."""
    # Palette
    OUTLINE   = (30,  15,   5, 255)
    BODY      = (160,  80,  20, 255)   # amber body
    BODY_DARK = (110,  50,  10, 255)   # shadow side
    BODY_HL   = (210, 130,  50, 255)   # glass highlight
    LIQUID    = (190, 100,  25, 200)   # amber liquid (semi-transparent)
    LABEL     = (230, 215, 175, 255)   # cream label
    LABEL_TXT = (100,  50,  20, 255)   # label text/lines
    CORK      = (185, 155, 100, 255)   # cork top
    CORK_DK   = (140, 110,  65, 255)   # cork shadow
    GLASS_SHN = (255, 230, 180, 200)   # glass shine

    # Bottle body: square ish, 18px wide, 24px tall
    bx0, by0, bx1, by1 = ox + 7, 4, ox + 24, 27

    # Outer body fill (liquid)
    _rect(img, bx0 + 1, by0 + 1, bx1 - 1, by1 - 1, LIQUID)

    # Label area: rows 10-20
    _rect(img, bx0 + 2, by0 + 8, bx1 - 2, by0 + 16, LABEL)
    # Label lines
    _hline(img, by0 + 10, bx0 + 3, bx1 - 3, LABEL_TXT)
    _hline(img, by0 + 12, bx0 + 3, bx1 - 3, LABEL_TXT)
    _hline(img, by0 + 14, bx0 + 3, bx1 - 3, LABEL_TXT)

    # Shadow right side
    _vline(img, bx1 - 1, by0 + 1, by1 - 1, BODY_DARK)
    _vline(img, bx1 - 2, by0 + 1, by1 - 1, BODY_DARK)

    # Highlight left side
    _vline(img, bx0 + 1, by0 + 1, by1 - 1, BODY_HL)
    _px(img, bx0 + 2, by0 + 2, GLASS_SHN)
    _px(img, bx0 + 2, by0 + 3, GLASS_SHN)

    # Outline
    for xx in range(bx0, bx1 + 1):
        _px(img, xx, by0, OUTLINE)
        _px(img, xx, by1, OUTLINE)
    for yy in range(by0, by1 + 1):
        _px(img, bx0, yy, OUTLINE)
        _px(img, bx1, yy, OUTLINE)

    # Cork/cap: 4x4 centered top
    cx0 = ox + 14
    _rect(img, cx0, 1, cx0 + 3, 3, CORK)
    _hline(img, 1, cx0, cx0 + 3, CORK_DK)
    for xx in range(cx0, cx0 + 4):
        _px(img, xx, 0, OUTLINE)
    for yy in range(0, 4):
        _px(img, cx0 - 1, yy, OUTLINE)
        _px(img, cx0 + 4, yy, OUTLINE)

    # Bottom shadow
    _hline(img, by1 - 1, bx0 + 1, bx1 - 1, BODY_DARK)


def _draw_wine(img, ox):
    """Tall narrow dark wine bottle with long neck."""
    OUTLINE   = (15,  10,  20, 255)
    BODY      = (45,  20,  55, 255)   # deep purple-dark glass
    BODY_HL   = (80,  45,  95, 255)   # glass highlight
    BODY_DARK = (25,  10,  30, 255)   # shadow side
    LIQUID    = (130,  20,  40, 200)  # dark red wine
    NECK      = (40,  18,  50, 255)   # neck (narrower)
    CORK      = (200, 170, 110, 255)
    CORK_DK   = (155, 125,  70, 255)
    FOIL      = (180, 165,  30, 255)  # gold foil capsule
    GLASS_SHN = (160, 130, 200, 210)  # purple-tinted shine

    # Body: 14px wide, rows 10-27
    bx0, by0, bx1, by1 = ox + 9, 10, ox + 22, 27

    # Liquid fill
    _rect(img, bx0 + 1, by0 + 1, bx1 - 1, by1 - 1, LIQUID)

    # Shadow + highlight
    _vline(img, bx1 - 1, by0 + 1, by1 - 1, BODY_DARK)
    _vline(img, bx0 + 1, by0 + 1, by1 - 1, BODY_HL)
    _px(img, bx0 + 2, by0 + 2, GLASS_SHN)
    _px(img, bx0 + 2, by0 + 3, GLASS_SHN)

    # Body outline
    for xx in range(bx0, bx1 + 1):
        _px(img, xx, by0, OUTLINE)
        _px(img, xx, by1, OUTLINE)
    for yy in range(by0, by1 + 1):
        _px(img, bx0, yy, OUTLINE)
        _px(img, bx1, yy, OUTLINE)

    # Shoulder (transition body→neck): rows 7-9
    _rect(img, bx0 + 1, 7, bx1 - 1, 9, LIQUID)
    _px(img, bx0, 8, OUTLINE)
    _px(img, bx1, 8, OUTLINE)
    _px(img, bx0 + 1, 7, OUTLINE)
    _px(img, bx1 - 1, 7, OUTLINE)

    # Neck: 6px wide, rows 2-6
    nx0, nx1 = ox + 13, ox + 18
    _rect(img, nx0, 3, nx1, 6, NECK)
    _px(img, nx0 + 1, 3, BODY_HL)
    for xx in range(nx0, nx1 + 1):
        _px(img, xx, 2, OUTLINE)
    for yy in range(2, 7):
        _px(img, nx0 - 1, yy, OUTLINE)
        _px(img, nx1 + 1, yy, OUTLINE)

    # Foil capsule: rows 5-9 on neck
    _rect(img, nx0, 5, nx1, 8, FOIL)
    _hline(img, 5, nx0, nx1, OUTLINE)
    _hline(img, 8, nx0, nx1, OUTLINE)

    # Cork: rows 0-2
    _rect(img, nx0 + 1, 0, nx1 - 1, 1, CORK)
    _hline(img, 0, nx0 + 1, nx1 - 1, CORK_DK)
    for xx in range(nx0, nx1 + 1):
        _px(img, xx, 0, OUTLINE)


def _draw_gin(img, ox):
    """Short wide gin bottle, pale blue-green tint, metal cap."""
    OUTLINE   = (20,  35,  40, 255)
    BODY      = (140, 195, 195, 220)  # pale teal glass (semi-transparent)
    BODY_HL   = (210, 240, 240, 230)  # strong glass highlight
    BODY_DARK = (80,  130, 130, 220)  # shadow side
    LIQUID    = (175, 225, 215, 180)  # very pale gin
    LABEL     = (240, 240, 235, 255)  # white label
    LABEL_TXT = (20,  60,  80, 255)   # dark blue-teal text
    CAP       = (180, 180, 180, 255)  # metal cap
    CAP_HL    = (230, 230, 230, 255)
    CAP_DK    = (120, 120, 120, 255)
    GLASS_SHN = (255, 255, 255, 200)

    # Wide body: 20px wide, rows 8-27
    bx0, by0, bx1, by1 = ox + 6, 8, ox + 25, 27

    # Liquid fill
    _rect(img, bx0 + 1, by0 + 1, bx1 - 1, by1 - 1, LIQUID)

    # Label centre band
    _rect(img, bx0 + 2, by0 + 6, bx1 - 2, by0 + 14, LABEL)
    _hline(img, by0 + 7,  bx0 + 3, bx1 - 3, LABEL_TXT)
    _hline(img, by0 + 9,  bx0 + 3, bx1 - 3, LABEL_TXT)
    _hline(img, by0 + 11, bx0 + 3, bx1 - 3, LABEL_TXT)

    # Shadow + highlight
    _vline(img, bx1 - 1, by0 + 1, by1 - 1, BODY_DARK)
    _vline(img, bx1 - 2, by0 + 2, by1 - 2, BODY_DARK)
    _vline(img, bx0 + 1, by0 + 1, by1 - 1, BODY_HL)
    _px(img, bx0 + 2, by0 + 2, GLASS_SHN)
    _px(img, bx0 + 2, by0 + 3, GLASS_SHN)
    _px(img, bx0 + 3, by0 + 2, GLASS_SHN)

    # Body outline
    for xx in range(bx0, bx1 + 1):
        _px(img, xx, by0, OUTLINE)
        _px(img, xx, by1, OUTLINE)
    for yy in range(by0, by1 + 1):
        _px(img, bx0, yy, OUTLINE)
        _px(img, bx1, yy, OUTLINE)

    # Neck: short, 8px wide, rows 3-7
    nx0, nx1 = ox + 12, ox + 19
    _rect(img, nx0, 4, nx1, 7, BODY)
    _px(img, nx0 + 1, 4, BODY_HL)
    for xx in range(nx0, nx1 + 1):
        _px(img, xx, 3, OUTLINE)
    for yy in range(3, 8):
        _px(img, nx0 - 1, yy, OUTLINE)
        _px(img, nx1 + 1, yy, OUTLINE)

    # Metal cap: rows 0-3
    cx0, cx1 = nx0, nx1
    _rect(img, cx0, 0, cx1, 3, CAP)
    _hline(img, 0, cx0, cx1, CAP_HL)
    _hline(img, 3, cx0, cx1, CAP_DK)
    _px(img, cx0, 0, OUTLINE)
    _px(img, cx1, 0, OUTLINE)
    for xx in range(cx0, cx1 + 1):
        _px(img, xx, 0, OUTLINE)
    for yy in range(0, 4):
        _px(img, cx0 - 1, yy, OUTLINE)
        _px(img, cx1 + 1, yy, OUTLINE)


def _draw_beer(img, ox):
    """Classic dark brown beer bottle, metal crown cap, amber liquid."""
    OUTLINE   = (20,  10,   5, 255)
    BODY      = (70,  35,   5, 255)   # dark brown glass
    BODY_HL   = (110,  60,  15, 255)  # glass highlight
    BODY_DARK = (35,  15,   2, 255)   # deep shadow
    LIQUID    = (175, 100,  20, 210)  # amber beer
    CAP       = (180,  30,  20, 255)  # red crown cap
    CAP_HL    = (220,  80,  60, 255)
    CAP_METAL = (160, 160, 160, 255)  # cap rim (metal)
    GLASS_SHN = (200, 170, 100, 200)

    # Body: 14px wide, rows 10-27
    bx0, by0, bx1, by1 = ox + 9, 10, ox + 22, 27

    # Liquid fill
    _rect(img, bx0 + 1, by0 + 1, bx1 - 1, by1 - 1, LIQUID)

    # Shadow + highlight
    _vline(img, bx1 - 1, by0 + 1, by1 - 1, BODY_DARK)
    _vline(img, bx1 - 2, by0 + 2, by1 - 2, BODY_DARK)
    _vline(img, bx0 + 1, by0 + 1, by1 - 1, BODY_HL)
    _px(img, bx0 + 2, by0 + 2, GLASS_SHN)
    _px(img, bx0 + 2, by0 + 3, GLASS_SHN)

    # Body outline
    for xx in range(bx0, bx1 + 1):
        _px(img, xx, by0, OUTLINE)
        _px(img, xx, by1, OUTLINE)
    for yy in range(by0, by1 + 1):
        _px(img, bx0, yy, OUTLINE)
        _px(img, bx1, yy, OUTLINE)

    # Shoulder: rows 7-9
    _rect(img, bx0 + 1, 7, bx1 - 1, 9, LIQUID)
    _px(img, bx0, 8, OUTLINE)
    _px(img, bx1, 8, OUTLINE)
    _px(img, bx0 + 1, 7, OUTLINE)
    _px(img, bx1 - 1, 7, OUTLINE)

    # Neck: 6px wide, rows 3-6
    nx0, nx1 = ox + 13, ox + 18
    _rect(img, nx0, 3, nx1, 6, BODY)
    _px(img, nx0 + 1, 3, BODY_HL)
    for xx in range(nx0, nx1 + 1):
        _px(img, xx, 2, OUTLINE)
    for yy in range(2, 7):
        _px(img, nx0 - 1, yy, OUTLINE)
        _px(img, nx1 + 1, yy, OUTLINE)

    # Crown cap: rows 0-2 (crown top, slightly wider than neck)
    cx0, cx1 = nx0 - 1, nx1 + 1
    _rect(img, cx0, 0, cx1, 2, CAP)
    _hline(img, 0, cx0, cx1, CAP_HL)
    _hline(img, 2, cx0, cx1, CAP_METAL)
    for xx in range(cx0, cx1 + 1):
        _px(img, xx, 0, OUTLINE)
    for yy in range(0, 3):
        _px(img, cx0 - 1, yy, OUTLINE)
        _px(img, cx1 + 1, yy, OUTLINE)

    # Bottom shadow
    _hline(img, by1 - 1, bx0 + 1, bx1 - 1, BODY_DARK)


# ---------------------------------------------------------------------------
# MAIN GENERATE FUNCTION
# ---------------------------------------------------------------------------

def generate() -> Image.Image:
    """Generate the 128x32 alcohol bottles spritesheet."""
    img = Image.new("RGBA", (SHEET_W, SHEET_H), (0, 0, 0, 0))

    _draw_whiskey(img, 0)
    _draw_wine(img, 32)
    _draw_gin(img, 64)
    _draw_beer(img, 96)

    return img


# ---------------------------------------------------------------------------
# ATLAS
# ---------------------------------------------------------------------------

BOTTLE_NAMES = ["whiskey", "wine", "gin", "beer"]


def build_atlas(image_file: str) -> dict:
    frames = {}
    for i, name in enumerate(BOTTLE_NAMES):
        frames[name] = {
            "frame": {"x": i * BOTTLE_W, "y": 0, "w": BOTTLE_W, "h": BOTTLE_H},
            "rotated": False,
            "trimmed": False,
            "spriteSourceSize": {"x": 0, "y": 0, "w": BOTTLE_W, "h": BOTTLE_H},
            "sourceSize": {"w": BOTTLE_W, "h": BOTTLE_H},
        }
    return {
        "frames": frames,
        "meta": {
            "app": "phaser-mobile-game-topdown/sprite-generator",
            "image": image_file,
            "size": {"w": SHEET_W, "h": SHEET_H},
            "scale": "1",
        },
    }


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(PUBLIC_DIR, exist_ok=True)

    img = generate()

    png_path  = os.path.join(OUTPUT_DIR, "alcohol_bottles.png")
    json_path = os.path.join(OUTPUT_DIR, "alcohol_bottles.json")
    pub_path  = os.path.join(PUBLIC_DIR,  "alcohol_bottles.png")

    img.save(png_path)

    atlas = build_atlas("alcohol_bottles.png")
    with open(json_path, "w") as f:
        json.dump(atlas, f, indent=2)

    shutil.copy(png_path, pub_path)

    print(f"  Spritesheet : {png_path}  ({SHEET_W}x{SHEET_H})")
    print(f"  Atlas JSON  : {json_path}")
    print(f"  Exported    : {pub_path}")
