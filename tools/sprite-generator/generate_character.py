#!/usr/bin/env python3
"""
Top-down humanoid character sprite generator for Phaser 3.

Generates a 16x16 walk cycle spritesheet (4 directions x 4 frames)
with JSON texture atlas and browser preview.

Style reference: chibi top-down RPG sprites with rounded heads,
dark outlines, 2-tone shading, and diverse hair styles.

Usage:
    python generate_character.py --preset 0 --name player
    python generate_character.py --preset 3 --hair afro --name npc1
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
PADDING = 0

DIRECTIONS = ["down", "left", "right", "up"]
FRAMES_PER_DIR = 4

# ---------------------------------------------------------------------------
# COLOR PALETTES — each preset defines a full character look
# ---------------------------------------------------------------------------
# Colors use (R, G, B, A). "shade" variants are the darker tone for 2-tone
# shading. "outline" is the dark border color.
PRESETS = [
    {
        "name": "Light skin, brown hair, blue shirt",
        "skin": (222, 187, 155, 255),
        "skin_shade": (197, 160, 128, 255),
        "hair": (90, 60, 35, 255),
        "hair_shade": (65, 42, 22, 255),
        "shirt": (80, 130, 190, 255),
        "shirt_shade": (55, 100, 155, 255),
        "pants": (70, 70, 85, 255),
        "pants_shade": (50, 50, 65, 255),
        "shoes": (55, 45, 40, 255),
        "shoes_shade": (40, 32, 28, 255),
        "outline": (30, 25, 22, 255),
        "eye": (25, 25, 30, 255),
        "eye_white": (240, 240, 240, 255),
    },
    {
        "name": "Medium skin, black hair, red shirt",
        "skin": (195, 150, 110, 255),
        "skin_shade": (170, 125, 88, 255),
        "hair": (35, 28, 25, 255),
        "hair_shade": (22, 18, 16, 255),
        "shirt": (185, 60, 55, 255),
        "shirt_shade": (145, 42, 40, 255),
        "pants": (55, 60, 75, 255),
        "pants_shade": (40, 44, 55, 255),
        "shoes": (50, 40, 35, 255),
        "shoes_shade": (35, 28, 24, 255),
        "outline": (28, 22, 20, 255),
        "eye": (25, 25, 30, 255),
        "eye_white": (240, 240, 240, 255),
    },
    {
        "name": "Dark skin, short dark hair, green shirt",
        "skin": (140, 95, 65, 255),
        "skin_shade": (115, 75, 50, 255),
        "hair": (30, 25, 22, 255),
        "hair_shade": (20, 16, 14, 255),
        "shirt": (60, 155, 80, 255),
        "shirt_shade": (42, 120, 58, 255),
        "pants": (65, 65, 80, 255),
        "pants_shade": (48, 48, 60, 255),
        "shoes": (50, 42, 36, 255),
        "shoes_shade": (36, 30, 25, 255),
        "outline": (25, 20, 18, 255),
        "eye": (22, 22, 28, 255),
        "eye_white": (235, 235, 235, 255),
    },
    {
        "name": "Dark skin, afro, yellow shirt",
        "skin": (120, 78, 50, 255),
        "skin_shade": (95, 60, 38, 255),
        "hair": (28, 22, 18, 255),
        "hair_shade": (18, 14, 10, 255),
        "shirt": (210, 185, 60, 255),
        "shirt_shade": (175, 152, 42, 255),
        "pants": (60, 58, 72, 255),
        "pants_shade": (44, 42, 55, 255),
        "shoes": (48, 38, 32, 255),
        "shoes_shade": (34, 26, 22, 255),
        "outline": (22, 18, 15, 255),
        "eye": (22, 22, 28, 255),
        "eye_white": (232, 232, 232, 255),
    },
    {
        "name": "Light skin, blonde hair, purple shirt",
        "skin": (235, 200, 168, 255),
        "skin_shade": (210, 175, 142, 255),
        "hair": (220, 185, 100, 255),
        "hair_shade": (190, 155, 75, 255),
        "shirt": (140, 80, 170, 255),
        "shirt_shade": (110, 58, 135, 255),
        "pants": (68, 68, 82, 255),
        "pants_shade": (50, 50, 62, 255),
        "shoes": (52, 42, 38, 255),
        "shoes_shade": (38, 30, 26, 255),
        "outline": (30, 25, 22, 255),
        "eye": (25, 25, 30, 255),
        "eye_white": (240, 240, 240, 255),
    },
    {
        "name": "Medium skin, auburn hair, teal shirt",
        "skin": (205, 165, 125, 255),
        "skin_shade": (180, 140, 102, 255),
        "hair": (150, 65, 30, 255),
        "hair_shade": (115, 45, 20, 255),
        "shirt": (45, 155, 155, 255),
        "shirt_shade": (32, 120, 120, 255),
        "pants": (62, 62, 78, 255),
        "pants_shade": (45, 45, 58, 255),
        "shoes": (50, 40, 35, 255),
        "shoes_shade": (36, 28, 24, 255),
        "outline": (28, 22, 20, 255),
        "eye": (25, 25, 30, 255),
        "eye_white": (240, 240, 240, 255),
    },
    {
        "name": "Medium-dark skin, dark hair, orange shirt",
        "skin": (165, 115, 78, 255),
        "skin_shade": (140, 92, 60, 255),
        "hair": (32, 26, 22, 255),
        "hair_shade": (20, 16, 14, 255),
        "shirt": (215, 130, 45, 255),
        "shirt_shade": (180, 105, 32, 255),
        "pants": (58, 58, 72, 255),
        "pants_shade": (42, 42, 55, 255),
        "shoes": (48, 38, 32, 255),
        "shoes_shade": (34, 26, 22, 255),
        "outline": (24, 20, 18, 255),
        "eye": (22, 22, 28, 255),
        "eye_white": (235, 235, 235, 255),
    },
    {
        "name": "Light skin, red hair, white shirt",
        "skin": (240, 210, 180, 255),
        "skin_shade": (215, 185, 155, 255),
        "hair": (180, 55, 30, 255),
        "hair_shade": (140, 38, 20, 255),
        "shirt": (225, 225, 230, 255),
        "shirt_shade": (190, 190, 198, 255),
        "pants": (70, 70, 85, 255),
        "pants_shade": (52, 52, 65, 255),
        "shoes": (55, 45, 40, 255),
        "shoes_shade": (40, 32, 28, 255),
        "outline": (30, 25, 22, 255),
        "eye": (25, 25, 30, 255),
        "eye_white": (240, 240, 240, 255),
    },
]

# ---------------------------------------------------------------------------
# HAIR STYLES
# Defined as pixel masks relative to the head area.
# Each style is a dict with "front", "back", "left", "right" keys.
# Each direction value is a list of (x, y) pixel positions to fill,
# relative to the frame's top-left (0,0).
# ---------------------------------------------------------------------------

def _make_hair_short():
    """Short cropped hair — sits close to the head."""
    front = []
    # Top row across full head width
    for x in range(5, 11):
        front.append((x, 1))
    # Second row
    for x in range(4, 12):
        front.append((x, 2))
    # Side bits
    front.append((4, 3))
    front.append((11, 3))

    back = list(front)  # Same from behind
    # Add back coverage
    for x in range(5, 11):
        back.append((x, 3))

    left = []
    for x in range(5, 11):
        left.append((x, 1))
    for x in range(4, 11):
        left.append((x, 2))
    left.append((4, 3))
    left.append((4, 4))

    right = []
    for x in range(5, 11):
        right.append((x, 1))
    for x in range(5, 12):
        right.append((x, 2))
    right.append((11, 3))
    right.append((11, 4))

    return {"down": front, "up": back, "left": left, "right": right}


def _make_hair_long():
    """Long hair that drapes down past the shoulders."""
    front = []
    for x in range(5, 11):
        front.append((x, 1))
    for x in range(4, 12):
        front.append((x, 2))
    # Side drapes
    front.append((4, 3))
    front.append((4, 4))
    front.append((4, 5))
    front.append((4, 6))
    front.append((4, 7))
    front.append((11, 3))
    front.append((11, 4))
    front.append((11, 5))
    front.append((11, 6))
    front.append((11, 7))

    back = []
    for x in range(5, 11):
        back.append((x, 1))
    for x in range(4, 12):
        back.append((x, 2))
    for x in range(4, 12):
        back.append((x, 3))
    for x in range(4, 12):
        back.append((x, 4))
    # Drape down the back
    for x in range(5, 11):
        back.append((x, 5))
        back.append((x, 6))
        back.append((x, 7))
        back.append((x, 8))
    front.append((4, 3))
    front.append((11, 3))

    left = []
    for x in range(5, 11):
        left.append((x, 1))
    for x in range(4, 11):
        left.append((x, 2))
    for x in range(4, 10):
        left.append((x, 3))
    left.append((4, 4))
    left.append((4, 5))
    left.append((4, 6))
    left.append((4, 7))
    left.append((4, 8))

    right = []
    for x in range(5, 11):
        right.append((x, 1))
    for x in range(5, 12):
        right.append((x, 2))
    for x in range(6, 12):
        right.append((x, 3))
    right.append((11, 4))
    right.append((11, 5))
    right.append((11, 6))
    right.append((11, 7))
    right.append((11, 8))

    return {"down": front, "up": back, "left": left, "right": right}


def _make_hair_afro():
    """Big round afro — extends above and around the head."""
    front = []
    # Very top — narrow
    for x in range(6, 10):
        front.append((x, 0))
    # Full width rows
    for x in range(4, 12):
        front.append((x, 1))
    for x in range(3, 13):
        front.append((x, 2))
    for x in range(3, 13):
        front.append((x, 3))
    # Sides only at face level
    front.append((3, 4))
    front.append((3, 5))
    front.append((12, 4))
    front.append((12, 5))

    back = []
    for x in range(6, 10):
        back.append((x, 0))
    for x in range(4, 12):
        back.append((x, 1))
    for x in range(3, 13):
        back.append((x, 2))
    for x in range(3, 13):
        back.append((x, 3))
    for x in range(3, 13):
        back.append((x, 4))
    for x in range(4, 12):
        back.append((x, 5))

    left = []
    for x in range(5, 10):
        left.append((x, 0))
    for x in range(3, 11):
        left.append((x, 1))
    for x in range(3, 11):
        left.append((x, 2))
    for x in range(3, 10):
        left.append((x, 3))
    left.append((3, 4))
    left.append((3, 5))

    right = []
    for x in range(6, 11):
        right.append((x, 0))
    for x in range(5, 13):
        right.append((x, 1))
    for x in range(5, 13):
        right.append((x, 2))
    for x in range(6, 13):
        right.append((x, 3))
    right.append((12, 4))
    right.append((12, 5))

    return {"down": front, "up": back, "left": left, "right": right}


def _make_hair_ponytail():
    """Short top with a ponytail hanging down the back."""
    front = []
    for x in range(5, 11):
        front.append((x, 1))
    for x in range(4, 12):
        front.append((x, 2))
    front.append((4, 3))
    front.append((11, 3))

    back = []
    for x in range(5, 11):
        back.append((x, 1))
    for x in range(4, 12):
        back.append((x, 2))
    # Ponytail drop from center
    back.append((7, 3))
    back.append((8, 3))
    back.append((7, 4))
    back.append((8, 4))
    back.append((7, 5))
    back.append((8, 5))
    back.append((7, 6))
    back.append((8, 6))
    back.append((7, 7))
    back.append((8, 7))
    back.append((8, 8))

    left = []
    for x in range(5, 11):
        left.append((x, 1))
    for x in range(4, 11):
        left.append((x, 2))
    left.append((4, 3))

    right = []
    for x in range(5, 11):
        right.append((x, 1))
    for x in range(5, 12):
        right.append((x, 2))
    right.append((11, 3))

    return {"down": front, "up": back, "left": left, "right": right}


def _make_hair_spiky():
    """Spiky upward hair."""
    front = []
    # Spikes at top
    front.append((5, 0))
    front.append((7, 0))
    front.append((9, 0))
    front.append((10, 0))
    for x in range(5, 11):
        front.append((x, 1))
    for x in range(4, 12):
        front.append((x, 2))
    front.append((4, 3))
    front.append((11, 3))

    back = list(front)
    for x in range(5, 11):
        back.append((x, 3))

    left = []
    left.append((5, 0))
    left.append((7, 0))
    left.append((9, 0))
    for x in range(4, 11):
        left.append((x, 1))
    for x in range(4, 11):
        left.append((x, 2))
    left.append((4, 3))

    right = []
    right.append((6, 0))
    right.append((8, 0))
    right.append((10, 0))
    for x in range(5, 12):
        right.append((x, 1))
    for x in range(5, 12):
        right.append((x, 2))
    right.append((11, 3))

    return {"down": front, "up": back, "left": left, "right": right}


HAIR_STYLES = {
    "short": _make_hair_short(),
    "long": _make_hair_long(),
    "afro": _make_hair_afro(),
    "ponytail": _make_hair_ponytail(),
    "spiky": _make_hair_spiky(),
}

# Default hair style per preset index (cycles through styles)
DEFAULT_HAIR = ["short", "short", "short", "afro", "long", "ponytail", "spiky", "long"]


# ---------------------------------------------------------------------------
# PIXEL TEMPLATES
#
# The base character body is drawn pixel-by-pixel per direction.
# Each template is a list of (x, y, color_key) tuples defining every pixel.
# "shade" suffix means use the darker tone of that color.
#
# Head occupies roughly rows 1-6 (large chibi head).
# Body occupies rows 7-12.
# Legs/feet occupy rows 13-15.
# ---------------------------------------------------------------------------

def _build_body_down():
    """Facing-down (toward camera) body template — no hair, no animation."""
    pixels = []

    # --- Head outline (rounded) ---
    # Row 1: top of head
    for x in range(6, 10):
        pixels.append((x, 1, "outline"))
    # Row 2: wider
    pixels.append((5, 2, "outline"))
    for x in range(6, 10):
        pixels.append((x, 2, "skin"))
    pixels.append((10, 2, "outline"))
    # Row 3
    pixels.append((4, 3, "outline"))
    for x in range(5, 11):
        pixels.append((x, 3, "skin"))
    pixels.append((11, 3, "outline"))
    # Row 4 — eyes row
    pixels.append((4, 4, "outline"))
    pixels.append((5, 4, "skin"))
    pixels.append((6, 4, "eye_white"))
    pixels.append((7, 4, "eye"))
    pixels.append((8, 4, "skin"))
    pixels.append((9, 4, "eye_white"))
    pixels.append((10, 4, "eye"))
    pixels.append((11, 4, "outline"))
    # Row 5 — lower face
    pixels.append((4, 5, "outline"))
    for x in range(5, 11):
        pixels.append((x, 5, "skin"))
    pixels.append((11, 5, "outline"))
    # Row 6 — chin (narrower)
    pixels.append((5, 6, "outline"))
    for x in range(6, 10):
        pixels.append((x, 6, "skin_shade"))
    pixels.append((10, 6, "outline"))

    # --- Torso ---
    # Row 7 — neck/top of shirt
    pixels.append((6, 7, "outline"))
    pixels.append((7, 7, "shirt"))
    pixels.append((8, 7, "shirt"))
    pixels.append((9, 7, "outline"))
    # Row 8 — full shirt with arms
    pixels.append((4, 8, "outline"))
    pixels.append((5, 8, "shirt"))
    for x in range(6, 10):
        pixels.append((x, 8, "shirt"))
    pixels.append((10, 8, "shirt"))
    pixels.append((11, 8, "outline"))
    # Row 9
    pixels.append((4, 9, "outline"))
    pixels.append((5, 9, "shirt_shade"))
    for x in range(6, 10):
        pixels.append((x, 9, "shirt"))
    pixels.append((10, 9, "shirt_shade"))
    pixels.append((11, 9, "outline"))
    # Row 10 — bottom of shirt
    pixels.append((5, 10, "outline"))
    for x in range(6, 10):
        pixels.append((x, 10, "shirt_shade"))
    pixels.append((10, 10, "outline"))

    # --- Legs ---
    # Row 11
    pixels.append((5, 11, "outline"))
    pixels.append((6, 11, "pants"))
    pixels.append((7, 11, "pants"))
    pixels.append((8, 11, "pants"))
    pixels.append((9, 11, "pants"))
    pixels.append((10, 11, "outline"))
    # Row 12
    pixels.append((5, 12, "outline"))
    pixels.append((6, 12, "pants_shade"))
    pixels.append((7, 12, "outline"))
    pixels.append((8, 12, "outline"))
    pixels.append((9, 12, "pants_shade"))
    pixels.append((10, 12, "outline"))

    # --- Feet ---
    # Row 13
    pixels.append((5, 13, "outline"))
    pixels.append((6, 13, "shoes"))
    pixels.append((7, 13, "outline"))
    pixels.append((8, 13, "outline"))
    pixels.append((9, 13, "shoes"))
    pixels.append((10, 13, "outline"))
    # Row 14
    pixels.append((5, 14, "outline"))
    pixels.append((6, 14, "shoes_shade"))
    pixels.append((7, 14, "outline"))
    pixels.append((8, 14, "outline"))
    pixels.append((9, 14, "shoes_shade"))
    pixels.append((10, 14, "outline"))

    return pixels


def _build_body_up():
    """Facing-up (away from camera) body template."""
    pixels = []

    # --- Head outline (rounded, back of head) ---
    for x in range(6, 10):
        pixels.append((x, 1, "outline"))
    pixels.append((5, 2, "outline"))
    for x in range(6, 10):
        pixels.append((x, 2, "skin_shade"))
    pixels.append((10, 2, "outline"))
    pixels.append((4, 3, "outline"))
    for x in range(5, 11):
        pixels.append((x, 3, "skin_shade"))
    pixels.append((11, 3, "outline"))
    # Row 4 — no eyes from behind
    pixels.append((4, 4, "outline"))
    for x in range(5, 11):
        pixels.append((x, 4, "skin_shade"))
    pixels.append((11, 4, "outline"))
    pixels.append((4, 5, "outline"))
    for x in range(5, 11):
        pixels.append((x, 5, "skin"))
    pixels.append((11, 5, "outline"))
    pixels.append((5, 6, "outline"))
    for x in range(6, 10):
        pixels.append((x, 6, "skin_shade"))
    pixels.append((10, 6, "outline"))

    # --- Torso (back view) ---
    pixels.append((6, 7, "outline"))
    pixels.append((7, 7, "shirt_shade"))
    pixels.append((8, 7, "shirt_shade"))
    pixels.append((9, 7, "outline"))
    pixels.append((4, 8, "outline"))
    pixels.append((5, 8, "shirt_shade"))
    for x in range(6, 10):
        pixels.append((x, 8, "shirt"))
    pixels.append((10, 8, "shirt_shade"))
    pixels.append((11, 8, "outline"))
    pixels.append((4, 9, "outline"))
    pixels.append((5, 9, "shirt_shade"))
    for x in range(6, 10):
        pixels.append((x, 9, "shirt_shade"))
    pixels.append((10, 9, "shirt_shade"))
    pixels.append((11, 9, "outline"))
    pixels.append((5, 10, "outline"))
    for x in range(6, 10):
        pixels.append((x, 10, "shirt_shade"))
    pixels.append((10, 10, "outline"))

    # --- Legs ---
    pixels.append((5, 11, "outline"))
    pixels.append((6, 11, "pants_shade"))
    pixels.append((7, 11, "pants"))
    pixels.append((8, 11, "pants"))
    pixels.append((9, 11, "pants_shade"))
    pixels.append((10, 11, "outline"))
    pixels.append((5, 12, "outline"))
    pixels.append((6, 12, "pants_shade"))
    pixels.append((7, 12, "outline"))
    pixels.append((8, 12, "outline"))
    pixels.append((9, 12, "pants_shade"))
    pixels.append((10, 12, "outline"))

    # --- Feet ---
    pixels.append((5, 13, "outline"))
    pixels.append((6, 13, "shoes_shade"))
    pixels.append((7, 13, "outline"))
    pixels.append((8, 13, "outline"))
    pixels.append((9, 13, "shoes_shade"))
    pixels.append((10, 13, "outline"))
    pixels.append((5, 14, "outline"))
    pixels.append((6, 14, "shoes_shade"))
    pixels.append((7, 14, "outline"))
    pixels.append((8, 14, "outline"))
    pixels.append((9, 14, "shoes_shade"))
    pixels.append((10, 14, "outline"))

    return pixels


def _build_body_left():
    """Facing-left body template (side profile)."""
    pixels = []

    # --- Head (side profile, shifted left) ---
    for x in range(5, 9):
        pixels.append((x, 1, "outline"))
    pixels.append((4, 2, "outline"))
    for x in range(5, 9):
        pixels.append((x, 2, "skin"))
    pixels.append((9, 2, "outline"))
    pixels.append((3, 3, "outline"))
    for x in range(4, 10):
        pixels.append((x, 3, "skin"))
    pixels.append((10, 3, "outline"))
    # Row 4 — eye (only left eye visible)
    pixels.append((3, 4, "outline"))
    pixels.append((4, 4, "skin"))
    pixels.append((5, 4, "eye_white"))
    pixels.append((6, 4, "eye"))
    pixels.append((7, 4, "skin"))
    pixels.append((8, 4, "skin"))
    pixels.append((9, 4, "skin_shade"))
    pixels.append((10, 4, "outline"))
    pixels.append((3, 5, "outline"))
    for x in range(4, 10):
        pixels.append((x, 5, "skin"))
    pixels.append((10, 5, "outline"))
    pixels.append((4, 6, "outline"))
    for x in range(5, 9):
        pixels.append((x, 6, "skin_shade"))
    pixels.append((9, 6, "outline"))

    # --- Torso (side) ---
    pixels.append((5, 7, "outline"))
    pixels.append((6, 7, "shirt"))
    pixels.append((7, 7, "shirt"))
    pixels.append((8, 7, "outline"))
    pixels.append((4, 8, "outline"))
    pixels.append((5, 8, "shirt"))
    pixels.append((6, 8, "shirt"))
    pixels.append((7, 8, "shirt"))
    pixels.append((8, 8, "shirt_shade"))
    pixels.append((9, 8, "outline"))
    pixels.append((4, 9, "outline"))
    pixels.append((5, 9, "shirt"))
    pixels.append((6, 9, "shirt"))
    pixels.append((7, 9, "shirt_shade"))
    pixels.append((8, 9, "shirt_shade"))
    pixels.append((9, 9, "outline"))
    pixels.append((5, 10, "outline"))
    pixels.append((6, 10, "shirt_shade"))
    pixels.append((7, 10, "shirt_shade"))
    pixels.append((8, 10, "outline"))

    # --- Legs (side) ---
    pixels.append((5, 11, "outline"))
    pixels.append((6, 11, "pants"))
    pixels.append((7, 11, "pants"))
    pixels.append((8, 11, "outline"))
    pixels.append((5, 12, "outline"))
    pixels.append((6, 12, "pants_shade"))
    pixels.append((7, 12, "pants_shade"))
    pixels.append((8, 12, "outline"))

    # --- Feet (side) ---
    pixels.append((4, 13, "outline"))
    pixels.append((5, 13, "shoes"))
    pixels.append((6, 13, "shoes"))
    pixels.append((7, 13, "outline"))
    pixels.append((4, 14, "outline"))
    pixels.append((5, 14, "shoes_shade"))
    pixels.append((6, 14, "shoes_shade"))
    pixels.append((7, 14, "outline"))

    return pixels


def _build_body_right():
    """Facing-right body template (mirror of left)."""
    left = _build_body_left()
    # Mirror horizontally: new_x = (FRAME_W - 1) - old_x
    return [(FRAME_W - 1 - x, y, c) for x, y, c in left]


BODY_TEMPLATES = {
    "down": _build_body_down(),
    "up": _build_body_up(),
    "left": _build_body_left(),
    "right": _build_body_right(),
}

# ---------------------------------------------------------------------------
# ANIMATION DATA
#
# Each walk frame applies pixel offsets to specific body regions.
# We define regions by Y-range and apply (dx, dy) shifts.
# Region keys: "head" (y 1-6), "torso" (y 7-10), "arm_l"/"arm_r",
# "leg_l" (y 11-14 left half), "leg_r" (y 11-14 right half)
# ---------------------------------------------------------------------------

def _region_for_pixel(x, y, direction):
    """Classify a body pixel into an animation region."""
    if y <= 6:
        return "head"
    if y <= 10:
        # Arm detection based on x position
        if direction in ("down", "up"):
            if x <= 5:
                return "arm_l"
            if x >= 10:
                return "arm_r"
        elif direction == "left":
            if x <= 4:
                return "arm_l"
            if x >= 9:
                return "arm_r"
        elif direction == "right":
            if x >= 11:
                return "arm_r"
            if x <= 6:
                return "arm_l"
        return "torso"
    # Legs and feet
    if direction in ("down", "up"):
        if x <= 7:
            return "leg_l"
        return "leg_r"
    else:
        # Side view — treat as single leg pair for simpler animation
        if y <= 12:
            return "leg_l"  # front leg
        return "leg_r"  # back leg / feet


# Walk cycle offsets per region: [frame0, frame1, frame2, frame3]
# Frame 0 = stand, 1 = step left, 2 = stand, 3 = step right
WALK_OFFSETS = {
    "down": {
        "head":  [(0, 0), (0, -1), (0, 0), (0, -1)],
        "torso": [(0, 0), (0, 0),  (0, 0), (0, 0)],
        "arm_l": [(0, 0), (0, -1), (0, 0), (0, 1)],
        "arm_r": [(0, 0), (0, 1),  (0, 0), (0, -1)],
        "leg_l": [(0, 0), (0, 1),  (0, 0), (0, -1)],
        "leg_r": [(0, 0), (0, -1), (0, 0), (0, 1)],
    },
    "up": {
        "head":  [(0, 0), (0, -1), (0, 0), (0, -1)],
        "torso": [(0, 0), (0, 0),  (0, 0), (0, 0)],
        "arm_l": [(0, 0), (0, -1), (0, 0), (0, 1)],
        "arm_r": [(0, 0), (0, 1),  (0, 0), (0, -1)],
        "leg_l": [(0, 0), (0, 1),  (0, 0), (0, -1)],
        "leg_r": [(0, 0), (0, -1), (0, 0), (0, 1)],
    },
    "left": {
        "head":  [(0, 0), (0, -1), (0, 0), (0, -1)],
        "torso": [(0, 0), (0, 0),  (0, 0), (0, 0)],
        "arm_l": [(0, 0), (0, 1),  (0, 0), (0, -1)],
        "arm_r": [(0, 0), (0, -1), (0, 0), (0, 1)],
        "leg_l": [(0, 0), (0, 1),  (0, 0), (0, -1)],
        "leg_r": [(0, 0), (0, -1), (0, 0), (0, 1)],
    },
    "right": {
        "head":  [(0, 0), (0, -1), (0, 0), (0, -1)],
        "torso": [(0, 0), (0, 0),  (0, 0), (0, 0)],
        "arm_l": [(0, 0), (0, -1), (0, 0), (0, 1)],
        "arm_r": [(0, 0), (0, 1),  (0, 0), (0, -1)],
        "leg_l": [(0, 0), (0, 1),  (0, 0), (0, -1)],
        "leg_r": [(0, 0), (0, -1), (0, 0), (0, 1)],
    },
}


# ---------------------------------------------------------------------------
# RENDERING
# ---------------------------------------------------------------------------

def render_frame(direction: str, frame_idx: int, palette: dict, hair_style: str) -> Image.Image:
    """Render a single 16x16 frame."""
    img = Image.new("RGBA", (FRAME_W, FRAME_H), (0, 0, 0, 0))

    body_pixels = BODY_TEMPLATES[direction]
    offsets = WALK_OFFSETS[direction]

    # Draw body pixels with animation offsets
    for bx, by, color_key in body_pixels:
        region = _region_for_pixel(bx, by, direction)
        dx, dy = offsets[region][frame_idx]
        px, py = bx + dx, by + dy
        if 0 <= px < FRAME_W and 0 <= py < FRAME_H:
            color = palette[color_key]
            img.putpixel((px, py), color)

    # Draw hair on top (hair moves with head)
    hair_data = HAIR_STYLES.get(hair_style, HAIR_STYLES["short"])
    hair_pixels = hair_data.get(direction, [])
    head_dx, head_dy = offsets["head"][frame_idx]
    for hx, hy in hair_pixels:
        px, py = hx + head_dx, hy + head_dy
        if 0 <= px < FRAME_W and 0 <= py < FRAME_H:
            # Use shade for pixels that overlap with lower hair area
            if hy >= 3:
                img.putpixel((px, py), palette["hair_shade"])
            else:
                img.putpixel((px, py), palette["hair"])

    return img


def build_spritesheet(palette: dict, hair_style: str = "short") -> tuple[Image.Image, dict]:
    """Build the full spritesheet and return (image, atlas_data)."""
    cols = FRAMES_PER_DIR
    rows = len(DIRECTIONS)
    sheet_w = cols * (FRAME_W + PADDING) - PADDING
    sheet_h = rows * (FRAME_H + PADDING) - PADDING

    sheet = Image.new("RGBA", (sheet_w, sheet_h), (0, 0, 0, 0))
    frames_meta: dict = {}

    for row, direction in enumerate(DIRECTIONS):
        for col in range(FRAMES_PER_DIR):
            frame_img = render_frame(direction, col, palette, hair_style)
            x = col * (FRAME_W + PADDING)
            y = row * (FRAME_H + PADDING)
            sheet.paste(frame_img, (x, y))

            frame_name = f"walk_{direction}_{col}"
            frames_meta[frame_name] = {
                "frame": {"x": x, "y": y, "w": FRAME_W, "h": FRAME_H},
                "rotated": False,
                "trimmed": False,
                "spriteSourceSize": {"x": 0, "y": 0, "w": FRAME_W, "h": FRAME_H},
                "sourceSize": {"w": FRAME_W, "h": FRAME_H},
            }

    return sheet, frames_meta


def build_atlas(sprite_name: str, image_file: str, frames_meta: dict, sheet_size: tuple[int, int]) -> dict:
    """Build a Phaser-compatible JSON texture atlas."""
    return {
        "frames": frames_meta,
        "meta": {
            "app": "sprite-generator",
            "version": "2.0",
            "image": image_file,
            "format": "RGBA8888",
            "size": {"w": sheet_size[0], "h": sheet_size[1]},
            "scale": "1",
            "smartupdate": "",
        },
    }


def build_preview_html(sprite_name: str, image_file: str, atlas_file: str) -> str:
    """Generate a standalone HTML file that animates the spritesheet in-browser."""
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
  .info {{ color: #888; margin-bottom: 1.5rem; }}
  canvas {{
    image-rendering: pixelated;
    image-rendering: crisp-edges;
    border: 1px solid #444;
    margin-bottom: 1rem;
  }}
  .controls {{
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
  }}
  button {{
    background: #333;
    color: #eee;
    border: 1px solid #555;
    padding: 0.4rem 1rem;
    cursor: pointer;
    font-family: monospace;
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
<p class="info">Generated spritesheet preview — v2 (pixel art style)</p>

<canvas id="anim" width="{FRAME_W * 8}" height="{FRAME_H * 8}"></canvas>

<div class="controls">
  <button data-dir="0" class="active">Down</button>
  <button data-dir="1">Left</button>
  <button data-dir="2">Right</button>
  <button data-dir="3">Up</button>
</div>

<p class="info">Full spritesheet:</p>
<img class="sheet-preview" id="sheetImg" />

<script>
const FRAME_W = {FRAME_W};
const FRAME_H = {FRAME_H};
const COLS = {FRAMES_PER_DIR};
const SCALE = 8;
const FPS = 6;

const canvas = document.getElementById("anim");
const ctx = canvas.getContext("2d");
ctx.imageSmoothingEnabled = false;

const img = new Image();
img.src = "{image_file}";

let dirRow = 0;
let frameIdx = 0;

img.onload = () => {{
  document.getElementById("sheetImg").src = "{image_file}";
  document.getElementById("sheetImg").style.width = (img.width * 4) + "px";
  setInterval(() => {{
    frameIdx = (frameIdx + 1) % COLS;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(
      img,
      frameIdx * FRAME_W, dirRow * FRAME_H, FRAME_W, FRAME_H,
      0, 0, FRAME_W * SCALE, FRAME_H * SCALE
    );
  }}, 1000 / FPS);
}};

document.querySelectorAll("button[data-dir]").forEach(btn => {{
  btn.addEventListener("click", () => {{
    dirRow = parseInt(btn.dataset.dir);
    document.querySelectorAll("button[data-dir]").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
  }});
}});
</script>
</body>
</html>"""


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Generate a top-down character spritesheet (pixel art style).")
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
        print(f"\nHair styles: {', '.join(HAIR_STYLES.keys())}")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if args.all:
        # Generate all presets
        for i, preset in enumerate(PRESETS):
            hair = DEFAULT_HAIR[i] if i < len(DEFAULT_HAIR) else "short"
            _generate_one(f"char_{i}", preset, hair, i)
        print(f"\nGenerated {len(PRESETS)} characters.")
        return

    # Single generation
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

    total_frames = len(DIRECTIONS) * FRAMES_PER_DIR
    print(f"  Style:       {palette['name']} | hair: {hair_style}")
    print(f"  Frames:      {total_frames} ({len(DIRECTIONS)} dirs x {FRAMES_PER_DIR} frames)")
    print(f"  Frame size:  {FRAME_W}x{FRAME_H}px\n")


if __name__ == "__main__":
    main()
