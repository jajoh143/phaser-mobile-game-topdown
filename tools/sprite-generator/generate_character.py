#!/usr/bin/env python3
"""
Top-down chibi character sprite generator for Phaser 3.

Generates 16x16 spritesheets matching the classic top-heavy chibi style:
  - Giant head (~70% of sprite) with open mouth and dot eyes
  - Tiny blob body with shoulder-pivot arms
  - Arms rotate from shoulder connection points during animations
  - Stubby 2px legs
  - Thick dark outline around entire silhouette
  - Hair wraps around and defines the head shape

Sprites are 16x16 native, scaled 2x to fill 32x32 world tiles in Phaser.

Animations: walk, jump, crouch, interact (4 directions x 4 frames each).

Usage:
    python generate_character.py --preset 0 --name player
    python generate_character.py --all
    python generate_character.py --list-presets
"""

import argparse
import json
import os
from PIL import Image

# ---------------------------------------------------------------------------
# OUTPUT CONFIG
# ---------------------------------------------------------------------------
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "generated")
FRAME_W = 16
FRAME_H = 16
TILE_SIZE = 32  # world grid is 32x32; sprites render at 2x

DIRECTIONS = ["down", "left", "right", "up"]
FRAMES_PER_DIR = 4
ANIMATIONS = ["walk", "jump", "crouch", "interact"]

# ---------------------------------------------------------------------------
# COLOR PALETTES
#
# "mouth_inner" = dark interior of the open mouth
# "mouth_line"  = the outline/lip of the mouth opening
# ---------------------------------------------------------------------------
PRESETS = [
    {
        "name": "Blue hair, red shirt",
        "skin": (235, 190, 160, 255),
        "skin_shade": (210, 165, 135, 255),
        "hair": (55, 60, 120, 255),
        "hair_shade": (38, 42, 85, 255),
        "hair_highlight": (75, 80, 150, 255),
        "shirt": (190, 60, 55, 255),
        "shirt_shade": (150, 42, 38, 255),
        "pants": (70, 65, 80, 255),
        "pants_shade": (52, 48, 60, 255),
        "shoes": (55, 45, 40, 255),
        "shoes_shade": (40, 32, 28, 255),
        "outline": (35, 28, 28, 255),
        "eye": (28, 28, 35, 255),
        "mouth_inner": (120, 45, 40, 255),
        "mouth_line": (35, 28, 28, 255),
    },
    {
        "name": "Green goblin, teal tunic",
        "skin": (85, 160, 95, 255),
        "skin_shade": (62, 130, 70, 255),
        "hair": (55, 120, 65, 255),
        "hair_shade": (38, 90, 45, 255),
        "hair_highlight": (75, 145, 85, 255),
        "shirt": (60, 135, 140, 255),
        "shirt_shade": (42, 105, 110, 255),
        "pants": (55, 100, 105, 255),
        "pants_shade": (40, 78, 82, 255),
        "shoes": (50, 42, 36, 255),
        "shoes_shade": (36, 30, 25, 255),
        "outline": (28, 35, 28, 255),
        "eye": (25, 25, 30, 255),
        "mouth_inner": (50, 95, 55, 255),
        "mouth_line": (28, 35, 28, 255),
    },
    {
        "name": "White hair, mint shirt",
        "skin": (235, 200, 175, 255),
        "skin_shade": (210, 178, 150, 255),
        "hair": (220, 225, 230, 255),
        "hair_shade": (185, 190, 200, 255),
        "hair_highlight": (242, 245, 248, 255),
        "shirt": (140, 210, 185, 255),
        "shirt_shade": (110, 178, 155, 255),
        "pants": (100, 170, 148, 255),
        "pants_shade": (78, 140, 120, 255),
        "shoes": (52, 42, 38, 255),
        "shoes_shade": (38, 30, 26, 255),
        "outline": (30, 30, 35, 255),
        "eye": (28, 28, 35, 255),
        "mouth_inner": (170, 85, 75, 255),
        "mouth_line": (30, 30, 35, 255),
    },
    {
        "name": "Red beard, brown outfit",
        "skin": (225, 175, 140, 255),
        "skin_shade": (200, 150, 118, 255),
        "hair": (195, 80, 35, 255),
        "hair_shade": (155, 58, 22, 255),
        "hair_highlight": (225, 110, 55, 255),
        "shirt": (140, 100, 65, 255),
        "shirt_shade": (110, 78, 48, 255),
        "pants": (120, 85, 55, 255),
        "pants_shade": (95, 65, 40, 255),
        "shoes": (55, 42, 35, 255),
        "shoes_shade": (40, 30, 24, 255),
        "outline": (40, 28, 22, 255),
        "eye": (28, 25, 25, 255),
        "mouth_inner": (165, 60, 30, 255),
        "mouth_line": (40, 28, 22, 255),
    },
    {
        "name": "Purple hair, dark cloak",
        "skin": (230, 195, 165, 255),
        "skin_shade": (205, 170, 140, 255),
        "hair": (120, 70, 145, 255),
        "hair_shade": (88, 48, 110, 255),
        "hair_highlight": (150, 95, 175, 255),
        "shirt": (55, 48, 65, 255),
        "shirt_shade": (38, 32, 48, 255),
        "pants": (48, 42, 58, 255),
        "pants_shade": (35, 30, 42, 255),
        "shoes": (40, 35, 45, 255),
        "shoes_shade": (28, 24, 32, 255),
        "outline": (30, 25, 35, 255),
        "eye": (25, 22, 30, 255),
        "mouth_inner": (155, 78, 68, 255),
        "mouth_line": (30, 25, 35, 255),
    },
    {
        "name": "Cowboy hat, green vest",
        "skin": (225, 185, 148, 255),
        "skin_shade": (200, 160, 125, 255),
        "hair": (100, 75, 50, 255),
        "hair_shade": (72, 52, 35, 255),
        "hair_highlight": (128, 98, 68, 255),
        "shirt": (75, 140, 72, 255),
        "shirt_shade": (55, 110, 52, 255),
        "pants": (65, 62, 78, 255),
        "pants_shade": (48, 45, 58, 255),
        "shoes": (52, 42, 36, 255),
        "shoes_shade": (38, 30, 25, 255),
        "outline": (35, 30, 25, 255),
        "eye": (25, 25, 30, 255),
        "mouth_inner": (160, 80, 65, 255),
        "mouth_line": (35, 30, 25, 255),
    },
    {
        "name": "Dark skin, orange hair",
        "skin": (140, 95, 65, 255),
        "skin_shade": (115, 75, 48, 255),
        "hair": (220, 140, 45, 255),
        "hair_shade": (185, 110, 30, 255),
        "hair_highlight": (245, 170, 65, 255),
        "shirt": (60, 120, 155, 255),
        "shirt_shade": (42, 95, 125, 255),
        "pants": (55, 55, 70, 255),
        "pants_shade": (40, 40, 52, 255),
        "shoes": (48, 38, 32, 255),
        "shoes_shade": (34, 26, 22, 255),
        "outline": (28, 22, 18, 255),
        "eye": (22, 22, 28, 255),
        "mouth_inner": (100, 55, 38, 255),
        "mouth_line": (28, 22, 18, 255),
    },
    {
        "name": "Pink hair, chef outfit",
        "skin": (238, 205, 178, 255),
        "skin_shade": (215, 182, 155, 255),
        "hair": (215, 120, 140, 255),
        "hair_shade": (180, 90, 108, 255),
        "hair_highlight": (238, 150, 168, 255),
        "shirt": (232, 232, 238, 255),
        "shirt_shade": (200, 200, 210, 255),
        "pants": (65, 65, 78, 255),
        "pants_shade": (48, 48, 60, 255),
        "shoes": (52, 42, 38, 255),
        "shoes_shade": (38, 30, 26, 255),
        "outline": (32, 28, 30, 255),
        "eye": (28, 25, 28, 255),
        "mouth_inner": (175, 90, 82, 255),
        "mouth_line": (32, 28, 30, 255),
    },
]

