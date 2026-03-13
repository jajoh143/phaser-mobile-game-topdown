#!/usr/bin/env python3
"""
Top-down humanoid character sprite generator for Phaser 3.

Generates 32x48 spritesheets with multiple animations:
  - walk     (4 directions x 4 frames)
  - jump     (4 directions x 4 frames)
  - crouch   (4 directions x 4 frames)
  - interact (4 directions x 4 frames)

Characters are 32x48px — 1 tile wide, 1.5 tiles tall on a 32x32 world grid.
The top half of the sprite (head) extends above the tile collision box.

Style: chibi top-down RPG with rounded heads, dark outlines,
multi-tone shading, skin-toned arms, mouths, diverse hair styles.

Usage:
    python generate_character.py --preset 0 --name player
    python generate_character.py --preset 3 --hair afro --name npc1
    python generate_character.py --list-presets
    python generate_character.py --all
"""

import argparse
import json
import math
import os
from PIL import Image

# ---------------------------------------------------------------------------
# OUTPUT CONFIG
# ---------------------------------------------------------------------------
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "generated")
FRAME_W = 32
FRAME_H = 48
PADDING = 0
TILE_SIZE = 32

DIRECTIONS = ["down", "left", "right", "up"]
FRAMES_PER_DIR = 4
ANIMATIONS = ["walk", "jump", "crouch", "interact"]

# ---------------------------------------------------------------------------
# COLOR PALETTES
# ---------------------------------------------------------------------------
PRESETS = [
    {
        "name": "Light skin, brown hair, blue shirt",
        "skin": (222, 187, 155, 255),
        "skin_shade": (197, 160, 128, 255),
        "skin_dark": (175, 140, 110, 255),
        "hair": (90, 60, 35, 255),
        "hair_shade": (65, 42, 22, 255),
        "hair_highlight": (115, 80, 50, 255),
        "shirt": (80, 130, 190, 255),
        "shirt_shade": (55, 100, 155, 255),
        "shirt_highlight": (105, 155, 210, 255),
        "pants": (70, 70, 85, 255),
        "pants_shade": (50, 50, 65, 255),
        "shoes": (55, 45, 40, 255),
        "shoes_shade": (40, 32, 28, 255),
        "outline": (30, 25, 22, 255),
        "eye": (25, 25, 30, 255),
        "eye_white": (240, 240, 240, 255),
        "mouth": (160, 90, 80, 255),
    },
    {
        "name": "Medium skin, black hair, red shirt",
        "skin": (195, 150, 110, 255),
        "skin_shade": (170, 125, 88, 255),
        "skin_dark": (148, 108, 72, 255),
        "hair": (35, 28, 25, 255),
        "hair_shade": (22, 18, 16, 255),
        "hair_highlight": (52, 42, 38, 255),
        "shirt": (185, 60, 55, 255),
        "shirt_shade": (145, 42, 40, 255),
        "shirt_highlight": (210, 82, 75, 255),
        "pants": (55, 60, 75, 255),
        "pants_shade": (40, 44, 55, 255),
        "shoes": (50, 40, 35, 255),
        "shoes_shade": (35, 28, 24, 255),
        "outline": (28, 22, 20, 255),
        "eye": (25, 25, 30, 255),
        "eye_white": (240, 240, 240, 255),
        "mouth": (140, 75, 65, 255),
    },
    {
        "name": "Dark skin, short dark hair, green shirt",
        "skin": (140, 95, 65, 255),
        "skin_shade": (115, 75, 50, 255),
        "skin_dark": (95, 62, 40, 255),
        "hair": (30, 25, 22, 255),
        "hair_shade": (20, 16, 14, 255),
        "hair_highlight": (45, 38, 32, 255),
        "shirt": (60, 155, 80, 255),
        "shirt_shade": (42, 120, 58, 255),
        "shirt_highlight": (80, 178, 100, 255),
        "pants": (65, 65, 80, 255),
        "pants_shade": (48, 48, 60, 255),
        "shoes": (50, 42, 36, 255),
        "shoes_shade": (36, 30, 25, 255),
        "outline": (25, 20, 18, 255),
        "eye": (22, 22, 28, 255),
        "eye_white": (235, 235, 235, 255),
        "mouth": (110, 60, 45, 255),
    },
    {
        "name": "Dark skin, afro, yellow shirt",
        "skin": (120, 78, 50, 255),
        "skin_shade": (95, 60, 38, 255),
        "skin_dark": (78, 48, 30, 255),
        "hair": (28, 22, 18, 255),
        "hair_shade": (18, 14, 10, 255),
        "hair_highlight": (42, 35, 28, 255),
        "shirt": (210, 185, 60, 255),
        "shirt_shade": (175, 152, 42, 255),
        "shirt_highlight": (230, 205, 82, 255),
        "pants": (60, 58, 72, 255),
        "pants_shade": (44, 42, 55, 255),
        "shoes": (48, 38, 32, 255),
        "shoes_shade": (34, 26, 22, 255),
        "outline": (22, 18, 15, 255),
        "eye": (22, 22, 28, 255),
        "eye_white": (232, 232, 232, 255),
        "mouth": (95, 50, 35, 255),
    },
    {
        "name": "Light skin, blonde hair, purple shirt",
        "skin": (235, 200, 168, 255),
        "skin_shade": (210, 175, 142, 255),
        "skin_dark": (190, 155, 125, 255),
        "hair": (220, 185, 100, 255),
        "hair_shade": (190, 155, 75, 255),
        "hair_highlight": (240, 210, 130, 255),
        "shirt": (140, 80, 170, 255),
        "shirt_shade": (110, 58, 135, 255),
        "shirt_highlight": (165, 105, 195, 255),
        "pants": (68, 68, 82, 255),
        "pants_shade": (50, 50, 62, 255),
        "shoes": (52, 42, 38, 255),
        "shoes_shade": (38, 30, 26, 255),
        "outline": (30, 25, 22, 255),
        "eye": (25, 25, 30, 255),
        "eye_white": (240, 240, 240, 255),
        "mouth": (170, 100, 90, 255),
    },
    {
        "name": "Medium skin, auburn hair, teal shirt",
        "skin": (205, 165, 125, 255),
        "skin_shade": (180, 140, 102, 255),
        "skin_dark": (158, 120, 85, 255),
        "hair": (150, 65, 30, 255),
        "hair_shade": (115, 45, 20, 255),
        "hair_highlight": (178, 88, 45, 255),
        "shirt": (45, 155, 155, 255),
        "shirt_shade": (32, 120, 120, 255),
        "shirt_highlight": (65, 178, 178, 255),
        "pants": (62, 62, 78, 255),
        "pants_shade": (45, 45, 58, 255),
        "shoes": (50, 40, 35, 255),
        "shoes_shade": (36, 28, 24, 255),
        "outline": (28, 22, 20, 255),
        "eye": (25, 25, 30, 255),
        "eye_white": (240, 240, 240, 255),
        "mouth": (155, 85, 72, 255),
    },
    {
        "name": "Medium-dark skin, dark hair, orange shirt",
        "skin": (165, 115, 78, 255),
        "skin_shade": (140, 92, 60, 255),
        "skin_dark": (118, 78, 48, 255),
        "hair": (32, 26, 22, 255),
        "hair_shade": (20, 16, 14, 255),
        "hair_highlight": (48, 40, 34, 255),
        "shirt": (215, 130, 45, 255),
        "shirt_shade": (180, 105, 32, 255),
        "shirt_highlight": (235, 155, 68, 255),
        "pants": (58, 58, 72, 255),
        "pants_shade": (42, 42, 55, 255),
        "shoes": (48, 38, 32, 255),
        "shoes_shade": (34, 26, 22, 255),
        "outline": (24, 20, 18, 255),
        "eye": (22, 22, 28, 255),
        "eye_white": (235, 235, 235, 255),
        "mouth": (128, 68, 48, 255),
    },
    {
        "name": "Light skin, red hair, white shirt",
        "skin": (240, 210, 180, 255),
        "skin_shade": (215, 185, 155, 255),
        "skin_dark": (195, 165, 138, 255),
        "hair": (180, 55, 30, 255),
        "hair_shade": (140, 38, 20, 255),
        "hair_highlight": (210, 78, 48, 255),
        "shirt": (225, 225, 230, 255),
        "shirt_shade": (190, 190, 198, 255),
        "shirt_highlight": (242, 242, 245, 255),
        "pants": (70, 70, 85, 255),
        "pants_shade": (52, 52, 65, 255),
        "shoes": (55, 45, 40, 255),
        "shoes_shade": (40, 32, 28, 255),
        "outline": (30, 25, 22, 255),
        "eye": (25, 25, 30, 255),
        "eye_white": (240, 240, 240, 255),
        "mouth": (175, 105, 95, 255),
    },
]

