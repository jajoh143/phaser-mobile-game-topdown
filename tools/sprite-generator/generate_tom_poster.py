#!/usr/bin/env python3
"""
Tom of Finland-style poster generator for Phaser 3.

Generates a 32×48 pixel-art poster sprite: a stylised portrait of a man
wearing a leather peaked cap, thick handlebar mustache, and dark aviator
sunglasses — in the bold, graphic aesthetic of Tom of Finland.

The poster has a cream/off-white background with a simple black outer frame
and a coloured inner frame border, giving it the look of a framed print on
a bar wall.

Output:
    generated/tom_poster.png
    generated/tom_poster.json
    public/assets/sprites/tom_poster.png

Usage:
    python generate_tom_poster.py
"""

import json
import os
from PIL import Image

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT   = os.path.abspath(os.path.join(_SCRIPT_DIR, "..", ".."))

OUTPUT_DIR  = os.path.join(_SCRIPT_DIR, "generated")
PUBLIC_DIR  = os.path.join(_REPO_ROOT, "public", "assets", "sprites")

IMAGE_FILE = "tom_poster.png"
JSON_FILE  = "tom_poster.json"

W = 32
H = 48

# ---------------------------------------------------------------------------
# PALETTE
# ---------------------------------------------------------------------------
FRAME_OUTER    = (20,  16, 14, 255)   # black outer poster frame
FRAME_INNER    = (180, 40, 40, 255)   # bold red inner border
PAPER          = (238, 230, 210, 255) # cream poster paper
SKIN           = (210, 165, 120, 255) # warm olive skin tone
SKIN_SHADOW    = (175, 125,  80, 255) # jaw / temple shadow
SKIN_HIGHLIGHT = (225, 185, 145, 255) # nose bridge highlight
CAP_LEATHER    = (28,  22,  18, 255)  # very dark leather cap body
CAP_SHINE      = (60,  50,  40, 255)  # leather sheen highlight strip
CAP_PEAK       = (22,  18,  14, 255)  # peak/brim (darker)
CAP_BADGE      = (190, 160,  30, 255) # gold badge on cap front
GLASSES_FRAME  = (18,  16,  12, 255)  # dark aviator frame
GLASSES_LENS   = (40,  36,  50, 255)  # dark tinted lens
GLASSES_SHINE  = (90,  86, 110, 255)  # tiny lens glint
MUSTACHE       = (40,  28,  18, 255)  # dark brown handlebar mustache
MUSTACHE_MID   = (60,  44,  28, 255)  # mid tone in mustache
LIPS           = (170,  90,  70, 255) # lips (barely visible under mustache)
NECK           = (190, 148, 105, 255) # neck
SHIRT_DARK     = (28,  22,  18, 255)  # dark leather jacket collar/shirt
SHIRT_MID      = (42,  36,  28, 255)
SHIRT_LIGHT    = (62,  52,  40, 255)  # jacket highlight
SHIRT_ZIP      = (120, 110,  80, 255) # metallic zip

# ---------------------------------------------------------------------------
# PIXEL MAP  (32 cols × 48 rows)
# Each row is a string of length 32; key below.
#
# Key:
#  .  = PAPER (background)
#  F  = FRAME_OUTER
#  f  = FRAME_INNER
#  s  = SKIN
#  S  = SKIN_SHADOW
#  H  = SKIN_HIGHLIGHT
#  C  = CAP_LEATHER
#  c  = CAP_SHINE
#  P  = CAP_PEAK
#  B  = CAP_BADGE
#  G  = GLASSES_FRAME
#  g  = GLASSES_LENS
#  *  = GLASSES_SHINE
#  M  = MUSTACHE
#  m  = MUSTACHE_MID
#  L  = LIPS
#  N  = NECK
#  J  = SHIRT_DARK
#  j  = SHIRT_MID
#  l  = SHIRT_LIGHT
#  Z  = SHIRT_ZIP
# ---------------------------------------------------------------------------