# ---------------------------------------------------------------------------
# HAIR STYLES — pixel masks for 16x16 oversized head
#
# Head center is roughly x=7-8, y=5-6. Head spans ~y=1..9.
# Hair wraps around and defines the head silhouette.
# Each direction returns list of (x, y, shade):
#   0=base, 1=shade(dark), 2=highlight(light)
# ---------------------------------------------------------------------------

def _hr(y, xs, xe, s=0):
    """Hair row helper."""
    return [(x, y, s) for x in range(xs, xe)]


def _make_hair_short():
    """Short bowl/cap hair — like the blue-haired character."""
    front = []
    front += _hr(1, 5, 11, 2)
    front += _hr(2, 4, 12, 0)
    front += _hr(3, 3, 13, 0)
    front += [(3, 4, 1), (12, 4, 1)]  # side tufts

    back = []
    back += _hr(1, 5, 11, 1)
    back += _hr(2, 4, 12, 1)
    back += _hr(3, 3, 13, 1)
    back += _hr(4, 3, 13, 1)
    back += _hr(5, 4, 12, 1)

    left = []
    left += _hr(1, 4, 10, 2)
    left += _hr(2, 3, 10, 0)
    left += _hr(3, 3, 10, 0)
    left += [(3, 4, 1), (3, 5, 1)]

    right = [(FRAME_W - 1 - x, y, s) for x, y, s in left]
    return {"down": front, "up": back, "left": left, "right": right}


def _make_hair_long():
    """Long flowing hair — drapes down past the body."""
    front = []
    front += _hr(1, 5, 11, 2)
    front += _hr(2, 4, 12, 0)
    front += _hr(3, 3, 13, 0)
    for y in range(4, 11):
        front += [(3, y, 1), (12, y, 1)]
    for y in range(4, 9):
        front += [(2, y, 1), (13, y, 1)]

    back = []
    back += _hr(1, 5, 11, 1)
    back += _hr(2, 4, 12, 1)
    for y in range(3, 8):
        back += _hr(y, 3, 13, 1)
    for y in range(8, 12):
        back += _hr(y, 4, 12, 1)

    left = []
    left += _hr(1, 4, 10, 2)
    left += _hr(2, 3, 10, 0)
    left += _hr(3, 2, 10, 0)
    for y in range(4, 11):
        left += [(2, y, 1)]
    for y in range(4, 9):
        left += [(3, y, 1)]

    right = [(FRAME_W - 1 - x, y, s) for x, y, s in left]
    return {"down": front, "up": back, "left": left, "right": right}