# ---------------------------------------------------------------------------
# HAIR STYLES — pixel masks for 32x48 head region
#
# Head center is roughly x=15, y=10 (large chibi head).
# Each style returns {"down": [...], "up": [...], "left": [...], "right": [...]}
# where each value is a list of (x, y, shade) tuples.
# shade: 0 = base hair, 1 = hair_shade (dark), 2 = hair_highlight (light)
# ---------------------------------------------------------------------------

def _hair_row(y, x_start, x_end, shade=0):
    """Helper: generate a horizontal run of hair pixels."""
    return [(x, y, shade) for x in range(x_start, x_end)]


def _make_hair_short():
    front = []
    front += _hair_row(2, 10, 22, 2)
    front += _hair_row(3, 8, 24, 0)
    front += _hair_row(4, 7, 25, 0)
    front += _hair_row(5, 7, 25, 1)
    front += [(7, 6, 1), (24, 6, 1)]

    back = []
    back += _hair_row(2, 10, 22, 1)
    back += _hair_row(3, 8, 24, 1)
    back += _hair_row(4, 7, 25, 1)
    back += _hair_row(5, 7, 25, 1)
    back += _hair_row(6, 7, 25, 1)
    back += _hair_row(7, 8, 24, 1)

    left = []
    left += _hair_row(2, 9, 20, 2)
    left += _hair_row(3, 7, 21, 0)
    left += _hair_row(4, 6, 21, 0)
    left += _hair_row(5, 6, 21, 1)
    left += [(6, 6, 1), (6, 7, 1)]

    right = [(FRAME_W - 1 - x, y, s) for x, y, s in left]
    return {"down": front, "up": back, "left": left, "right": right}


def _make_hair_long():
    front = []
    front += _hair_row(2, 10, 22, 2)
    front += _hair_row(3, 8, 24, 0)
    front += _hair_row(4, 7, 25, 0)
    front += _hair_row(5, 7, 25, 1)
    for y in range(6, 26):
        front += [(7, y, 1), (24, y, 1)]
    for y in range(6, 22):
        front += [(6, y, 1), (25, y, 1)]

    back = []
    back += _hair_row(2, 10, 22, 1)
    back += _hair_row(3, 8, 24, 1)
    for y in range(4, 10):
        back += _hair_row(y, 7, 25, 1)
    for y in range(10, 26):
        back += _hair_row(y, 8, 24, 1)
    for y in range(26, 30):
        back += _hair_row(y, 10, 22, 1)

    left = []
    left += _hair_row(2, 9, 20, 2)
    left += _hair_row(3, 7, 21, 0)
    left += _hair_row(4, 6, 21, 0)
    left += _hair_row(5, 6, 21, 1)
    for y in range(6, 26):
        left += [(6, y, 1)]
    for y in range(6, 20):
        left += [(5, y, 1)]

    right = [(FRAME_W - 1 - x, y, s) for x, y, s in left]
    return {"down": front, "up": back, "left": left, "right": right}


def _make_hair_afro():
    front = []
    front += _hair_row(0, 11, 21, 2)
    front += _hair_row(1, 8, 24, 2)
    front += _hair_row(2, 6, 26, 0)
    front += _hair_row(3, 5, 27, 0)
    front += _hair_row(4, 5, 27, 0)
    front += _hair_row(5, 5, 27, 1)
    front += _hair_row(6, 5, 27, 1)
    for y in range(7, 12):
        front += [(5, y, 1), (6, y, 1), (25, y, 1), (26, y, 1)]

    back = []
    back += _hair_row(0, 11, 21, 1)
    back += _hair_row(1, 8, 24, 1)
    for y in range(2, 14):
        back += _hair_row(y, 5, 27, 1)
    back += _hair_row(14, 7, 25, 1)

    left = []
    left += _hair_row(0, 9, 19, 2)
    left += _hair_row(1, 6, 21, 0)
    left += _hair_row(2, 4, 22, 0)
    left += _hair_row(3, 3, 22, 0)
    left += _hair_row(4, 3, 22, 1)
    left += _hair_row(5, 3, 22, 1)
    left += _hair_row(6, 3, 21, 1)
    for y in range(7, 12):
        left += [(3, y, 1), (4, y, 1)]

    right = [(FRAME_W - 1 - x, y, s) for x, y, s in left]
    return {"down": front, "up": back, "left": left, "right": right}