ROWS = [
    # 0123456789012345678901234567890 1
    "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF",  # row  0 outer frame top
    "FfffffffffffffffffffffffffffffffF",  # placeholder — rebuild below
    "FfffffffffffffffffffffffffffffffF",
    "Fff............................ffF",
    "Fff............................ffF",
    "Fff....CCCCCCCCCCCCCCCCC.......ffF",  # cap start (wider)
    "Fff...CCCCCCCCCCCCCCCCCCCc......ffF",
    "Fff..CCCCCCCCcCCCCCCCCCCCC......ffF",
    "Fff..PPPPPPPPPPPPPPPPPPPPPP.....ffF",  # peak / brim
    "Fff...sssssssssssssssssss......ffF",  # forehead
    "Fff...sSSSsssssssssssSSSs......ffF",
    "Fff...sssssssssssssssssss......ffF",
    "Fff...sGGGGGGGGsGGGGGGGGs......ffF",  # sunglasses row 1 (frame)
    "Fff...sGgggggGsGgggggGGs......ffF",  # lenses
    "Fff...sGggg*gGGGg*gggGGs......ffF",  # lenses with glints
    "Fff...sGgggggGsGgggggGGs......ffF",
    "Fff...sGGGGGGGsGGGGGGGGs......ffF",  # sunglasses row 5 (frame)
    "Fff...ssssHssssssssHssss......ffF",  # nose / under glasses
    "Fff...sssssssssssssssss.......ffF",
    "Fff...sMMMMMsssssMMMMMs.......ffF",  # mustache outer
    "Fff...sMMMMMMmmmMMMMMMMs......ffF",  # mustache thick centre
    "Fff...sLMMMMMMMMMMMMMMs.......ffF",  # lips / mustache bottom
    "Fff...ssssssssssssssss........ffF",  # chin
    "Fff....SSSSSSSSSSSSSSS........ffF",  # jaw shadow
    "Fff.....NNNNNNNNNNNN..........ffF",  # neck
    "Fff.....JJJJNNNNNJJJJ.........ffF",  # shirt collar begins
    "Fff....JJJJjJJJJJjJJJJ........ffF",
    "Fff....JJJllJZZZJllJJJ.........ffF",  # jacket zip
    "Fff....JJJlJZZZZZJlJJJ.........ffF",
    "Fff....JJJJjZZZZZjJJJJ.........ffF",
    "Fff....JJJJJJJJJJJJJJJ........ffF",
    "Fff....JJJJJJJJJJJJJJJ........ffF",
    "Fff............................ffF",
    "Fff............................ffF",
    "Fff............................ffF",
    "Fff............................ffF",
    "Fff............................ffF",
    "Fff............................ffF",
    "Fff............................ffF",
    "Fff............................ffF",
    "Fff............................ffF",
    "Fff............................ffF",
    "Fff............................ffF",
    "Fff............................ffF",
    "FfffffffffffffffffffffffffffffffF",
    "FfffffffffffffffffffffffffffffffF",
    "FfffffffffffffffffffffffffffffffF",
    "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF",  # row 47 outer frame bottom
]

COLOR_MAP = {
    'F': FRAME_OUTER,
    'f': FRAME_INNER,
    '.': PAPER,
    's': SKIN,
    'S': SKIN_SHADOW,
    'H': SKIN_HIGHLIGHT,
    'C': CAP_LEATHER,
    'c': CAP_SHINE,
    'P': CAP_PEAK,
    'B': CAP_BADGE,
    'G': GLASSES_FRAME,
    'g': GLASSES_LENS,
    '*': GLASSES_SHINE,
    'M': MUSTACHE,
    'm': MUSTACHE_MID,
    'L': LIPS,
    'N': NECK,
    'J': SHIRT_DARK,
    'j': SHIRT_MID,
    'l': SHIRT_LIGHT,
    'Z': SHIRT_ZIP,
}