def _make_hair_afro():
    """Big round afro — extends well above and around head."""
    front = []
    front += _hr(0, 5, 11, 2)
    front += _hr(1, 3, 13, 0)
    front += _hr(2, 2, 14, 0)
    front += _hr(3, 2, 14, 1)
    for y in range(4, 7):
        front += [(2, y, 1), (13, y, 1)]

    back = []
    back += _hr(0, 5, 11, 1)
    back += _hr(1, 3, 13, 1)
    for y in range(2, 7):
        back += _hr(y, 2, 14, 1)
    back += _hr(7, 3, 13, 1)

    left = []
    left += _hr(0, 4, 10, 2)
    left += _hr(1, 2, 11, 0)
    left += _hr(2, 1, 11, 0)
    left += _hr(3, 1, 11, 1)
    for y in range(4, 7):
        left += [(1, y, 1), (2, y, 1)]

    right = [(FRAME_W - 1 - x, y, s) for x, y, s in left]
    return {"down": front, "up": back, "left": left, "right": right}


def _make_hair_ponytail():
    """Short top with ponytail in back."""
    front = []
    front += _hr(1, 5, 11, 2)
    front += _hr(2, 4, 12, 0)
    front += _hr(3, 3, 13, 0)
    front += [(3, 4, 1), (12, 4, 1)]

    back = []
    back += _hr(1, 5, 11, 1)
    back += _hr(2, 4, 12, 0)
    back += _hr(3, 3, 13, 1)
    # Ponytail
    for y in range(4, 7):
        back += [(7, y, 1), (8, y, 1)]
    for y in range(7, 12):
        back += [(7, y, 1)]

    left = []
    left += _hr(1, 4, 10, 2)
    left += _hr(2, 3, 10, 0)
    left += _hr(3, 3, 10, 1)

    right = [(FRAME_W - 1 - x, y, s) for x, y, s in left]
    return {"down": front, "up": back, "left": left, "right": right}


def _make_hair_spiky():
    """Sharp spiky hair — defined triangular points."""
    front = []
    # Individual spikes with sharp tips
    front += [(5, 0, 2), (8, 0, 0), (11, 0, 2)]  # spike tips
    front += [(4, 1, 0), (5, 1, 0), (7, 1, 0), (8, 1, 0), (9, 1, 0), (10, 1, 0), (11, 1, 0)]
    front += _hr(2, 4, 12, 0)
    front += _hr(3, 3, 13, 1)
    front += [(3, 4, 1), (12, 4, 1)]

    back = list(front[:])
    back += _hr(4, 3, 13, 1)
    back += _hr(5, 4, 12, 1)

    left = []
    left += [(4, 0, 2), (7, 0, 0), (10, 0, 2)]
    left += _hr(1, 3, 11, 0)
    left += _hr(2, 3, 10, 0)
    left += _hr(3, 3, 10, 1)
    left += [(3, 4, 1)]

    right = [(FRAME_W - 1 - x, y, s) for x, y, s in left]
    return {"down": front, "up": back, "left": left, "right": right}


HAIR_STYLES = {
    "short": _make_hair_short(),
    "long": _make_hair_long(),
    "afro": _make_hair_afro(),
    "ponytail": _make_hair_ponytail(),
    "spiky": _make_hair_spiky(),
}

DEFAULT_HAIR = ["short", "short", "short", "short", "long", "ponytail", "spiky", "long"]


# ---------------------------------------------------------------------------
# BODY TEMPLATES — 16x16 top-heavy chibi
#
# Layout (front-facing):
#   y 0-3:  hair (above + wrapping head)
#   y 4-8:  head interior (skin, eyes at y5, mouth at y7)
#   y 9:    chin / head bottom outline
#   y 10-12: body/shirt (tiny, ~6px wide)
#   y 13:   pants
#   y 14:   legs/shoes
#   y 15:   shoe bottoms
#
# NO visible arms at rest — body is a clean blob silhouette.
# Arms only appear via animation offsets.
# ---------------------------------------------------------------------------