def _make_hair_ponytail():
    front = []
    front += _hair_row(2, 10, 22, 2)
    front += _hair_row(3, 8, 24, 0)
    front += _hair_row(4, 7, 25, 0)
    front += _hair_row(5, 7, 25, 1)
    front += [(7, 6, 1), (24, 6, 1)]

    back = []
    back += _hair_row(2, 10, 22, 1)
    back += _hair_row(3, 8, 24, 0)
    back += _hair_row(4, 7, 25, 0)
    back += _hair_row(5, 7, 25, 1)
    for y in range(6, 10):
        back += _hair_row(y, 13, 19, 1)
    for y in range(10, 28):
        back += _hair_row(y, 14, 18, 1)
    back += _hair_row(28, 15, 18, 1)

    left = []
    left += _hair_row(2, 9, 20, 2)
    left += _hair_row(3, 7, 21, 0)
    left += _hair_row(4, 6, 21, 0)
    left += _hair_row(5, 6, 21, 1)
    left += [(6, 6, 1)]

    right = [(FRAME_W - 1 - x, y, s) for x, y, s in left]
    return {"down": front, "up": back, "left": left, "right": right}


def _spike_triangle(tip_x, tip_y, base_y, half_width):
    """Generate pixels for a triangular spike from tip down to base_y."""
    pixels = []
    height = base_y - tip_y
    if height <= 0:
        return pixels
    for dy in range(height + 1):
        y = tip_y + dy
        progress = dy / height
        w = max(1, round(half_width * progress))
        for dx in range(-w, w + 1):
            pixels.append((tip_x + dx, y))
    return pixels


def _make_hair_spiky():
    """Spiky hair with sharp triangular points."""
    # Define spike tips: (tip_x, tip_y, base_y, half_width)
    spikes_front = [
        (10, -1, 5, 2),   # left spike
        (14,  -2, 4, 2),  # left-center spike (tallest)
        (18,  -1, 4, 2),  # center-right spike
        (22,  -2, 5, 2),  # right spike (tall)
        (12,   0, 4, 1),  # small fill spike
        (20,   0, 4, 1),  # small fill spike
    ]

    front = []
    for tx, ty, by, hw in spikes_front:
        for x, y in _spike_triangle(tx, ty, by, hw):
            if 0 <= x < FRAME_W and 0 <= y < FRAME_H:
                shade = 2 if y <= ty + 1 else (0 if y <= by - 2 else 1)
                front.append((x, y, shade))
    # Base hair mass
    front += _hair_row(4, 7, 25, 0)
    front += _hair_row(5, 7, 25, 1)
    front += [(7, 6, 1), (24, 6, 1)]

    spikes_back = [
        (10, -1, 5, 2),
        (14, -2, 4, 2),
        (18, -1, 4, 2),
        (22, -2, 5, 2),
        (12,  0, 4, 1),
        (20,  0, 4, 1),
    ]
    back = []
    for tx, ty, by, hw in spikes_back:
        for x, y in _spike_triangle(tx, ty, by, hw):
            if 0 <= x < FRAME_W and 0 <= y < FRAME_H:
                back.append((x, y, 1))
    back += _hair_row(4, 7, 25, 1)
    back += _hair_row(5, 7, 25, 1)
    back += _hair_row(6, 7, 25, 1)
    back += _hair_row(7, 8, 24, 1)

    spikes_left = [
        (8,  -1, 5, 2),
        (12, -2, 4, 2),
        (16, -1, 4, 2),
        (19, -2, 5, 1),
        (10,  0, 4, 1),
    ]
    left = []
    for tx, ty, by, hw in spikes_left:
        for x, y in _spike_triangle(tx, ty, by, hw):
            if 0 <= x < FRAME_W and 0 <= y < FRAME_H:
                shade = 2 if y <= ty + 1 else (0 if y <= by - 2 else 1)
                left.append((x, y, shade))
    left += _hair_row(4, 6, 21, 0)
    left += _hair_row(5, 6, 21, 1)
    left += [(6, 6, 1)]

    right = [(FRAME_W - 1 - x, y, s) for x, y, s in left]
    return {"down": front, "up": back, "left": left, "right": right}


HAIR_STYLES = {
    "short": _make_hair_short(),
    "long": _make_hair_long(),
    "afro": _make_hair_afro(),
    "ponytail": _make_hair_ponytail(),
    "spiky": _make_hair_spiky(),
}

DEFAULT_HAIR = ["short", "short", "short", "afro", "long", "ponytail", "spiky", "long"]


# ---------------------------------------------------------------------------
# BODY TEMPLATES — 32x48 pixel art
#
# Coordinate system:
#   Head:     y  2-18  (large chibi head, ~17px tall)
#   Neck:     y 19-20
#   Torso:    y 21-32  (shirt + arms)
#   Arms:     y 21-31  (skin-toned, extend alongside torso)
#   Legs:     y 33-42  (pants)
#   Feet:     y 43-47  (shoes)
#
# Arms are LONGER than before — they extend from shoulders (y=21)
# down to y=31, giving clear swing during walk and big reach for interact.
# ---------------------------------------------------------------------------

def _oval_outline(cx, cy, rx, ry):
    """Generate pixel positions for an oval outline."""
    points = set()
    for angle_step in range(360):
        a = math.radians(angle_step)
        x = round(cx + rx * math.cos(a))
        y = round(cy + ry * math.sin(a))
        points.add((x, y))
    return sorted(points)


def _filled_oval(cx, cy, rx, ry):
    """Generate pixel positions for a filled oval."""
    points = []
    for y in range(cy - ry, cy + ry + 1):
        for x in range(cx - rx, cx + rx + 1):
            dx = (x - cx) / max(rx, 0.1)
            dy = (y - cy) / max(ry, 0.1)
            if dx * dx + dy * dy <= 1.0:
                points.append((x, y))
    return points


def _build_head_pixels(cx, cy, rx, ry, facing):
    """Build head pixels with shading based on facing direction."""
    pixels = []
    outline_pts = set(_oval_outline(cx, cy, rx, ry))
    fill_pts = set((x, y) for x, y in _filled_oval(cx, cy, rx, ry))
    inner_pts = fill_pts - outline_pts

    for x, y in outline_pts:
        if 0 <= x < FRAME_W and 0 <= y < FRAME_H:
            pixels.append((x, y, "outline"))

    for x, y in inner_pts:
        if 0 <= x < FRAME_W and 0 <= y < FRAME_H:
            if facing == "down":
                if y >= cy + 4:
                    pixels.append((x, y, "skin_shade"))
                else:
                    pixels.append((x, y, "skin"))
            elif facing == "up":
                if y >= cy + 3:
                    pixels.append((x, y, "skin_dark"))
                else:
                    pixels.append((x, y, "skin_shade"))
            elif facing == "left":
                if x >= cx + 3 or y >= cy + 4:
                    pixels.append((x, y, "skin_shade"))
                else:
                    pixels.append((x, y, "skin"))
            else:  # right — mirror of left
                if x <= cx - 3 or y >= cy + 4:
                    pixels.append((x, y, "skin_shade"))
                else:
                    pixels.append((x, y, "skin"))

    return pixels