def _pixel_data() -> list[list[tuple]]:
    """
    Build the W×H grid of RGBA tuples from the ROWS string art above.
    Rows that are too short are padded with PAPER; too long are truncated.
    Rows 1-2 and 44-45 are the inner frame bands (all 'f' except outer 'F').
    """
    grid: list[list[tuple]] = []

    for row_idx in range(H):
        if row_idx < len(ROWS):
            row_str = ROWS[row_idx]
        else:
            row_str = ""

        row_pixels: list[tuple] = []
        for col_idx in range(W):
            if col_idx < len(row_str):
                ch = row_str[col_idx]
            else:
                # default: frame on edges, paper inside
                if col_idx == 0 or col_idx == W - 1:
                    ch = 'F'
                elif row_idx == 0 or row_idx == H - 1:
                    ch = 'F'
                elif col_idx == 1 or col_idx == W - 2:
                    ch = 'f'
                elif row_idx == 1 or row_idx == H - 2 or row_idx == 2 or row_idx == H - 3:
                    ch = 'f'
                else:
                    ch = '.'
            color = COLOR_MAP.get(ch, PAPER)
            row_pixels.append(color)

        grid.append(row_pixels)

    return grid


def generate() -> Image.Image:
    """Generate and return the 32×48 poster sprite."""
    img = Image.new("RGBA", (W, H), PAPER)
    pix = img.load()

    grid = _pixel_data()
    for y in range(H):
        for x in range(W):
            pix[x, y] = grid[y][x]

    # ----- Draw portrait programmatically over the pixel-art base -----------
    # We draw key portrait elements directly so they look consistent at 32 px wide.

    def put(x, y, color):
        if 0 <= x < W and 0 <= y < H:
            pix[x, y] = color

    def hline(y, x0, x1, color):
        for x in range(x0, x1 + 1):
            put(x, y, color)

    def vline(x, y0, y1, color):
        for y in range(y0, y1 + 1):
            put(x, y, color)

    # --- outer frame ---
    hline(0, 0, W-1, FRAME_OUTER)
    hline(H-1, 0, W-1, FRAME_OUTER)
    vline(0, 0, H-1, FRAME_OUTER)
    vline(W-1, 0, H-1, FRAME_OUTER)

    # --- red inner border (2 px inset) ---
    for b in range(1, 3):
        hline(b, 1, W-2, FRAME_INNER)
        hline(H-1-b, 1, W-2, FRAME_INNER)
        vline(b, 1, H-2, FRAME_INNER)
        vline(W-1-b, 1, H-2, FRAME_INNER)

    # --- paper fill ---
    for y in range(3, H-3):
        hline(y, 3, W-4, PAPER)

    # ---- LEATHER CAP (rows 5-8) ----
    #  Cap crown: rows 5-7, centered, ~20 px wide
    cap_cx = W // 2   # 16
    for y in range(5, 8):
        half = 10 - (y - 5)   # 10, 9, 8
        for x in range(cap_cx - half, cap_cx + half):
            put(x, y, CAP_LEATHER)
        # shine strip at top
        if y == 5:
            put(cap_cx - 3, y, CAP_SHINE)
            put(cap_cx - 2, y, CAP_SHINE)
    # Peak / brim row 8
    for x in range(cap_cx - 9, cap_cx + 10):
        put(x, 8, CAP_PEAK)
    # Badge on cap front (row 6, center)
    put(cap_cx, 6, CAP_BADGE)
    put(cap_cx+1, 6, CAP_BADGE)

    # ---- FACE (rows 9-23) ----
    face_top = 9
    face_bot = 23
    for y in range(face_top, face_bot + 1):
        half = 7 if y < 22 else (5 if y < 23 else 3)
        for x in range(cap_cx - half, cap_cx + half + 1):
            put(x, y, SKIN)
    # Jaw shadow
    for x in range(cap_cx - 6, cap_cx + 7):
        put(x, 23, SKIN_SHADOW)
    # Nose highlight
    put(cap_cx, 17, SKIN_HIGHLIGHT)
    put(cap_cx, 18, SKIN_HIGHLIGHT)

    # ---- SUNGLASSES (rows 12-16) ----
    # Two rectangular lenses connected by a thin bridge
    for y in range(12, 17):
        # Left lens
        for x in range(cap_cx - 7, cap_cx - 1):
            put(x, y, GLASSES_LENS if (y > 12 and y < 16) else GLASSES_FRAME)
        # Right lens
        for x in range(cap_cx + 1, cap_cx + 8):
            put(x, y, GLASSES_LENS if (y > 12 and y < 16) else GLASSES_FRAME)
        # outer frame pixels
        put(cap_cx - 7, y, GLASSES_FRAME)
        put(cap_cx - 1, y, GLASSES_FRAME)
        put(cap_cx + 1, y, GLASSES_FRAME)
        put(cap_cx + 7, y, GLASSES_FRAME)
    # top and bottom frame lines
    for x in range(cap_cx - 7, cap_cx):
        put(x, 12, GLASSES_FRAME)
        put(x, 16, GLASSES_FRAME)
    for x in range(cap_cx + 1, cap_cx + 8):
        put(x, 12, GLASSES_FRAME)
        put(x, 16, GLASSES_FRAME)
    # nose bridge
    put(cap_cx, 14, GLASSES_FRAME)
    # lens glints
    put(cap_cx - 5, 13, GLASSES_SHINE)
    put(cap_cx + 3, 13, GLASSES_SHINE)

    # ---- MUSTACHE (rows 19-21) ----
    # Thick handlebar shape
    for y in range(19, 22):
        half = 5 + (1 if y == 20 else 0)
        for x in range(cap_cx - half, cap_cx + half + 1):
            put(x, y, MUSTACHE if y != 20 else MUSTACHE_MID)
        # Handlebar tips curl up at the ends
    # Upward-curling tips
    put(cap_cx - 6, 18, MUSTACHE)
    put(cap_cx + 6, 18, MUSTACHE)
    put(cap_cx - 7, 19, MUSTACHE)
    put(cap_cx + 7, 19, MUSTACHE)

    # ---- NECK (rows 24-25) ----
    for y in range(24, 26):
        for x in range(cap_cx - 3, cap_cx + 4):
            put(x, y, NECK)

    # ---- LEATHER JACKET (rows 25-35) ----
    for y in range(25, 36):
        half = 10
        for x in range(cap_cx - half, cap_cx + half + 1):
            put(x, y, SHIRT_DARK)
        # Jacket highlights on sides
        put(cap_cx - half + 1, y, SHIRT_MID)
        put(cap_cx + half - 1, y, SHIRT_MID)
        # lapels (inner V shape)
        lapel_offset = max(0, y - 25)
        for dx in range(lapel_offset + 1):
            if dx <= 3:
                put(cap_cx - dx, y, SHIRT_MID)
                put(cap_cx + dx, y, SHIRT_MID)

    # Zip strip down centre
    for y in range(28, 36):
        put(cap_cx, y, SHIRT_ZIP)
        put(cap_cx - 1, y, SHIRT_LIGHT)
        put(cap_cx + 1, y, SHIRT_LIGHT)

    # ---- Poster title text at bottom (rows 38-42) -------------------------
    # Draw "T.o.F." in tiny 3×5 dot pixels at the bottom of the poster
    # We'll just do a small underline bar as a stylistic element
    hline(40, 7, W - 8, FRAME_INNER)
    hline(41, 7, W - 8, FRAME_OUTER)

    return img


# ---------------------------------------------------------------------------
# ATLAS JSON
# ---------------------------------------------------------------------------

def build_atlas() -> dict:
    return {
        "meta": {
            "image": IMAGE_FILE,
            "size": {"w": W, "h": H},
            "scale": "1",
        },
        "frames": {
            "tom_poster": {
                "frame":            {"x": 0, "y": 0, "w": W, "h": H},
                "rotated":          False,
                "trimmed":          False,
                "spriteSourceSize": {"x": 0, "y": 0, "w": W, "h": H},
                "sourceSize":       {"w": W, "h": H},
            }
        },
        "animations": {
            "tom_poster": ["tom_poster"]
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
    print(f"  Poster     : {png_path}  ({W}x{H})")

    atlas = build_atlas()
    with open(json_path, "w") as f:
        json.dump(atlas, f, indent=2)
    print(f"  Atlas JSON : {json_path}")

    pub_path = os.path.join(PUBLIC_DIR, IMAGE_FILE)
    img.save(pub_path)
    print(f"  Public     : {pub_path}")