def _build_body_down():
    """Facing down (toward camera)."""
    p = []

    # --- Head outline + skin fill ---
    # Row 4: head widens
    p += [(3, 4, "outline")]
    for x in range(4, 12):
        p.append((x, 4, "skin"))
    p.append((12, 4, "outline"))
    # Row 5: eyes row
    p.append((3, 5, "outline"))
    p.append((4, 5, "skin"))
    p.append((5, 5, "eye"))
    p.append((6, 5, "skin"))
    p.append((7, 5, "skin"))
    p.append((8, 5, "skin"))
    p.append((9, 5, "eye"))
    p.append((10, 5, "skin"))
    p.append((11, 5, "skin"))
    p.append((12, 5, "outline"))
    # Row 6: face
    p.append((3, 6, "outline"))
    for x in range(4, 12):
        p.append((x, 6, "skin"))
    p.append((12, 6, "outline"))
    # Row 7: mouth row — open mouth!
    p.append((3, 7, "outline"))
    p.append((4, 7, "skin"))
    p.append((5, 7, "skin"))
    p.append((6, 7, "mouth_line"))
    p.append((7, 7, "mouth_inner"))
    p.append((8, 7, "mouth_inner"))
    p.append((9, 7, "mouth_line"))
    p.append((10, 7, "skin"))
    p.append((11, 7, "skin"))
    p.append((12, 7, "outline"))
    # Row 8: lower face / chin area
    p.append((3, 8, "outline"))
    p.append((4, 8, "skin_shade"))
    p.append((5, 8, "skin"))
    p.append((6, 8, "mouth_line"))
    p.append((7, 8, "skin_shade"))
    p.append((8, 8, "skin_shade"))
    p.append((9, 8, "mouth_line"))
    p.append((10, 8, "skin"))
    p.append((11, 8, "skin_shade"))
    p.append((12, 8, "outline"))
    # Row 9: chin outline
    p.append((4, 9, "outline"))
    for x in range(5, 11):
        p.append((x, 9, "skin_shade"))
    p.append((11, 9, "outline"))

    # --- Body / Shirt (tiny!) ---
    # Row 10
    p.append((4, 10, "outline"))
    for x in range(5, 11):
        p.append((x, 10, "shirt"))
    p.append((11, 10, "outline"))
    # Row 11
    p.append((4, 11, "outline"))
    for x in range(5, 11):
        p.append((x, 11, "shirt_shade"))
    p.append((11, 11, "outline"))
    # Row 12
    p.append((5, 12, "outline"))
    for x in range(6, 10):
        p.append((x, 12, "shirt_shade"))
    p.append((10, 12, "outline"))

    # --- Legs / Feet ---
    # Row 13: pants
    p.append((5, 13, "outline"))
    p.append((6, 13, "pants"))
    p.append((7, 13, "outline"))
    p.append((8, 13, "outline"))
    p.append((9, 13, "pants"))
    p.append((10, 13, "outline"))
    # Row 14: shoes
    p.append((5, 14, "outline"))
    p.append((6, 14, "shoes"))
    p.append((7, 14, "outline"))
    p.append((8, 14, "outline"))
    p.append((9, 14, "shoes"))
    p.append((10, 14, "outline"))

    return p


def _build_body_up():
    """Facing up (away from camera). No eyes, no mouth."""
    p = []

    # --- Head (back of head — skin_shade, no features) ---
    p.append((3, 4, "outline"))
    for x in range(4, 12):
        p.append((x, 4, "skin_shade"))
    p.append((12, 4, "outline"))
    for y in range(5, 9):
        p.append((3, y, "outline"))
        for x in range(4, 12):
            p.append((x, y, "skin_shade"))
        p.append((12, y, "outline"))
    p.append((4, 9, "outline"))
    for x in range(5, 11):
        p.append((x, 9, "skin_shade"))
    p.append((11, 9, "outline"))

    # --- Body (back) ---
    p.append((4, 10, "outline"))
    for x in range(5, 11):
        p.append((x, 10, "shirt_shade"))
    p.append((11, 10, "outline"))
    p.append((4, 11, "outline"))
    for x in range(5, 11):
        p.append((x, 11, "shirt_shade"))
    p.append((11, 11, "outline"))
    p.append((5, 12, "outline"))
    for x in range(6, 10):
        p.append((x, 12, "shirt_shade"))
    p.append((10, 12, "outline"))

    # --- Legs ---
    p.append((5, 13, "outline"))
    p.append((6, 13, "pants_shade"))
    p.append((7, 13, "outline"))
    p.append((8, 13, "outline"))
    p.append((9, 13, "pants_shade"))
    p.append((10, 13, "outline"))
    p.append((5, 14, "outline"))
    p.append((6, 14, "shoes_shade"))
    p.append((7, 14, "outline"))
    p.append((8, 14, "outline"))
    p.append((9, 14, "shoes_shade"))
    p.append((10, 14, "outline"))

    return p


def _build_body_left():
    """Facing left — side profile."""
    p = []

    # --- Head (side, shifted left slightly) ---
    p.append((3, 4, "outline"))
    for x in range(4, 11):
        p.append((x, 4, "skin"))
    p.append((11, 4, "outline"))
    # Row 5: eye
    p.append((3, 5, "outline"))
    p.append((4, 5, "skin"))
    p.append((5, 5, "eye"))
    p.append((6, 5, "skin"))
    for x in range(7, 11):
        p.append((x, 5, "skin"))
    p.append((11, 5, "outline"))
    # Row 6
    p.append((3, 6, "outline"))
    for x in range(4, 11):
        p.append((x, 6, "skin"))
    p.append((11, 6, "outline"))
    # Row 7: mouth (side)
    p.append((3, 7, "outline"))
    p.append((4, 7, "skin"))
    p.append((5, 7, "mouth_line"))
    p.append((6, 7, "mouth_inner"))
    p.append((7, 7, "mouth_line"))
    for x in range(8, 11):
        p.append((x, 7, "skin"))
    p.append((11, 7, "outline"))
    # Row 8
    p.append((3, 8, "outline"))
    for x in range(4, 11):
        p.append((x, 8, "skin_shade"))
    p.append((11, 8, "outline"))
    # Row 9: chin
    p.append((4, 9, "outline"))
    for x in range(5, 10):
        p.append((x, 9, "skin_shade"))
    p.append((10, 9, "outline"))

    # --- Body (side, narrower) ---
    p.append((4, 10, "outline"))
    for x in range(5, 10):
        p.append((x, 10, "shirt"))
    p.append((10, 10, "outline"))
    p.append((4, 11, "outline"))
    for x in range(5, 10):
        p.append((x, 11, "shirt_shade"))
    p.append((10, 11, "outline"))
    p.append((5, 12, "outline"))
    for x in range(6, 9):
        p.append((x, 12, "shirt_shade"))
    p.append((9, 12, "outline"))

    # --- Legs (side) ---
    p.append((5, 13, "outline"))
    p.append((6, 13, "pants"))
    p.append((7, 13, "pants"))
    p.append((8, 13, "outline"))
    p.append((4, 14, "outline"))
    p.append((5, 14, "shoes"))
    p.append((6, 14, "shoes"))
    p.append((7, 14, "outline"))

    return p


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
# ANIMATION REGIONS
#
# Regions: head, body, leg_l, leg_r.
# Arms are handled separately via shoulder-pivot overlay system.
# ---------------------------------------------------------------------------