def _build_body_down():
    """Facing down (toward camera) — 32x48."""
    pixels = []
    head_cx, head_cy = 15, 10

    # --- Head ---
    pixels += _build_head_pixels(head_cx, head_cy, 8, 8, "down")

    # Eyes (y=11)
    eye_y = 11
    for ex, ey, c in [
        (11, eye_y, "eye_white"), (12, eye_y, "eye_white"), (13, eye_y, "eye"),
        (11, eye_y+1, "eye_white"), (12, eye_y+1, "eye"), (13, eye_y+1, "outline"),
        (17, eye_y, "eye_white"), (18, eye_y, "eye_white"), (19, eye_y, "eye"),
        (17, eye_y+1, "eye_white"), (18, eye_y+1, "eye"), (19, eye_y+1, "outline"),
    ]:
        pixels.append((ex, ey, c))

    # Mouth (small, centered, y=15)
    pixels.append((14, 15, "mouth"))
    pixels.append((15, 15, "mouth"))
    pixels.append((16, 15, "mouth"))
    pixels.append((14, 16, "outline"))
    pixels.append((15, 16, "skin_shade"))
    pixels.append((16, 16, "outline"))

    # --- Neck ---
    for y in range(19, 21):
        pixels.append((12, y, "outline"))
        for x in range(13, 18):
            pixels.append((x, y, "skin_shade"))
        pixels.append((18, y, "outline"))

    # --- Torso + Arms (y=21-32) ---
    # Row 21-22: shoulders
    for y in [21, 22]:
        pixels.append((8, y, "outline"))
        for x in range(9, 12):
            pixels.append((x, y, "skin"))
        for x in range(12, 20):
            pixels.append((x, y, "shirt_highlight" if y == 21 else "shirt"))
        for x in range(20, 23):
            pixels.append((x, y, "skin"))
        pixels.append((23, y, "outline"))

    # Row 23-27: upper arm + torso
    for y in range(23, 28):
        pixels.append((7, y, "outline"))
        for x in range(8, 11):
            pixels.append((x, y, "skin" if y < 26 else "skin_shade"))
        pixels.append((11, y, "outline"))
        for x in range(12, 20):
            c = "shirt" if y < 26 else "shirt_shade"
            pixels.append((x, y, c))
        pixels.append((20, y, "outline"))
        for x in range(21, 24):
            pixels.append((x, y, "skin" if y < 26 else "skin_shade"))
        pixels.append((24, y, "outline"))

    # Row 28-30: forearm (narrower) + lower torso
    for y in range(28, 31):
        pixels.append((7, y, "outline"))
        pixels.append((8, y, "skin_shade"))
        pixels.append((9, y, "skin_shade"))
        pixels.append((10, y, "outline"))
        for x in range(11, 21):
            pixels.append((x, y, "shirt_shade"))
        pixels.append((21, y, "outline"))
        pixels.append((22, y, "skin_shade"))
        pixels.append((23, y, "skin_shade"))
        pixels.append((24, y, "outline"))

    # Row 31: hand tips
    pixels.append((7, 31, "outline"))
    pixels.append((8, 31, "skin_dark"))
    pixels.append((9, 31, "outline"))
    for x in range(10, 22):
        pixels.append((x, 31, "shirt_shade"))
    pixels.append((22, 31, "outline"))
    pixels.append((23, 31, "skin_dark"))
    pixels.append((24, 31, "outline"))

    # Row 32: waistline
    pixels.append((10, 32, "outline"))
    for x in range(11, 21):
        pixels.append((x, 32, "shirt_shade"))
    pixels.append((21, 32, "outline"))

    # --- Legs ---
    for y in range(33, 38):
        pixels.append((10, y, "outline"))
        for x in range(11, 15):
            pixels.append((x, y, "pants"))
        pixels.append((15, y, "outline"))
        pixels.append((16, y, "outline"))
        for x in range(17, 21):
            pixels.append((x, y, "pants"))
        pixels.append((21, y, "outline"))

    for y in range(38, 43):
        pixels.append((10, y, "outline"))
        for x in range(11, 15):
            pixels.append((x, y, "pants_shade"))
        pixels.append((15, y, "outline"))
        pixels.append((16, y, "outline"))
        for x in range(17, 21):
            pixels.append((x, y, "pants_shade"))
        pixels.append((21, y, "outline"))

    # --- Feet ---
    for y in range(43, 46):
        pixels.append((9, y, "outline"))
        for x in range(10, 15):
            pixels.append((x, y, "shoes" if y < 45 else "shoes_shade"))
        pixels.append((15, y, "outline"))
        pixels.append((16, y, "outline"))
        for x in range(17, 22):
            pixels.append((x, y, "shoes" if y < 45 else "shoes_shade"))
        pixels.append((22, y, "outline"))
    for x in range(9, 23):
        pixels.append((x, 46, "outline"))

    return pixels


def _build_body_up():
    """Facing up (away from camera) — 32x48."""
    pixels = []
    head_cx, head_cy = 15, 10

    # --- Head (back, no eyes, no mouth) ---
    pixels += _build_head_pixels(head_cx, head_cy, 8, 8, "up")

    # --- Neck ---
    for y in range(19, 21):
        pixels.append((12, y, "outline"))
        for x in range(13, 18):
            pixels.append((x, y, "skin_dark"))
        pixels.append((18, y, "outline"))

    # --- Torso (back view) ---
    for y in [21, 22]:
        pixels.append((8, y, "outline"))
        for x in range(9, 12):
            pixels.append((x, y, "skin_shade"))
        for x in range(12, 20):
            pixels.append((x, y, "shirt" if y == 21 else "shirt_shade"))
        for x in range(20, 23):
            pixels.append((x, y, "skin_shade"))
        pixels.append((23, y, "outline"))

    for y in range(23, 28):
        pixels.append((7, y, "outline"))
        for x in range(8, 11):
            pixels.append((x, y, "skin_shade"))
        pixels.append((11, y, "outline"))
        for x in range(12, 20):
            pixels.append((x, y, "shirt_shade"))
        pixels.append((20, y, "outline"))
        for x in range(21, 24):
            pixels.append((x, y, "skin_shade"))
        pixels.append((24, y, "outline"))

    for y in range(28, 31):
        pixels.append((7, y, "outline"))
        pixels.append((8, y, "skin_dark"))
        pixels.append((9, y, "skin_dark"))
        pixels.append((10, y, "outline"))
        for x in range(11, 21):
            pixels.append((x, y, "shirt_shade"))
        pixels.append((21, y, "outline"))
        pixels.append((22, y, "skin_dark"))
        pixels.append((23, y, "skin_dark"))
        pixels.append((24, y, "outline"))

    pixels.append((7, 31, "outline"))
    pixels.append((8, 31, "skin_dark"))
    pixels.append((9, 31, "outline"))
    for x in range(10, 22):
        pixels.append((x, 31, "shirt_shade"))
    pixels.append((22, 31, "outline"))
    pixels.append((23, 31, "skin_dark"))
    pixels.append((24, 31, "outline"))

    pixels.append((10, 32, "outline"))
    for x in range(11, 21):
        pixels.append((x, 32, "shirt_shade"))
    pixels.append((21, 32, "outline"))

    # --- Legs ---
    for y in range(33, 43):
        pixels.append((10, y, "outline"))
        for x in range(11, 15):
            pixels.append((x, y, "pants_shade"))
        pixels.append((15, y, "outline"))
        pixels.append((16, y, "outline"))
        for x in range(17, 21):
            pixels.append((x, y, "pants_shade"))
        pixels.append((21, y, "outline"))

    # --- Feet ---
    for y in range(43, 46):
        pixels.append((9, y, "outline"))
        for x in range(10, 15):
            pixels.append((x, y, "shoes_shade"))
        pixels.append((15, y, "outline"))
        pixels.append((16, y, "outline"))
        for x in range(17, 22):
            pixels.append((x, y, "shoes_shade"))
        pixels.append((22, y, "outline"))
    for x in range(9, 23):
        pixels.append((x, 46, "outline"))

    return pixels


def _build_body_left():
    """Facing left — side profile, 32x48."""
    pixels = []
    head_cx, head_cy = 14, 10

    # --- Head (side) ---
    pixels += _build_head_pixels(head_cx, head_cy, 7, 8, "left")

    # Eye (one visible)
    pixels.append((10, 11, "eye_white"))
    pixels.append((11, 11, "eye_white"))
    pixels.append((12, 11, "eye"))
    pixels.append((10, 12, "eye_white"))
    pixels.append((11, 12, "eye"))
    pixels.append((12, 12, "outline"))

    # Mouth (side — smaller, shifted left)
    pixels.append((10, 15, "mouth"))
    pixels.append((11, 15, "mouth"))
    pixels.append((10, 16, "outline"))
    pixels.append((11, 16, "outline"))

    # --- Neck ---
    for y in range(19, 21):
        pixels.append((11, y, "outline"))
        for x in range(12, 17):
            pixels.append((x, y, "skin_shade"))
        pixels.append((17, y, "outline"))

    # --- Torso (side) + Arms ---
    for y in [21, 22]:
        pixels.append((7, y, "outline"))
        for x in range(8, 11):
            pixels.append((x, y, "skin"))
        for x in range(11, 19):
            pixels.append((x, y, "shirt" if y == 21 else "shirt_shade"))
        for x in range(19, 22):
            pixels.append((x, y, "skin_shade"))
        pixels.append((22, y, "outline"))

    for y in range(23, 28):
        pixels.append((6, y, "outline"))
        for x in range(7, 10):
            pixels.append((x, y, "skin" if y < 26 else "skin_shade"))
        pixels.append((10, y, "outline"))
        for x in range(11, 19):
            c = "shirt" if y < 26 else "shirt_shade"
            pixels.append((x, y, c))
        pixels.append((19, y, "outline"))
        for x in range(20, 23):
            pixels.append((x, y, "skin_shade"))
        pixels.append((23, y, "outline"))

    for y in range(28, 31):
        pixels.append((6, y, "outline"))
        pixels.append((7, y, "skin_shade"))
        pixels.append((8, y, "skin_shade"))
        pixels.append((9, y, "outline"))
        for x in range(10, 20):
            pixels.append((x, y, "shirt_shade"))
        pixels.append((20, y, "outline"))
        pixels.append((21, y, "skin_dark"))
        pixels.append((22, y, "skin_dark"))
        pixels.append((23, y, "outline"))

    pixels.append((6, 31, "outline"))
    pixels.append((7, 31, "skin_dark"))
    pixels.append((8, 31, "outline"))
    for x in range(9, 21):
        pixels.append((x, 31, "shirt_shade"))
    pixels.append((21, 31, "outline"))
    pixels.append((22, 31, "skin_dark"))
    pixels.append((23, 31, "outline"))

    pixels.append((9, 32, "outline"))
    for x in range(10, 20):
        pixels.append((x, 32, "shirt_shade"))
    pixels.append((20, 32, "outline"))

    # --- Legs (side) ---
    for y in range(33, 38):
        pixels.append((9, y, "outline"))
        for x in range(10, 15):
            pixels.append((x, y, "pants"))
        pixels.append((15, y, "outline"))
        for x in range(16, 20):
            pixels.append((x, y, "pants_shade"))
        pixels.append((20, y, "outline"))

    for y in range(38, 43):
        pixels.append((9, y, "outline"))
        for x in range(10, 15):
            pixels.append((x, y, "pants_shade"))
        pixels.append((15, y, "outline"))
        for x in range(16, 20):
            pixels.append((x, y, "pants_shade"))
        pixels.append((20, y, "outline"))

    # --- Feet (side) ---
    for y in range(43, 46):
        pixels.append((7, y, "outline"))
        for x in range(8, 15):
            pixels.append((x, y, "shoes" if y < 45 else "shoes_shade"))
        pixels.append((15, y, "outline"))
    for x in range(7, 16):
        pixels.append((x, 46, "outline"))

    return pixels


def _build_body_right():
    """Facing right — mirror of left."""
    left = _build_body_left()
    return [(FRAME_W - 1 - x, y, c) for x, y, c in left]


BODY_TEMPLATES = {
    "down": _build_body_down(),
    "up": _build_body_up(),
    "left": _build_body_left(),
    "right": _build_body_right(),
}


# ---------------------------------------------------------------------------
# ANIMATION REGION CLASSIFICATION
# ---------------------------------------------------------------------------

def _region_for_pixel(x, y, direction):
    """Classify a pixel into an animation region for 32x48 layout."""
    if y <= 18:
        return "head"
    if y <= 20:
        return "torso"  # neck moves with torso
    if y <= 32:
        if direction in ("down", "up"):
            if x <= 11:
                return "arm_l"
            if x >= 20:
                return "arm_r"
        elif direction == "left":
            if x <= 10:
                return "arm_l"
            if x >= 19:
                return "arm_r"
        elif direction == "right":
            if x >= FRAME_W - 1 - 10:
                return "arm_r"
            if x <= FRAME_W - 1 - 19:
                return "arm_l"
        return "torso"
    if direction in ("down", "up"):
        if x <= 15:
            return "leg_l"
        return "leg_r"
    else:
        if y <= 42:
            return "leg_l"
        return "leg_r"