def _region_for_pixel(x, y, direction):
    """Classify pixel into animation region."""
    if y <= 9:
        return "head"
    if y <= 12:
        return "body"
    # Legs
    if direction in ("down", "up"):
        if x <= 7:
            return "leg_l"
        return "leg_r"
    else:
        return "leg_l" if y <= 13 else "leg_r"


# ---------------------------------------------------------------------------
# SHOULDER-PIVOT ARM SYSTEM
#
# Arms are 1-2 pixel appendages that rotate from shoulder pivot points.
# Shoulder pivots sit at the top-outer edge of the body (y=10).
# Arm pixels are skin-colored and drawn outside the body silhouette.
#
# For each animation+direction+frame, we define discrete arm positions
# as pixel offsets from the shoulder pivot. The offsets simulate rotation:
#   "down" from shoulder = arm hanging at rest
#   "horizontal" = arm extended outward
#   "up" = arm raised above shoulder
#
# Outline pixels are added at the arm extremities for visual consistency.
# ---------------------------------------------------------------------------

# Shoulder pivot positions per direction (left_shoulder, right_shoulder)
_SHOULDERS = {
    "down":  ((4, 10), (11, 10)),
    "up":    ((4, 10), (11, 10)),
    "left":  ((4, 10), (10, 10)),
    "right": ((5, 10), (11, 10)),
}

# Arm pose definitions: pixel offsets from shoulder pivot.
# Each pose = list of (dx, dy) for arm segment pixels (skin-colored).
# Convention: negative dx = away from body center for left arm.
#             positive dx = away from body center for right arm.
# We store for LEFT arm; right arm mirrors dx.

_ARM_POSE_LEFT = {
    # Front/back views (arms extend sideways)
    "rest":       [],                          # hidden in body
    "out_mid":    [(-1, 1)],                   # 1px out, slightly below shoulder
    "out_low":    [(-1, 2)],                   # 1px out, well below shoulder
    "out_high":   [(-1, 0)],                   # 1px out, at shoulder level
    "swing_fwd":  [(-1, 0)],                   # forward swing = at shoulder
    "swing_back": [(-1, 2)],                   # back swing = below shoulder
    "raised":     [(-1, 0), (-1, -1)],         # 2px arm reaching up
    "reach_up":   [(-1, -1), (-2, -2)],        # reaching up and out diagonally
    "reach_out":  [(-1, 0), (-2, 0)],          # reaching out horizontally
    # Side views (arms extend forward/back along depth axis)
    "side_mid":   [(-1, 1)],                   # beside body
    "side_fwd":   [(-1, 0)],                   # forward (higher)
    "side_back":  [(-1, 2)],                   # back (lower)
    "side_raise": [(-1, 0), (-1, -1)],         # raised on side
    "side_reach": [(-1, -1), (-1, -2)],        # reaching upward on side
}


def _mirror_pose(pose):
    """Mirror a left-arm pose for the right arm (flip dx)."""
    return [(-dx, dy) for dx, dy in pose]


def _get_arm_pixels(direction, animation, frame_idx):
    """Return arm overlay pixels as list of (x, y, color_key).

    Arms rotate from shoulder pivots. Positions are absolute pixel coords.
    Includes outline pixels at arm tips for visual consistency.
    """
    l_sh, r_sh = _SHOULDERS[direction]

    # Look up pose names for this animation/direction/frame
    l_pose_name, r_pose_name = _ARM_ANIM_POSES[animation][direction][frame_idx]

    # Get offset lists
    if direction in ("left", "right"):
        l_offsets = _ARM_POSE_LEFT.get(l_pose_name, [])
        r_offsets = _mirror_pose(_ARM_POSE_LEFT.get(r_pose_name, []))
    else:
        l_offsets = _ARM_POSE_LEFT.get(l_pose_name, [])
        r_offsets = _mirror_pose(_ARM_POSE_LEFT.get(r_pose_name, []))

    pixels = []

    # Draw left arm segments
    for dx, dy in l_offsets:
        ax, ay = l_sh[0] + dx, l_sh[1] + dy
        if 0 <= ax < FRAME_W and 0 <= ay < FRAME_H:
            pixels.append((ax, ay, "skin"))

    # Draw right arm segments
    for dx, dy in r_offsets:
        ax, ay = r_sh[0] + dx, r_sh[1] + dy
        if 0 <= ax < FRAME_W and 0 <= ay < FRAME_H:
            pixels.append((ax, ay, "skin"))

    # Add outline at the tip of each arm (outermost pixel)
    if l_offsets:
        tip_dx, tip_dy = l_offsets[-1]
        tip_x, tip_y = l_sh[0] + tip_dx, l_sh[1] + tip_dy
        # Outline below/outside the tip
        for ox, oy in [(-1, 0), (0, 1)]:
            ex, ey = tip_x + ox, tip_y + oy
            if 0 <= ex < FRAME_W and 0 <= ey < FRAME_H:
                # Only add outline if not overlapping existing arm/body pixels
                if not any(px == ex and py == ey for px, py, _ in pixels):
                    pixels.append((ex, ey, "outline"))

    if r_offsets:
        tip_dx, tip_dy = r_offsets[-1]
        tip_x, tip_y = r_sh[0] + tip_dx, r_sh[1] + tip_dy
        for ox, oy in [(1, 0), (0, 1)]:
            ex, ey = tip_x + ox, tip_y + oy
            if 0 <= ex < FRAME_W and 0 <= ey < FRAME_H:
                if not any(px == ex and py == ey for px, py, _ in pixels):
                    pixels.append((ex, ey, "outline"))

    return pixels