# ---------------------------------------------------------------------------
# ANIMATION OFFSET TABLES — 32x48
#
# Longer arms means bigger swing for walk and much bigger reach for interact.
# ---------------------------------------------------------------------------

ANIM_OFFSETS = {
    "walk": {
        "down": {
            "head":  [(0, 0), (0, -1), (0, 0), (0, -1)],
            "torso": [(0, 0), (0, 0),  (0, 0), (0, 0)],
            "arm_l": [(0, 0), (0, -3), (0, 0), (0, 3)],
            "arm_r": [(0, 0), (0, 3),  (0, 0), (0, -3)],
            "leg_l": [(0, 0), (0, 2),  (0, 0), (0, -2)],
            "leg_r": [(0, 0), (0, -2), (0, 0), (0, 2)],
        },
        "up": {
            "head":  [(0, 0), (0, -1), (0, 0), (0, -1)],
            "torso": [(0, 0), (0, 0),  (0, 0), (0, 0)],
            "arm_l": [(0, 0), (0, -3), (0, 0), (0, 3)],
            "arm_r": [(0, 0), (0, 3),  (0, 0), (0, -3)],
            "leg_l": [(0, 0), (0, 2),  (0, 0), (0, -2)],
            "leg_r": [(0, 0), (0, -2), (0, 0), (0, 2)],
        },
        "left": {
            "head":  [(0, 0), (0, -1), (0, 0), (0, -1)],
            "torso": [(0, 0), (0, 0),  (0, 0), (0, 0)],
            "arm_l": [(0, 0), (0, 3),  (0, 0), (0, -3)],
            "arm_r": [(0, 0), (0, -3), (0, 0), (0, 3)],
            "leg_l": [(0, 0), (0, 2),  (0, 0), (0, -2)],
            "leg_r": [(0, 0), (0, -2), (0, 0), (0, 2)],
        },
        "right": {
            "head":  [(0, 0), (0, -1), (0, 0), (0, -1)],
            "torso": [(0, 0), (0, 0),  (0, 0), (0, 0)],
            "arm_l": [(0, 0), (0, -3), (0, 0), (0, 3)],
            "arm_r": [(0, 0), (0, 3),  (0, 0), (0, -3)],
            "leg_l": [(0, 0), (0, 2),  (0, 0), (0, -2)],
            "leg_r": [(0, 0), (0, -2), (0, 0), (0, 2)],
        },
    },

    "jump": {
        "down": {
            "head":  [(0, 2),  (0, -2), (0, -4), (0, 0)],
            "torso": [(0, 2),  (0, -2), (0, -4), (0, 0)],
            "arm_l": [(0, 2),  (0, -3), (0, -5), (0, 0)],
            "arm_r": [(0, 2),  (0, -3), (0, -5), (0, 0)],
            "leg_l": [(0, 2),  (0, 0),  (0, -2), (0, 2)],
            "leg_r": [(0, 2),  (0, 0),  (0, -2), (0, 2)],
        },
        "up": {
            "head":  [(0, 2),  (0, -2), (0, -4), (0, 0)],
            "torso": [(0, 2),  (0, -2), (0, -4), (0, 0)],
            "arm_l": [(0, 2),  (0, -3), (0, -5), (0, 0)],
            "arm_r": [(0, 2),  (0, -3), (0, -5), (0, 0)],
            "leg_l": [(0, 2),  (0, 0),  (0, -2), (0, 2)],
            "leg_r": [(0, 2),  (0, 0),  (0, -2), (0, 2)],
        },
        "left": {
            "head":  [(0, 2),  (0, -2), (0, -4), (0, 0)],
            "torso": [(0, 2),  (0, -2), (0, -4), (0, 0)],
            "arm_l": [(0, 2),  (0, -3), (0, -5), (0, 0)],
            "arm_r": [(0, 2),  (0, -3), (0, -5), (0, 0)],
            "leg_l": [(0, 2),  (0, 0),  (0, -2), (0, 2)],
            "leg_r": [(0, 2),  (0, 0),  (0, -2), (0, 2)],
        },
        "right": {
            "head":  [(0, 2),  (0, -2), (0, -4), (0, 0)],
            "torso": [(0, 2),  (0, -2), (0, -4), (0, 0)],
            "arm_l": [(0, 2),  (0, -3), (0, -5), (0, 0)],
            "arm_r": [(0, 2),  (0, -3), (0, -5), (0, 0)],
            "leg_l": [(0, 2),  (0, 0),  (0, -2), (0, 2)],
            "leg_r": [(0, 2),  (0, 0),  (0, -2), (0, 2)],
        },
    },

    "crouch": {
        "down": {
            "head":  [(0, 0), (0, 2),  (0, 4),  (0, 2)],
            "torso": [(0, 0), (0, 2),  (0, 3),  (0, 2)],
            "arm_l": [(0, 0), (0, 2),  (0, 3),  (0, 2)],
            "arm_r": [(0, 0), (0, 2),  (0, 3),  (0, 2)],
            "leg_l": [(0, 0), (0, 1),  (0, 2),  (0, 1)],
            "leg_r": [(0, 0), (0, 1),  (0, 2),  (0, 1)],
        },
        "up": {
            "head":  [(0, 0), (0, 2),  (0, 4),  (0, 2)],
            "torso": [(0, 0), (0, 2),  (0, 3),  (0, 2)],
            "arm_l": [(0, 0), (0, 2),  (0, 3),  (0, 2)],
            "arm_r": [(0, 0), (0, 2),  (0, 3),  (0, 2)],
            "leg_l": [(0, 0), (0, 1),  (0, 2),  (0, 1)],
            "leg_r": [(0, 0), (0, 1),  (0, 2),  (0, 1)],
        },
        "left": {
            "head":  [(0, 0), (0, 2),  (0, 4),  (0, 2)],
            "torso": [(0, 0), (0, 2),  (0, 3),  (0, 2)],
            "arm_l": [(0, 0), (0, 2),  (0, 3),  (0, 2)],
            "arm_r": [(0, 0), (0, 2),  (0, 3),  (0, 2)],
            "leg_l": [(0, 0), (0, 1),  (0, 2),  (0, 1)],
            "leg_r": [(0, 0), (0, 1),  (0, 2),  (0, 1)],
        },
        "right": {
            "head":  [(0, 0), (0, 2),  (0, 4),  (0, 2)],
            "torso": [(0, 0), (0, 2),  (0, 3),  (0, 2)],
            "arm_l": [(0, 0), (0, 2),  (0, 3),  (0, 2)],
            "arm_r": [(0, 0), (0, 2),  (0, 3),  (0, 2)],
            "leg_l": [(0, 0), (0, 1),  (0, 2),  (0, 1)],
            "leg_r": [(0, 0), (0, 1),  (0, 2),  (0, 1)],
        },
    },

    # Interact: the leading arm reaches OUT from the body and UP.
    # Longer arms make this a dramatic, clear gesture.
    "interact": {
        "down": {
            "head":  [(0, 0), (0, 0),  (0, 0),  (0, 0)],
            "torso": [(0, 0), (0, 0),  (0, 0),  (0, 0)],
            "arm_l": [(0, 0), (0, 0),  (0, 0),  (0, 0)],
            "arm_r": [(0, 0), (3, -3), (5, -6), (3, -3)],
            "leg_l": [(0, 0), (0, 0),  (0, 0),  (0, 0)],
            "leg_r": [(0, 0), (0, 0),  (0, 0),  (0, 0)],
        },
        "up": {
            "head":  [(0, 0), (0, 0),  (0, 0),  (0, 0)],
            "torso": [(0, 0), (0, 0),  (0, 0),  (0, 0)],
            "arm_l": [(0, 0), (0, 0),  (0, 0),  (0, 0)],
            "arm_r": [(0, 0), (3, -3), (5, -6), (3, -3)],
            "leg_l": [(0, 0), (0, 0),  (0, 0),  (0, 0)],
            "leg_r": [(0, 0), (0, 0),  (0, 0),  (0, 0)],
        },
        "left": {
            "head":  [(0, 0), (0, 0),   (0, 0),   (0, 0)],
            "torso": [(0, 0), (0, 0),   (0, 0),   (0, 0)],
            "arm_l": [(0, 0), (-3, -3), (-5, -6), (-3, -3)],
            "arm_r": [(0, 0), (0, 0),   (0, 0),   (0, 0)],
            "leg_l": [(0, 0), (0, 0),   (0, 0),   (0, 0)],
            "leg_r": [(0, 0), (0, 0),   (0, 0),   (0, 0)],
        },
        "right": {
            "head":  [(0, 0), (0, 0),  (0, 0),  (0, 0)],
            "torso": [(0, 0), (0, 0),  (0, 0),  (0, 0)],
            "arm_l": [(0, 0), (0, 0),  (0, 0),  (0, 0)],
            "arm_r": [(0, 0), (3, -3), (5, -6), (3, -3)],
            "leg_l": [(0, 0), (0, 0),  (0, 0),  (0, 0)],
            "leg_r": [(0, 0), (0, 0),  (0, 0),  (0, 0)],
        },
    },
}


# ---------------------------------------------------------------------------
# RENDERING
# ---------------------------------------------------------------------------

def render_frame(direction: str, frame_idx: int, palette: dict,
                 hair_style: str, animation: str = "walk") -> Image.Image:
    """Render a single 32x48 frame."""
    img = Image.new("RGBA", (FRAME_W, FRAME_H), (0, 0, 0, 0))

    body_pixels = BODY_TEMPLATES[direction]
    offsets = ANIM_OFFSETS[animation][direction]

    for bx, by, color_key in body_pixels:
        region = _region_for_pixel(bx, by, direction)
        dx, dy = offsets[region][frame_idx]
        px, py = bx + dx, by + dy
        if 0 <= px < FRAME_W and 0 <= py < FRAME_H:
            img.putpixel((px, py), palette[color_key])

    # Hair
    hair_data = HAIR_STYLES.get(hair_style, HAIR_STYLES["short"])
    hair_pixels = hair_data.get(direction, [])
    head_dx, head_dy = offsets["head"][frame_idx]
    shade_map = {0: "hair", 1: "hair_shade", 2: "hair_highlight"}
    for hx, hy, shade in hair_pixels:
        px, py = hx + head_dx, hy + head_dy
        if 0 <= px < FRAME_W and 0 <= py < FRAME_H:
            img.putpixel((px, py), palette[shade_map[shade]])

    return img


def build_spritesheet(palette: dict, hair_style: str = "short") -> tuple[Image.Image, dict]:
    """Build the full spritesheet with all animations."""
    cols = FRAMES_PER_DIR
    rows = len(ANIMATIONS) * len(DIRECTIONS)
    sheet_w = cols * FRAME_W
    sheet_h = rows * FRAME_H

    sheet = Image.new("RGBA", (sheet_w, sheet_h), (0, 0, 0, 0))
    frames_meta: dict = {}

    row = 0
    for anim in ANIMATIONS:
        for direction in DIRECTIONS:
            for col in range(FRAMES_PER_DIR):
                frame_img = render_frame(direction, col, palette, hair_style, anim)
                x = col * FRAME_W
                y = row * FRAME_H
                sheet.paste(frame_img, (x, y))

                frame_name = f"{anim}_{direction}_{col}"
                frames_meta[frame_name] = {
                    "frame": {"x": x, "y": y, "w": FRAME_W, "h": FRAME_H},
                    "rotated": False,
                    "trimmed": False,
                    "spriteSourceSize": {"x": 0, "y": 0, "w": FRAME_W, "h": FRAME_H},
                    "sourceSize": {"w": FRAME_W, "h": FRAME_H},
                }
            row += 1

    return sheet, frames_meta


def build_atlas(sprite_name: str, image_file: str, frames_meta: dict, sheet_size: tuple[int, int]) -> dict:
    """Build a Phaser-compatible JSON texture atlas."""
    anim_groups = {}
    for anim in ANIMATIONS:
        for direction in DIRECTIONS:
            key = f"{anim}_{direction}"
            anim_groups[key] = [f"{anim}_{direction}_{i}" for i in range(FRAMES_PER_DIR)]

    return {
        "frames": frames_meta,
        "animations": anim_groups,
        "meta": {
            "app": "sprite-generator",
            "version": "5.0",
            "image": image_file,
            "format": "RGBA8888",
            "size": {"w": sheet_size[0], "h": sheet_size[1]},
            "scale": "1",
            "frameSize": {"w": FRAME_W, "h": FRAME_H},
            "tileSize": TILE_SIZE,
            "spriteTiles": {"w": 1, "h": 1.5},
        },
    }


def build_preview_html(sprite_name: str, image_file: str, atlas_file: str) -> str:
    """Generate a standalone HTML preview."""
    animations_json = json.dumps(ANIMATIONS)
    directions_json = json.dumps(DIRECTIONS)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{sprite_name} — Sprite Preview</title>