# Arm pose schedule per animation.
# Format: _ARM_ANIM_POSES[anim][direction] = [(left_pose, right_pose), ...] x 4 frames
# Poses reference names in _ARM_POSE_LEFT.

_ARM_ANIM_POSES = {
    "walk": {
        "down": [
            ("out_mid",   "out_mid"),     # frame 0: neutral stride
            ("swing_fwd", "swing_back"),  # frame 1: left fwd, right back
            ("out_mid",   "out_mid"),     # frame 2: neutral stride
            ("swing_back", "swing_fwd"),  # frame 3: left back, right fwd
        ],
        "up": [
            ("out_mid",   "out_mid"),
            ("swing_fwd", "swing_back"),
            ("out_mid",   "out_mid"),
            ("swing_back", "swing_fwd"),
        ],
        "left": [
            ("side_mid",  "side_mid"),
            ("side_fwd",  "side_back"),
            ("side_mid",  "side_mid"),
            ("side_back", "side_fwd"),
        ],
        "right": [
            ("side_mid",  "side_mid"),
            ("side_fwd",  "side_back"),
            ("side_mid",  "side_mid"),
            ("side_back", "side_fwd"),
        ],
    },

    "jump": {
        "down": [
            ("out_mid",  "out_mid"),      # frame 0: crouch before jump
            ("out_high", "out_high"),      # frame 1: launching
            ("raised",   "raised"),        # frame 2: peak — arms up!
            ("out_high", "out_high"),      # frame 3: landing
        ],
        "up": [
            ("out_mid",  "out_mid"),
            ("out_high", "out_high"),
            ("raised",   "raised"),
            ("out_high", "out_high"),
        ],
        "left": [
            ("side_mid",   "side_mid"),
            ("side_fwd",   "side_fwd"),
            ("side_raise", "side_raise"),
            ("side_fwd",   "side_fwd"),
        ],
        "right": [
            ("side_mid",   "side_mid"),
            ("side_fwd",   "side_fwd"),
            ("side_raise", "side_raise"),
            ("side_fwd",   "side_fwd"),
        ],
    },

    "crouch": {
        "down": [
            ("out_mid",  "out_mid"),       # frame 0: standing
            ("out_low",  "out_low"),        # frame 1: lowering
            ("out_low",  "out_low"),        # frame 2: fully crouched
            ("out_low",  "out_low"),        # frame 3: holding crouch
        ],
        "up": [
            ("out_mid",  "out_mid"),
            ("out_low",  "out_low"),
            ("out_low",  "out_low"),
            ("out_low",  "out_low"),
        ],
        "left": [
            ("side_mid",  "side_mid"),
            ("side_back", "side_back"),
            ("side_back", "side_back"),
            ("side_back", "side_back"),
        ],
        "right": [
            ("side_mid",  "side_mid"),
            ("side_back", "side_back"),
            ("side_back", "side_back"),
            ("side_back", "side_back"),
        ],
    },

    "interact": {
        "down": [
            ("out_mid",  "out_mid"),       # frame 0: idle
            ("out_mid",  "out_high"),       # frame 1: right arm starts raising
            ("out_mid",  "raised"),         # frame 2: right arm fully raised
            ("out_mid",  "out_high"),       # frame 3: right arm lowering
        ],
        "up": [
            ("out_mid",  "out_mid"),
            ("out_mid",  "out_high"),
            ("out_mid",  "raised"),
            ("out_mid",  "out_high"),
        ],
        "left": [
            ("side_mid",  "side_mid"),
            ("side_mid",  "side_fwd"),
            ("side_mid",  "side_raise"),
            ("side_mid",  "side_fwd"),
        ],
        "right": [
            ("side_mid",  "side_mid"),
            ("side_mid",  "side_fwd"),
            ("side_mid",  "side_raise"),
            ("side_mid",  "side_fwd"),
        ],
    },
}


# ---------------------------------------------------------------------------
# ANIMATION OFFSETS (body region movement)
# ---------------------------------------------------------------------------