<style>
  body {{
    background: #1a1a2e;
    color: #eee;
    font-family: monospace;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 2rem;
  }}
  h1 {{ margin-bottom: 0.5rem; }}
  .info {{ color: #888; margin-bottom: 1rem; }}
  canvas {{
    image-rendering: pixelated;
    image-rendering: crisp-edges;
    border: 1px solid #444;
    margin-bottom: 1rem;
  }}
  .controls {{
    display: flex;
    gap: 0.5rem;
    margin-bottom: 0.75rem;
    flex-wrap: wrap;
    justify-content: center;
  }}
  .controls label {{
    color: #888;
    margin-right: 0.5rem;
    line-height: 2;
  }}
  button {{
    background: #333;
    color: #eee;
    border: 1px solid #555;
    padding: 0.4rem 0.8rem;
    cursor: pointer;
    font-family: monospace;
    font-size: 0.85rem;
  }}
  button:hover {{ background: #555; }}
  button.active {{ background: #0a7; color: #fff; }}
  .sheet-preview {{
    margin-top: 1rem;
    border: 1px solid #333;
  }}
</style>
</head>
<body>
<h1>{sprite_name}</h1>
<p class="info">v5 — 32x48 chibi (1x1.5 tiles on 32px grid) — walk / jump / crouch / interact</p>

<canvas id="anim" width="{FRAME_W * 6}" height="{FRAME_H * 6}"></canvas>

<div class="controls" id="animBtns">
  <label>Anim:</label>
</div>
<div class="controls" id="dirBtns">
  <label>Dir:</label>
</div>

<p class="info">Full spritesheet:</p>
<img class="sheet-preview" id="sheetImg" />

<script>
const FRAME_W = {FRAME_W};
const FRAME_H = {FRAME_H};
const COLS = {FRAMES_PER_DIR};
const SCALE = 6;
const FPS = 6;
const ANIMATIONS = {animations_json};
const DIRECTIONS = {directions_json};
const DIRS_PER_ANIM = DIRECTIONS.length;

const canvas = document.getElementById("anim");
const ctx = canvas.getContext("2d");
ctx.imageSmoothingEnabled = false;

const img = new Image();
img.src = "{image_file}";

let animIdx = 0;
let dirIdx = 0;
let frameIdx = 0;

function getRow() {{
  return animIdx * DIRS_PER_ANIM + dirIdx;
}}

function makeButtons(containerId, labels, setter) {{
  const container = document.getElementById(containerId);
  labels.forEach((label, i) => {{
    const btn = document.createElement("button");
    btn.textContent = label;
    btn.dataset.idx = i;
    if (i === 0) btn.classList.add("active");
    btn.addEventListener("click", () => {{
      container.querySelectorAll("button").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      setter(i);
    }});
    container.appendChild(btn);
  }});
}}

makeButtons("animBtns", ANIMATIONS, i => {{ animIdx = i; }});
makeButtons("dirBtns", DIRECTIONS, i => {{ dirIdx = i; }});

img.onload = () => {{
  document.getElementById("sheetImg").src = "{image_file}";
  document.getElementById("sheetImg").style.width = (img.width * 3) + "px";
  setInterval(() => {{
    frameIdx = (frameIdx + 1) % COLS;
    const row = getRow();
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(
      img,
      frameIdx * FRAME_W, row * FRAME_H, FRAME_W, FRAME_H,
      0, 0, FRAME_W * SCALE, FRAME_H * SCALE
    );
  }}, 1000 / FPS);
}};
</script>
</body>
</html>"""


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Generate a 32x48 top-down character spritesheet.")
    parser.add_argument("--preset", type=int, default=0,
                        help=f"Palette preset index 0-{len(PRESETS)-1} (default: 0)")
    parser.add_argument("--hair", choices=list(HAIR_STYLES.keys()), default=None,
                        help="Hair style (default: depends on preset)")
    parser.add_argument("--name", default="player",
                        help="Sprite name used in filenames (default: player)")
    parser.add_argument("--list-presets", action="store_true",
                        help="List all available palette presets and exit")
    parser.add_argument("--all", action="store_true",
                        help="Generate one sprite per preset (for preview)")
    args = parser.parse_args()

    if args.list_presets:
        print("Available presets:")
        for i, p in enumerate(PRESETS):
            hair = DEFAULT_HAIR[i] if i < len(DEFAULT_HAIR) else "short"
            print(f"  {i}: {p['name']}  (default hair: {hair})")
        print(f"\nHair styles:  {', '.join(HAIR_STYLES.keys())}")
        print(f"Animations:   {', '.join(ANIMATIONS)}")
        print(f"Frame size:   {FRAME_W}x{FRAME_H}px (1x1.5 tiles on {TILE_SIZE}px grid)")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if args.all:
        for i, preset in enumerate(PRESETS):
            hair = DEFAULT_HAIR[i] if i < len(DEFAULT_HAIR) else "short"
            _generate_one(f"char_{i}", preset, hair, i)
        print(f"\nGenerated {len(PRESETS)} characters.")
        return

    if args.preset < 0 or args.preset >= len(PRESETS):
        parser.error(f"--preset must be 0-{len(PRESETS)-1}")
    palette = PRESETS[args.preset]
    hair = args.hair or (DEFAULT_HAIR[args.preset] if args.preset < len(DEFAULT_HAIR) else "short")
    _generate_one(args.name, palette, hair, args.preset)


def _generate_one(sprite_name: str, palette: dict, hair_style: str, preset_idx: int):
    """Generate a single character spritesheet + atlas + preview."""
    sheet_img, frames_meta = build_spritesheet(palette, hair_style)

    tag = f"preset{preset_idx}"
    image_file = f"{sprite_name}_{tag}.png"
    atlas_file = f"{sprite_name}_{tag}.json"
    preview_file = f"{sprite_name}_{tag}_preview.html"

    sheet_path = os.path.join(OUTPUT_DIR, image_file)
    sheet_img.save(sheet_path)
    print(f"  Spritesheet: {sheet_path}  ({sheet_img.width}x{sheet_img.height})")

    atlas = build_atlas(sprite_name, image_file, frames_meta, sheet_img.size)
    atlas_path = os.path.join(OUTPUT_DIR, atlas_file)
    with open(atlas_path, "w") as f:
        json.dump(atlas, f, indent=2)
    print(f"  Atlas:       {atlas_path}")

    preview_path = os.path.join(OUTPUT_DIR, preview_file)
    with open(preview_path, "w") as f:
        f.write(build_preview_html(sprite_name, image_file, atlas_file))
    print(f"  Preview:     {preview_path}")

    total_frames = len(ANIMATIONS) * len(DIRECTIONS) * FRAMES_PER_DIR
    print(f"  Style:       {palette['name']} | hair: {hair_style}")
    print(f"  Animations:  {', '.join(ANIMATIONS)}")
    print(f"  Frames:      {total_frames} ({len(ANIMATIONS)} anims x {len(DIRECTIONS)} dirs x {FRAMES_PER_DIR} frames)")
    print(f"  Frame size:  {FRAME_W}x{FRAME_H}px (1x1.5 tiles on {TILE_SIZE}px grid)\n")


if __name__ == "__main__":
    main()