ANIM_OFFSETS = {
    "walk": {
        "down": {
            "head":  [(0, 0), (0, -1), (0, 0), (0, -1)],
            "body":  [(0, 0), (0, 0),  (0, 0), (0, 0)],
            "leg_l": [(0, 0), (0, 1),  (0, 0), (0, -1)],
            "leg_r": [(0, 0), (0, -1), (0, 0), (0, 1)],
        },
        "up": {
            "head":  [(0, 0), (0, -1), (0, 0), (0, -1)],
            "body":  [(0, 0), (0, 0),  (0, 0), (0, 0)],
            "leg_l": [(0, 0), (0, 1),  (0, 0), (0, -1)],
            "leg_r": [(0, 0), (0, -1), (0, 0), (0, 1)],
        },
        "left": {
            "head":  [(0, 0), (0, -1), (0, 0), (0, -1)],
            "body":  [(0, 0), (0, 0),  (0, 0), (0, 0)],
            "leg_l": [(0, 0), (0, 1),  (0, 0), (0, -1)],
            "leg_r": [(0, 0), (0, -1), (0, 0), (0, 1)],
        },
        "right": {
            "head":  [(0, 0), (0, -1), (0, 0), (0, -1)],
            "body":  [(0, 0), (0, 0),  (0, 0), (0, 0)],
            "leg_l": [(0, 0), (0, 1),  (0, 0), (0, -1)],
            "leg_r": [(0, 0), (0, -1), (0, 0), (0, 1)],
        },
    },

    "jump": {
        "down": {
            "head":  [(0, 1),  (0, -1), (0, -2), (0, 0)],
            "body":  [(0, 1),  (0, -1), (0, -2), (0, 0)],
            "leg_l": [(0, 1),  (0, 0),  (0, -1), (0, 1)],
            "leg_r": [(0, 1),  (0, 0),  (0, -1), (0, 1)],
        },
        "up": {
            "head":  [(0, 1),  (0, -1), (0, -2), (0, 0)],
            "body":  [(0, 1),  (0, -1), (0, -2), (0, 0)],
            "leg_l": [(0, 1),  (0, 0),  (0, -1), (0, 1)],
            "leg_r": [(0, 1),  (0, 0),  (0, -1), (0, 1)],
        },
        "left": {
            "head":  [(0, 1),  (0, -1), (0, -2), (0, 0)],
            "body":  [(0, 1),  (0, -1), (0, -2), (0, 0)],
            "leg_l": [(0, 1),  (0, 0),  (0, -1), (0, 1)],
            "leg_r": [(0, 1),  (0, 0),  (0, -1), (0, 1)],
        },
        "right": {
            "head":  [(0, 1),  (0, -1), (0, -2), (0, 0)],
            "body":  [(0, 1),  (0, -1), (0, -2), (0, 0)],
            "leg_l": [(0, 1),  (0, 0),  (0, -1), (0, 1)],
            "leg_r": [(0, 1),  (0, 0),  (0, -1), (0, 1)],
        },
    },

    "crouch": {
        "down": {
            "head":  [(0, 0), (0, 1),  (0, 2),  (0, 1)],
            "body":  [(0, 0), (0, 1),  (0, 1),  (0, 1)],
            "leg_l": [(0, 0), (0, 0),  (0, 1),  (0, 0)],
            "leg_r": [(0, 0), (0, 0),  (0, 1),  (0, 0)],
        },
        "up": {
            "head":  [(0, 0), (0, 1),  (0, 2),  (0, 1)],
            "body":  [(0, 0), (0, 1),  (0, 1),  (0, 1)],
            "leg_l": [(0, 0), (0, 0),  (0, 1),  (0, 0)],
            "leg_r": [(0, 0), (0, 0),  (0, 1),  (0, 0)],
        },
        "left": {
            "head":  [(0, 0), (0, 1),  (0, 2),  (0, 1)],
            "body":  [(0, 0), (0, 1),  (0, 1),  (0, 1)],
            "leg_l": [(0, 0), (0, 0),  (0, 1),  (0, 0)],
            "leg_r": [(0, 0), (0, 0),  (0, 1),  (0, 0)],
        },
        "right": {
            "head":  [(0, 0), (0, 1),  (0, 2),  (0, 1)],
            "body":  [(0, 0), (0, 1),  (0, 1),  (0, 1)],
            "leg_l": [(0, 0), (0, 0),  (0, 1),  (0, 0)],
            "leg_r": [(0, 0), (0, 0),  (0, 1),  (0, 0)],
        },
    },

    "interact": {
        "down": {
            "head":  [(0, 0), (0, 0),  (0, -1), (0, 0)],
            "body":  [(0, 0), (0, 0),  (0, 0),  (0, 0)],
            "leg_l": [(0, 0), (0, 0),  (0, 0),  (0, 0)],
            "leg_r": [(0, 0), (0, 0),  (0, 0),  (0, 0)],
        },
        "up": {
            "head":  [(0, 0), (0, 0),  (0, -1), (0, 0)],
            "body":  [(0, 0), (0, 0),  (0, 0),  (0, 0)],
            "leg_l": [(0, 0), (0, 0),  (0, 0),  (0, 0)],
            "leg_r": [(0, 0), (0, 0),  (0, 0),  (0, 0)],
        },
        "left": {
            "head":  [(0, 0), (0, 0),  (0, -1), (0, 0)],
            "body":  [(0, 0), (0, 0),  (0, 0),  (0, 0)],
            "leg_l": [(0, 0), (0, 0),  (0, 0),  (0, 0)],
            "leg_r": [(0, 0), (0, 0),  (0, 0),  (0, 0)],
        },
        "right": {
            "head":  [(0, 0), (0, 0),  (0, -1), (0, 0)],
            "body":  [(0, 0), (0, 0),  (0, 0),  (0, 0)],
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
    """Render a single 16x16 frame."""
    img = Image.new("RGBA", (FRAME_W, FRAME_H), (0, 0, 0, 0))

    body_pixels = BODY_TEMPLATES[direction]
    offsets = ANIM_OFFSETS[animation][direction]

    # 1. Draw body template pixels (with region-based animation offsets)
    for bx, by, color_key in body_pixels:
        region = _region_for_pixel(bx, by, direction)
        dx, dy = offsets[region][frame_idx]
        px, py = bx + dx, by + dy
        if 0 <= px < FRAME_W and 0 <= py < FRAME_H:
            img.putpixel((px, py), palette[color_key])

    # 2. Draw arm overlay (shoulder-pivot rotation)
    body_dx, body_dy = offsets["body"][frame_idx]
    arm_pixels = _get_arm_pixels(direction, animation, frame_idx)
    for ax, ay, color_key in arm_pixels:
        px, py = ax + body_dx, ay + body_dy
        if 0 <= px < FRAME_W and 0 <= py < FRAME_H:
            img.putpixel((px, py), palette[color_key])

    # 3. Draw hair (moves with head)
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
    """Build the full spritesheet."""
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
            "version": "6.0",
            "image": image_file,
            "format": "RGBA8888",
            "size": {"w": sheet_size[0], "h": sheet_size[1]},
            "scale": "1",
            "frameSize": {"w": FRAME_W, "h": FRAME_H},
            "tileSize": TILE_SIZE,
            "renderScale": TILE_SIZE // FRAME_W,
        },
    }


def build_preview_html(sprite_name: str, image_file: str, atlas_file: str) -> str:
    animations_json = json.dumps(ANIMATIONS)
    directions_json = json.dumps(DIRECTIONS)
    scale = TILE_SIZE // FRAME_W
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
<p class="info">v6 — 16x16 chibi (renders at {scale}x on {TILE_SIZE}px grid)</p>

<canvas id="anim" width="{FRAME_W * 10}" height="{FRAME_H * 10}"></canvas>

<div class="controls" id="animBtns">
  <label>Anim:</label>
</div>
<div class="controls" id="dirBtns">
  <label>Dir:</label>
</div>

<p class="info">Full spritesheet ({scale}x zoom):</p>
<img class="sheet-preview" id="sheetImg" />

<script>
const FRAME_W = {FRAME_W};
const FRAME_H = {FRAME_H};
const COLS = {FRAMES_PER_DIR};
const SCALE = 10;
const FPS = 6;
const ANIMATIONS = {animations_json};
const DIRECTIONS = {directions_json};
const DIRS_PER_ANIM = DIRECTIONS.length;

const canvas = document.getElementById("anim");
const ctx = canvas.getContext("2d");
ctx.imageSmoothingEnabled = false;

const img = new Image();
img.src = "{image_file}";

let animIdx = 0, dirIdx = 0, frameIdx = 0;

function getRow() {{ return animIdx * DIRS_PER_ANIM + dirIdx; }}

function makeButtons(id, labels, setter) {{
  const c = document.getElementById(id);
  labels.forEach((l, i) => {{
    const b = document.createElement("button");
    b.textContent = l;
    if (i === 0) b.classList.add("active");
    b.addEventListener("click", () => {{
      c.querySelectorAll("button").forEach(x => x.classList.remove("active"));
      b.classList.add("active");
      setter(i);
    }});
    c.appendChild(b);
  }});
}}

makeButtons("animBtns", ANIMATIONS, i => {{ animIdx = i; }});
makeButtons("dirBtns", DIRECTIONS, i => {{ dirIdx = i; }});

img.onload = () => {{
  document.getElementById("sheetImg").src = "{image_file}";
  document.getElementById("sheetImg").style.width = (img.width * 5) + "px";
  setInterval(() => {{
    frameIdx = (frameIdx + 1) % COLS;
    const row = getRow();
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(img, frameIdx * FRAME_W, row * FRAME_H, FRAME_W, FRAME_H, 0, 0, FRAME_W * SCALE, FRAME_H * SCALE);
  }}, 1000 / FPS);
}};
</script>
</body>
</html>"""


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Generate a 16x16 top-heavy chibi character spritesheet.")
    parser.add_argument("--preset", type=int, default=0,
                        help=f"Palette preset index 0-{len(PRESETS)-1}")
    parser.add_argument("--hair", choices=list(HAIR_STYLES.keys()), default=None)
    parser.add_argument("--name", default="player")
    parser.add_argument("--list-presets", action="store_true")
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()

    if args.list_presets:
        print("Available presets:")
        for i, p in enumerate(PRESETS):
            hair = DEFAULT_HAIR[i] if i < len(DEFAULT_HAIR) else "short"
            print(f"  {i}: {p['name']}  (default hair: {hair})")
        print(f"\nHair styles:  {', '.join(HAIR_STYLES.keys())}")
        print(f"Animations:   {', '.join(ANIMATIONS)}")
        print(f"Frame size:   {FRAME_W}x{FRAME_H}px (renders at {TILE_SIZE // FRAME_W}x on {TILE_SIZE}px grid)")
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

    total = len(ANIMATIONS) * len(DIRECTIONS) * FRAMES_PER_DIR
    print(f"  Style:       {palette['name']} | hair: {hair_style}")
    print(f"  Animations:  {', '.join(ANIMATIONS)}")
    print(f"  Frames:      {total} | Frame: {FRAME_W}x{FRAME_H}px (renders {TILE_SIZE // FRAME_W}x)\n")


if __name__ == "__main__":
    main()
