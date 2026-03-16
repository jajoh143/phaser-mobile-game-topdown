#!/usr/bin/env python3
"""
Top-down chibi character sprite generator for Phaser 3.

Generates 32x32 spritesheets with SNES-inspired chibi proportions:
  - Moderate round head (~40% of sprite) with 2x2 eyes, catchlight, and
    forehead highlight for 3/4 top-down depth
  - Shoulder step-out (14px) tapering to waist (10px) with belt-line detail
  - 2px leg gap for clear readability in front/back views
  - Thick 3px-wide arms hanging from shoulder pivots
  - Detailed hair with 3-tone shading (highlight, base, shade)
  - Clothing with shirt/pants/shoes distinction and belt-line detail
  - Hue-shifted shadows (cool-shifted) for depth and richness
  - Selective outlining (sel-out): lighter outlines on light-facing edges
  - Forehead highlight and interior torso shading for depth

Sprites are 32x32 native, fitting 1:1 on 32x32 world tiles in Phaser.

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
FRAME_W = 32
FRAME_H = 32
TILE_SIZE = 32  # world grid is 32x32; sprites render at 1x

DIRECTIONS = ["down", "left", "right", "up"]
FRAMES_PER_DIR = 4
ANIMATIONS = ["walk", "jump", "crouch", "interact"]

# ---------------------------------------------------------------------------
# COLOR PALETTES
# ---------------------------------------------------------------------------
PRESETS = [
    {
        "name": "Blue hair, red shirt",
        "skin": (235, 190, 160, 255),
        "skin_shade": (208, 158, 148, 255),       # hue-shifted toward rose
        "hair": (55, 60, 120, 255),
        "hair_shade": (35, 38, 95, 255),           # shifted toward deeper blue
        "hair_highlight": (75, 80, 150, 255),
        "shirt": (190, 60, 55, 255),
        "shirt_shade": (148, 38, 55, 255),         # red shifted toward maroon
        "pants": (60, 75, 135, 255),               # blue jeans
        "pants_shade": (40, 52, 108, 255),         # shifted toward deeper blue
        "shoes": (55, 45, 40, 255),
        "shoes_shade": (38, 30, 38, 255),          # shifted toward purple
        "outline": (25, 20, 42, 255),              # dark navy-purple
        "eye": (28, 28, 35, 255),
    },
    {
        "name": "Green goblin, teal tunic",
        "skin": (85, 160, 95, 255),
        "skin_shade": (58, 125, 82, 255),          # green shifted toward teal
        "hair": (55, 120, 65, 255),
        "hair_shade": (32, 88, 58, 255),           # shifted toward teal
        "hair_highlight": (75, 145, 85, 255),
        "shirt": (60, 135, 140, 255),
        "shirt_shade": (38, 98, 118, 255),         # teal shifted toward blue
        "pants": (55, 100, 105, 255),
        "pants_shade": (35, 72, 90, 255),          # shifted toward blue
        "shoes": (50, 42, 36, 255),
        "shoes_shade": (34, 28, 30, 255),          # shifted toward cool
        "outline": (18, 32, 30, 255),              # dark teal
        "eye": (25, 25, 30, 255),
    },
    {
        "name": "White hair, mint shirt",
        "skin": (235, 200, 175, 255),
        "skin_shade": (212, 175, 162, 255),        # shifted toward lavender
        "hair": (220, 225, 230, 255),
        "hair_shade": (182, 188, 205, 255),        # shifted toward blue-grey
        "hair_highlight": (242, 245, 248, 255),
        "shirt": (140, 210, 185, 255),
        "shirt_shade": (105, 172, 165, 255),       # mint shifted toward teal
        "pants": (225, 218, 205, 255),             # cream / khaki
        "pants_shade": (192, 182, 168, 255),       # shifted toward warm grey
        "shoes": (52, 42, 38, 255),
        "shoes_shade": (36, 28, 32, 255),          # shifted toward cool
        "outline": (22, 24, 40, 255),              # dark slate-blue
        "eye": (28, 28, 35, 255),
    },
    {
        "name": "Red beard, brown outfit",
        "skin": (225, 175, 140, 255),
        "skin_shade": (198, 148, 128, 255),        # shifted toward rose
        "hair": (195, 80, 35, 255),
        "hair_shade": (152, 52, 30, 255),          # shifted toward deeper red
        "hair_highlight": (225, 110, 55, 255),
        "shirt": (140, 100, 65, 255),
        "shirt_shade": (108, 72, 55, 255),         # brown shifted toward olive
        "pants": (95, 75, 52, 255),                # darker brown leather
        "pants_shade": (68, 50, 38, 255),          # shifted toward warm brown
        "shoes": (55, 42, 35, 255),
        "shoes_shade": (38, 28, 30, 255),          # shifted toward maroon
        "outline": (32, 20, 22, 255),              # dark brown-red
        "eye": (28, 25, 25, 255),
    },
    {
        "name": "Purple hair, dark cloak",
        "skin": (230, 195, 165, 255),
        "skin_shade": (202, 165, 150, 255),        # shifted toward mauve
        "hair": (120, 70, 145, 255),
        "hair_shade": (85, 42, 115, 255),          # shifted toward deep violet
        "hair_highlight": (150, 95, 175, 255),
        "shirt": (55, 48, 65, 255),
        "shirt_shade": (35, 28, 52, 255),          # shifted toward indigo
        "pants": (48, 42, 58, 255),
        "pants_shade": (32, 26, 48, 255),          # shifted toward deep blue
        "shoes": (40, 35, 45, 255),
        "shoes_shade": (26, 22, 36, 255),          # shifted toward indigo
        "outline": (22, 18, 40, 255),              # dark purple
        "eye": (25, 22, 30, 255),
    },
    {
        "name": "Cowboy hat, green vest",
        "skin": (225, 185, 148, 255),
        "skin_shade": (198, 155, 132, 255),        # shifted toward rose
        "hair": (100, 75, 50, 255),
        "hair_shade": (70, 48, 40, 255),           # shifted toward warm brown
        "hair_highlight": (128, 98, 68, 255),
        "shirt": (75, 140, 72, 255),
        "shirt_shade": (50, 108, 62, 255),         # green shifted toward teal
        "pants": (140, 120, 85, 255),              # tan / sandy
        "pants_shade": (108, 88, 62, 255),         # shifted toward warm brown
        "shoes": (52, 42, 36, 255),
        "shoes_shade": (35, 28, 30, 255),          # shifted toward cool
        "outline": (25, 22, 28, 255),              # dark olive-grey
        "eye": (25, 25, 30, 255),
    },
    {
        "name": "Dark skin, orange hair",
        "skin": (140, 95, 65, 255),
        "skin_shade": (112, 70, 55, 255),          # shifted toward brown-red
        "hair": (220, 140, 45, 255),
        "hair_shade": (182, 105, 35, 255),         # orange shifted toward red
        "hair_highlight": (245, 170, 65, 255),
        "shirt": (60, 120, 155, 255),
        "shirt_shade": (38, 88, 132, 255),         # shifted toward deeper blue
        "pants": (55, 55, 70, 255),
        "pants_shade": (38, 35, 58, 255),          # shifted toward blue
        "shoes": (48, 38, 32, 255),
        "shoes_shade": (32, 24, 28, 255),          # shifted toward cool
        "outline": (22, 16, 24, 255),              # dark plum-brown
        "eye": (22, 22, 28, 255),
    },
    {
        "name": "Pink hair, chef outfit",
        "skin": (238, 205, 178, 255),
        "skin_shade": (215, 178, 165, 255),        # shifted toward rose
        "hair": (215, 120, 140, 255),
        "hair_shade": (178, 85, 118, 255),         # pink shifted toward mauve
        "hair_highlight": (238, 150, 168, 255),
        "shirt": (232, 232, 238, 255),
        "shirt_shade": (198, 195, 215, 255),       # shifted toward cool grey-blue
        "pants": (55, 55, 68, 255),                # dark charcoal (chef's pants)
        "pants_shade": (38, 35, 55, 255),          # shifted toward blue-grey
        "shoes": (52, 42, 38, 255),
        "shoes_shade": (36, 28, 32, 255),          # shifted toward cool
        "outline": (25, 18, 35, 255),              # dark rose-purple
        "eye": (28, 25, 28, 255),
    },
]


def _derive_palette(preset: dict) -> dict:
    """Derive additional colors from a base preset for enhanced rendering.

    Adds: eye_highlight, eye_white, skin_highlight, shirt_highlight,
          belt, outline_light (sel-out), skin_aa, shirt_aa (curve smoothing).
    """
    pal = dict(preset)

    # Eye catchlight — bright white with slight warmth
    pal["eye_highlight"] = (255, 255, 248, 255)

    # Eye white — off-white for the visible sclera portion
    pal["eye_white"] = (235, 232, 228, 255)

    # Skin highlight — shift toward yellow/warm, lighten
    sr, sg, sb, sa = pal["skin"]
    pal["skin_highlight"] = (
        min(sr + 18, 255),
        min(sg + 12, 255),
        min(sb + 2, 255),
        sa,
    )

    # Shirt highlight — lighten and warm slightly
    tr, tg, tb, ta = pal["shirt"]
    pal["shirt_highlight"] = (
        min(tr + 25, 255),
        min(tg + 20, 255),
        min(tb + 15, 255),
        ta,
    )

    # Belt — midpoint between shirt_shade and pants, slightly darker
    shr, shg, shb, sha = pal["shirt_shade"]
    pr, pg, pb, _ = pal["pants"]
    pal["belt"] = (
        max((shr + pr) // 2 - 15, 0),
        max((shg + pg) // 2 - 15, 0),
        max((shb + pb) // 2 - 10, 0),
        sha,
    )

    # Sel-out: lighter outline for light-facing edges (top/shoulders)
    # Blend outline toward shirt base color
    olr, olg, olb, ola = pal["outline"]
    pal["outline_light"] = (
        min(olr + 40, 180),
        min(olg + 35, 180),
        min(olb + 35, 180),
        ola,
    )

    # Manual AA color — midpoint between outline and skin, for smoothing
    # stair-step transitions on the head/chin curves
    pal["skin_aa"] = (
        (olr + sr) // 2,
        (olg + sg) // 2,
        (olb + sb) // 2,
        sa,
    )

    # AA color for shirt edge transitions
    pal["shirt_aa"] = (
        (olr + tr) // 2,
        (olg + tg) // 2,
        (olb + tb) // 2,
        ta,
    )

    return pal


# ---------------------------------------------------------------------------
# HAIR STYLES — pixel masks for 32x32
#
# Smaller head: y=5..15, x=7..24 (18px wide max).
# Hair wraps around top and sides.
# Each direction returns list of (x, y, shade):
#   0=base, 1=shade(dark), 2=highlight(light)
# ---------------------------------------------------------------------------

def _hr(y, xs, xe, s=0):
    """Hair row helper — range of pixels at y from xs to xe (inclusive)."""
    return [(x, y, s) for x in range(xs, xe + 1)]


def _make_hair_short():
    """Short bowl/cap hair — classic chibi style."""
    front = []
    front += _hr(2, 12, 19, 2)      # highlight at very top
    front += _hr(3, 10, 21, 0)
    front += _hr(4, 8, 23, 0)
    front += _hr(5, 7, 24, 0)       # overlaps head top
    front += _hr(6, 7, 24, 1)       # shade at forehead line
    # Side tufts
    for y in range(7, 10):
        front += [(7, y, 1), (24, y, 1)]

    back = []
    back += _hr(2, 12, 19, 1)
    back += _hr(3, 10, 21, 1)
    back += _hr(4, 8, 23, 1)
    for y in range(5, 10):
        back += _hr(y, 7, 24, 1)

    left = []
    left += _hr(2, 11, 18, 2)
    left += _hr(3, 9, 20, 0)
    left += _hr(4, 7, 21, 0)
    left += _hr(5, 6, 22, 0)
    left += _hr(6, 6, 22, 1)
    for y in range(7, 10):
        left += [(6, y, 1)]

    right = [(FRAME_W - 1 - x, y, s) for x, y, s in left]
    return {"down": front, "up": back, "left": left, "right": right}


def _make_hair_long():
    """Long flowing hair — drapes past shoulders."""
    front = []
    front += _hr(2, 12, 19, 2)
    front += _hr(3, 10, 21, 0)
    front += _hr(4, 8, 23, 0)
    front += _hr(5, 7, 24, 0)
    front += _hr(6, 7, 24, 1)
    # Long side strands draping down
    for y in range(7, 22):
        front += [(6, y, 1), (7, y, 1), (24, y, 1), (25, y, 1)]
    for y in range(7, 14):
        front += [(5, y, 1), (26, y, 1)]

    back = []
    back += _hr(2, 12, 19, 1)
    back += _hr(3, 10, 21, 1)
    back += _hr(4, 8, 23, 1)
    for y in range(5, 10):
        back += _hr(y, 7, 24, 1)
    for y in range(10, 22):
        back += _hr(y, 8, 23, 1)

    left = []
    left += _hr(2, 11, 18, 2)
    left += _hr(3, 9, 20, 0)
    left += _hr(4, 7, 21, 0)
    left += _hr(5, 6, 22, 0)
    left += _hr(6, 6, 22, 1)
    for y in range(7, 22):
        left += [(5, y, 1), (6, y, 1)]
    for y in range(7, 14):
        left += [(4, y, 1)]

    right = [(FRAME_W - 1 - x, y, s) for x, y, s in left]
    return {"down": front, "up": back, "left": left, "right": right}


def _make_hair_afro():
    """Big round afro — extends well above and around head."""
    front = []
    front += _hr(0, 12, 19, 2)
    front += _hr(1, 9, 22, 0)
    front += _hr(2, 7, 24, 0)
    for y in range(3, 7):
        front += _hr(y, 5, 26, 0)
    for y in range(7, 12):
        front += [(5, y, 1), (6, y, 1), (25, y, 1), (26, y, 1)]

    back = []
    back += _hr(0, 12, 19, 1)
    back += _hr(1, 9, 22, 1)
    back += _hr(2, 7, 24, 1)
    for y in range(3, 12):
        back += _hr(y, 5, 26, 1)

    left = []
    left += _hr(0, 11, 18, 2)
    left += _hr(1, 8, 21, 0)
    left += _hr(2, 6, 23, 0)
    for y in range(3, 7):
        left += _hr(y, 4, 24, 0)
    for y in range(7, 12):
        left += [(4, y, 1), (5, y, 1)]

    right = [(FRAME_W - 1 - x, y, s) for x, y, s in left]
    return {"down": front, "up": back, "left": left, "right": right}


def _make_hair_ponytail():
    """Short top with ponytail in back."""
    front = []
    front += _hr(2, 12, 19, 2)
    front += _hr(3, 10, 21, 0)
    front += _hr(4, 8, 23, 0)
    front += _hr(5, 7, 24, 0)
    front += _hr(6, 7, 24, 1)
    for y in range(7, 9):
        front += [(7, y, 1), (24, y, 1)]

    back = []
    back += _hr(2, 12, 19, 1)
    back += _hr(3, 10, 21, 0)
    back += _hr(4, 8, 23, 1)
    for y in range(5, 8):
        back += _hr(y, 7, 24, 1)
    # Ponytail
    for y in range(8, 14):
        back += [(15, y, 1), (16, y, 1)]
    for y in range(14, 22):
        back += [(15, y, 1)]

    left = []
    left += _hr(2, 11, 18, 2)
    left += _hr(3, 9, 20, 0)
    left += _hr(4, 7, 21, 0)
    left += _hr(5, 6, 22, 0)
    left += _hr(6, 6, 22, 1)

    right = [(FRAME_W - 1 - x, y, s) for x, y, s in left]
    return {"down": front, "up": back, "left": left, "right": right}


def _make_hair_spiky():
    """Sharp spiky hair — triangular points sticking up."""
    front = []
    # Spike tips
    front += [(10, 0, 2), (16, 0, 0), (22, 0, 2)]
    front += [(9, 1, 0), (10, 1, 0), (11, 1, 0),
              (15, 1, 0), (16, 1, 0), (17, 1, 0),
              (21, 1, 0), (22, 1, 0), (23, 1, 0)]
    front += _hr(2, 8, 23, 0)
    front += _hr(3, 7, 24, 0)
    front += _hr(4, 7, 24, 0)
    front += _hr(5, 7, 24, 0)
    front += _hr(6, 7, 24, 1)
    for y in range(7, 10):
        front += [(7, y, 1), (24, y, 1)]

    back = list(front[:])
    for y in range(7, 12):
        back += _hr(y, 7, 24, 1)

    left = []
    left += [(9, 0, 2), (15, 0, 0), (21, 0, 2)]
    left += _hr(1, 8, 22, 0)
    left += _hr(2, 7, 21, 0)
    left += _hr(3, 6, 21, 0)
    left += _hr(4, 6, 22, 0)
    left += _hr(5, 6, 22, 0)
    left += _hr(6, 6, 22, 1)
    for y in range(7, 10):
        left += [(6, y, 1)]

    right = [(FRAME_W - 1 - x, y, s) for x, y, s in left]
    return {"down": front, "up": back, "left": left, "right": right}


def _make_hair_wavy():
    """Medium-length wavy hair with texture."""
    front = []
    front += _hr(2, 11, 20, 2)
    front += _hr(3, 9, 22, 0)
    front += _hr(4, 7, 24, 0)
    front += _hr(5, 7, 24, 0)
    front += _hr(6, 7, 24, 1)
    # Wavy side strands
    for y in range(7, 16):
        front += [(6, y, 0 if y % 2 == 0 else 1),
                  (7, y, 1),
                  (24, y, 1),
                  (25, y, 0 if y % 2 == 0 else 1)]

    back = []
    back += _hr(2, 11, 20, 1)
    back += _hr(3, 9, 22, 1)
    back += _hr(4, 7, 24, 1)
    for y in range(5, 8):
        back += _hr(y, 7, 24, 1)
    for y in range(8, 16):
        back += _hr(y, 8, 23, 1)

    left = []
    left += _hr(2, 10, 19, 2)
    left += _hr(3, 8, 21, 0)
    left += _hr(4, 6, 22, 0)
    left += _hr(5, 6, 22, 0)
    left += _hr(6, 6, 22, 1)
    for y in range(7, 16):
        left += [(5, y, 0 if y % 2 == 0 else 1), (6, y, 1)]

    right = [(FRAME_W - 1 - x, y, s) for x, y, s in left]
    return {"down": front, "up": back, "left": left, "right": right}


HAIR_STYLES = {
    "short": _make_hair_short(),
    "long": _make_hair_long(),
    "afro": _make_hair_afro(),
    "ponytail": _make_hair_ponytail(),
    "spiky": _make_hair_spiky(),
    "wavy": _make_hair_wavy(),
}

DEFAULT_HAIR = ["short", "short", "short", "short", "long", "ponytail", "spiky", "wavy"]


# ---------------------------------------------------------------------------
# BODY TEMPLATES — 32x32 balanced chibi
#
# Layout (front-facing):
#   y 0-3:   hair overflow above head
#   y 4-6:   head top / hair overlap (smooth oval cap)
#   y 7-12:  head full width (eyes at y=10-11)
#   y 13-15: lower face, chin
#   y 16-17: neck / upper torso (8-12px)
#   y 18-19: shoulder flare (14px — step-out)
#   y 20-21: mid torso (12px)
#   y 22-24: waist taper + hips (10px)
#   y 25-27: pants (2px gap between legs)
#   y 28-29: shoes
#
# Arms are handled by the shoulder-pivot overlay system (3px wide, 6px long).
# ---------------------------------------------------------------------------

def _row(y, xs, xe, color, outline_l="outline", outline_r="outline"):
    """Row with outline on both edges, color fill in between.

    outline_l/outline_r can be changed for selective outlining (sel-out).
    """
    if xe - xs < 2:
        return [(x, y, outline_l) for x in range(xs, xe + 1)]
    p = [(xs, y, outline_l)]
    for x in range(xs + 1, xe):
        p.append((x, y, color))
    p.append((xe, y, outline_r))
    return p


def _build_body_down():
    """Facing down (toward camera)."""
    p = []

    # --- Head (smooth oval, 18px wide max) ---
    # Width progression: 8→12→14→16→18→18→18→18→18→16→14→12
    # Shading: directional light from top-left. Most face is base skin.
    # Shadow only on bottom 2 rows of chin and a few pixels on the right edge.
    # This avoids the harsh two-tone "pillow shading" look.
    p += _row(4, 12, 19, "skin", "outline_light", "outline_light")    #  8px - tiny cap
    p += _row(5, 10, 21, "skin", "outline_light", "outline_light")    # 12px
    p += _row(6, 9, 22, "skin", "outline_light", "outline_light")     # 14px
    p += _row(7, 8, 23, "skin")           # 16px
    for y in range(8, 13):
        p += _row(y, 7, 24, "skin")       # 18px - full width
    # Chin rows: mostly skin, with shade only at edges for roundness
    p += _row(13, 8, 23, "skin")          # 16px - still base skin
    p += _row(14, 9, 22, "skin_shade")    # 14px - shadow starts here (chin underside)
    p += _row(15, 10, 21, "skin_shade")   # 12px - bottom of chin

    # Subtle right-edge shadow (light from top-left): a few shade pixels
    # along the right side of the face at mid-height
    for y in range(10, 13):
        p.append((24, y, "skin_shade"))   # rightmost column shade

    # Manual AA on chin curve inner corners (where width steps down)
    p.append((8, 14, "skin_aa"))    # left inner corner (18→16 step)
    p.append((23, 14, "skin_aa"))   # right inner corner
    p.append((9, 15, "skin_aa"))    # left inner corner (16→14 step)
    p.append((22, 15, "skin_aa"))   # right inner corner

    # Forehead highlight (y=8, between hair and eyes — smaller, left-biased)
    for x in range(11, 18):
        p.append((x, 8, "skin_highlight"))

    # Eyes — 2w x 2h per eye with catchlight, placed at y=10-11
    # Chibi-style: eyes closer together for cute proportions.
    # Left eye (x=11-12), Right eye (x=19-20) — 6px gap between eyes
    #   [eye]       [highlight]
    #   [eye_white] [eye]
    p.append((11, 10, "eye"))             # left eye: dark upper-left
    p.append((12, 10, "eye_highlight"))   # left eye: catchlight upper-right
    p.append((11, 11, "eye"))             # left eye: dark lower-left
    p.append((12, 11, "eye_white"))       # left eye: sclera lower-right
    p.append((19, 10, "eye_highlight"))   # right eye: catchlight upper-left
    p.append((20, 10, "eye"))             # right eye: dark upper-right
    p.append((19, 11, "eye_white"))       # right eye: sclera lower-left
    p.append((20, 11, "eye"))             # right eye: dark lower-right

    # --- Torso / Shirt (smooth shoulder-to-waist taper) ---
    # Width: 8→10→14→14→12→12→10→10→10 (added intermediate row)
    # Sel-out: shoulders use outline_light, waist keeps dark outline
    p += _row(16, 12, 19, "shirt_shade")  # 8px - neck (head shadow)
    p += _row(17, 11, 20, "shirt_highlight", "outline_light", "outline_light")  # 10px highlight
    p += _row(18, 9, 22, "shirt", "outline_light", "outline_light")   # 14px shoulder flare
    p += _row(19, 9, 22, "shirt", "outline_light", "outline_light")   # 14px shoulders
    p += _row(20, 10, 21, "shirt")        # 12px
    p += _row(21, 10, 21, "shirt")        # 12px
    p += _row(22, 11, 20, "belt")         # 10px belt line
    p += _row(23, 11, 20, "pants")        # 10px waist (matches pants)
    p += _row(24, 11, 20, "pants")        # 10px hips (matches pants)

    # Torso AA: smooth the shoulder flare (10→14) outer corners
    p.append((10, 18, "shirt_aa"))   # left shoulder inner corner
    p.append((21, 18, "shirt_aa"))   # right shoulder inner corner
    # Torso AA: smooth shoulder→mid-torso (14→12) inner corners
    p.append((9, 20, "shirt_aa"))    # left under-arm inner corner
    p.append((22, 20, "shirt_aa"))   # right under-arm inner corner

    # Legs are drawn by the leg pose system (see _WALK_LEGS / _STANDING_LEGS).
    return p


def _build_body_up():
    """Facing up (away from camera). No eyes."""
    p = []

    # --- Head (smooth oval, back view) ---
    # Back of head: mostly base skin with subtle shade on lower portion
    # (hair covers top, so less skin visible; nape of neck is shadowed)
    p += _row(4, 12, 19, "skin", "outline_light", "outline_light")   #  8px
    p += _row(5, 10, 21, "skin", "outline_light", "outline_light")   # 12px
    p += _row(6, 9, 22, "skin", "outline_light", "outline_light")    # 14px
    p += _row(7, 8, 23, "skin")          # 16px
    for y in range(8, 13):
        p += _row(y, 7, 24, "skin")      # 18px
    p += _row(13, 8, 23, "skin")         # 16px
    p += _row(14, 9, 22, "skin_shade")   # 14px (nape shadow)
    p += _row(15, 10, 21, "skin_shade")  # 12px (nape shadow)

    # Chin AA (back view)
    p.append((8, 14, "skin_aa"))
    p.append((23, 14, "skin_aa"))
    p.append((9, 15, "skin_aa"))
    p.append((22, 15, "skin_aa"))

    # --- Torso (back, smooth taper) ---
    p += _row(16, 12, 19, "shirt_shade")       #  8px neck
    p += _row(17, 11, 20, "shirt_shade")       # 10px widening
    p += _row(18, 9, 22, "shirt_shade", "outline_light", "outline_light")  # 14px shoulders
    p += _row(19, 9, 22, "shirt_shade", "outline_light", "outline_light")  # 14px shoulders
    p += _row(20, 10, 21, "shirt_shade")  # 12px
    p += _row(21, 10, 21, "shirt_shade")  # 12px
    p += _row(22, 11, 20, "belt")         # 10px belt
    p += _row(23, 11, 20, "pants")        # 10px waist (matches pants)
    p += _row(24, 11, 20, "pants")        # 10px hips (matches pants)

    # Legs are drawn by the leg pose system.
    return p


def _build_body_left():
    """Facing left — side profile."""
    p = []

    # --- Head (smooth oval, side view — shifted slightly left) ---
    # Light from top-left: left (front) face is lit, shade only on chin
    p += _row(4, 11, 18, "skin", "outline_light", "outline_light")    #  8px - tiny cap
    p += _row(5, 9, 20, "skin", "outline_light", "outline_light")     # 12px
    p += _row(6, 8, 21, "skin", "outline_light", "outline_light")     # 14px
    p += _row(7, 7, 22, "skin")           # 16px
    for y in range(8, 13):
        p += _row(y, 6, 23, "skin")       # 18px
    p += _row(13, 7, 22, "skin")          # 16px - still base skin
    p += _row(14, 8, 21, "skin_shade")    # 14px - chin shadow
    p += _row(15, 9, 20, "skin_shade")    # 12px - chin bottom

    # Right-edge shade (back of head from side view)
    for y in range(10, 13):
        p.append((23, y, "skin_shade"))

    # Chin AA pixels (smooth stair-step transitions)
    p.append((7, 14, "skin_aa"))    # left inner corner (16→14)
    p.append((22, 14, "skin_aa"))   # right inner corner
    p.append((8, 15, "skin_aa"))    # left inner corner (14→12)
    p.append((21, 15, "skin_aa"))   # right inner corner

    # Forehead highlight (left-biased for side view)
    for x in range(9, 16):
        p.append((x, 8, "skin_highlight"))

    # One eye visible (left side) — 2x2 with catchlight, placed toward front of face
    p.append((9, 10, "eye"))              # dark upper-left
    p.append((10, 10, "eye_highlight"))   # catchlight upper-right
    p.append((9, 11, "eye"))              # dark lower-left
    p.append((10, 11, "eye_white"))       # sclera lower-right

    # --- Torso (side, smooth taper) ---
    p += _row(16, 11, 18, "shirt_shade")  #  8px neck (head shadow)
    p += _row(17, 10, 19, "shirt_highlight", "outline_light", "outline_light")  # 10px
    p += _row(18, 8, 21, "shirt", "outline_light", "outline_light")   # 14px shoulder flare
    p += _row(19, 8, 21, "shirt", "outline_light", "outline_light")   # 14px shoulders
    p += _row(20, 9, 20, "shirt")         # 12px
    p += _row(21, 9, 20, "shirt")         # 12px
    p += _row(22, 10, 19, "belt")         # 10px belt
    p += _row(23, 10, 19, "pants")        # 10px waist (matches pants)
    p += _row(24, 10, 19, "pants")        # 10px hips (matches pants)

    # Torso AA: shoulder flare and under-arm transitions
    p.append((9, 18, "shirt_aa"))   # left shoulder inner corner
    p.append((20, 18, "shirt_aa"))  # right shoulder inner corner
    p.append((8, 20, "shirt_aa"))   # left under-arm inner corner
    p.append((21, 20, "shirt_aa"))  # right under-arm inner corner

    # Legs are drawn by the leg pose system.
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
# LEG POSE SYSTEM
#
# Legs are separate from body templates so they can change shape per frame.
# Walk animation uses stride-specific leg poses with spread and rotation.
# Other animations use standing legs with simple Y offsets.
#
# Down/Up: two separate legs (left x=11-14, right x=17-20) with 2px gap for readability.
# Left/Right: legs overlap from side; stride shows clear forward/back separation.
# ---------------------------------------------------------------------------

def _build_standing_legs_down():
    """Front-view standing legs with thigh-to-calf taper and 2px gap."""
    # Each leg: 5px wide at thigh (y=25), 4px at mid (y=26-27), shoe 4px
    # Left leg: x=11-15(thigh), x=11-14(calf), x=11-14(shoe)
    # Right leg: x=16-20(thigh), x=17-20(calf), x=17-20(shoe)
    return (
        # Thigh (wider, slight overlap at gap — creates hip shape)
        _row(25, 11, 15, "pants") + _row(25, 16, 20, "pants") +
        # Upper leg
        _row(26, 11, 14, "pants") + _row(26, 17, 20, "pants") +
        # Knee area (shaded)
        _row(27, 11, 14, "pants_shade") + _row(27, 17, 20, "pants_shade") +
        # Calf/ankle (slightly narrower)
        _row(28, 11, 14, "shoes") + _row(28, 17, 20, "shoes") +
        _row(29, 11, 14, "shoes_shade") + _row(29, 17, 20, "shoes_shade")
    )


def _build_standing_legs_up():
    """Back-view standing legs (all shaded) with thigh-to-calf taper."""
    return (
        _row(25, 11, 15, "pants_shade") + _row(25, 16, 20, "pants_shade") +
        _row(26, 11, 14, "pants_shade") + _row(26, 17, 20, "pants_shade") +
        _row(27, 11, 14, "pants_shade") + _row(27, 17, 20, "pants_shade") +
        _row(28, 11, 14, "shoes_shade") + _row(28, 17, 20, "shoes_shade") +
        _row(29, 11, 14, "shoes_shade") + _row(29, 17, 20, "shoes_shade")
    )


def _build_standing_legs_left():
    """Side-view standing legs — two legs overlapping, shaped thigh-to-calf."""
    # Thigh: 8px wide (torso width), tapers to 6px calf, 6px shoe
    return (
        _row(25, 11, 18, "pants") +       # 8px thigh (matches hips)
        _row(26, 11, 17, "pants") +        # 7px upper leg
        _row(27, 12, 17, "pants_shade") +  # 6px knee (narrowing)
        _row(28, 12, 17, "shoes") +        # 6px calf/ankle
        _row(29, 11, 17, "shoes_shade")    # 7px shoe (wider sole)
    )


_STANDING_LEGS = {
    "down": _build_standing_legs_down(),
    "up": _build_standing_legs_up(),
    "left": _build_standing_legs_left(),
    "right": [(FRAME_W - 1 - x, y, c) for x, y, c in _build_standing_legs_left()],
}

# --- Walk stride poses (per-frame, absolute pixel positions) ---
#
# Side-view walk cycle: 4 distinct poses for natural movement.
# Each individual leg is ~4px wide with thigh→calf taper.
# The walk reads as: contact → passing → stride → passing
#
# F0: Contact — right leg forward, left leg back (slight split)
# F1: Passing — legs overlap, right leg swinging past left
# F2: Contact — left leg forward, right leg back (mirror of F0)
# F3: Passing — legs overlap, left leg swinging past right

# DOWN/UP WALK: use standing legs + ANIM_OFFSETS per-leg Y-shifts
_walk_down_stand = _STANDING_LEGS["down"]
_walk_up_stand = _STANDING_LEGS["up"]

# LEFT-FACING WALK: 4 distinct poses for smooth animation
# Center of legs area ≈ x=14.5, torso hips at x=10-19

# F0: Contact — legs slightly apart, front foot forward, back foot behind
_walk_left_f0 = (
    # Hip connection (solid)
    _row(25, 11, 18, "pants") +
    # Front leg (left/forward): x=9-13
    _row(26, 9, 13, "pants") +
    _row(27, 9, 12, "pants_shade") +
    _row(28, 9, 12, "shoes") +
    _row(29, 8, 12, "shoes_shade") +
    # Back leg (right/behind): x=14-18
    _row(26, 14, 18, "pants") +
    _row(27, 15, 18, "pants_shade") +
    _row(28, 16, 18, "shoes") +
    _row(29, 16, 19, "shoes_shade")
)

# F1: Passing — legs overlap in center, one lifting
_walk_left_f1 = (
    _row(25, 11, 18, "pants") +
    _row(26, 11, 17, "pants") +
    _row(27, 12, 17, "pants_shade") +
    _row(28, 12, 17, "shoes") +
    _row(29, 11, 17, "shoes_shade")
)

# F2: Contact — mirror stride (other leg forward)
_walk_left_f2 = (
    # Hip connection
    _row(25, 11, 18, "pants") +
    # Back leg (left/behind): x=14-18
    _row(26, 14, 18, "pants") +
    _row(27, 15, 18, "pants_shade") +
    _row(28, 16, 18, "shoes") +
    _row(29, 16, 19, "shoes_shade") +
    # Front leg (right/forward): x=9-13
    _row(26, 9, 13, "pants") +
    _row(27, 9, 12, "pants_shade") +
    _row(28, 9, 12, "shoes") +
    _row(29, 8, 12, "shoes_shade")
)

# F3: Passing — legs overlap again (other direction)
_walk_left_f3 = (
    _row(25, 11, 18, "pants") +
    _row(26, 11, 17, "pants") +
    _row(27, 12, 17, "pants_shade") +
    _row(28, 12, 17, "shoes") +
    _row(29, 11, 17, "shoes_shade")
)

# RIGHT-FACING WALK: mirror of left
def _mirror_legs(poses):
    return [[(FRAME_W - 1 - x, y, c) for x, y, c in pose] for pose in poses]

_WALK_LEGS = {
    "down":  None,  # uses standing legs + ANIM_OFFSETS
    "up":    None,   # uses standing legs + ANIM_OFFSETS
    "left":  [_walk_left_f0,  _walk_left_f1,  _walk_left_f2,  _walk_left_f3],
    "right": _mirror_legs([_walk_left_f0, _walk_left_f1, _walk_left_f2, _walk_left_f3]),
}

# Y offsets for standing legs in non-walk animations (applied uniformly)
_LEG_Y_OFFSETS = {
    "jump":     [1, 0, -2, 1],
    "crouch":   [0, 0, 1, 0],
    "interact": [0, 0, 0, 0],
}


# ---------------------------------------------------------------------------
# ANIMATION REGIONS
# ---------------------------------------------------------------------------

def _region_for_pixel(x, y, direction):
    """Classify pixel into animation region."""
    if y <= 15:
        return "head"
    if y <= 24:
        return "body"
    # Legs
    if direction in ("down", "up"):
        if x <= 15:
            return "leg_l"
        return "leg_r"
    else:
        return "leg_l" if y <= 27 else "leg_r"


# ---------------------------------------------------------------------------
# SHOULDER-PIVOT ARM SYSTEM
#
# Arms are skin-colored appendages (3px wide, 6px long) that rotate from
# shoulder pivot points. Drawn outside the body silhouette.
# ---------------------------------------------------------------------------

# Shoulder pivot positions per direction (left_shoulder, right_shoulder)
# Side views: front arm pivots from torso center for proper side profile.
# Left-facing:  left arm = front (center x=14), right arm = back (edge x=20)
# Right-facing: right arm = front (center x=17), left arm = back (edge x=11)
_SHOULDERS = {
    "down":  ((9, 18), (22, 18)),      # widened for shoulder flare
    "up":    ((9, 18), (22, 18)),
    "left":  ((16, 18), (21, 18)),     # back arm at wider shoulder edge
    "right": ((10, 18), (15, 18)),     # back arm at wider shoulder edge
}

# Arm pose definitions: pixel offsets from shoulder pivot.
# Each pose = list of (dx, dy, color_key) tuples.
# 3px wide: inner=skin, middle=skin, outer=outline.
# We store for LEFT arm; right arm mirrors dx.

_ARM_POSE_LEFT = {
    "rest":       [],
    "hang":       [
        (-1, 0, "skin"), (-2, 0, "skin"), (-3, 0, "outline"),
        (-1, 1, "skin"), (-2, 1, "skin"), (-3, 1, "outline"),
        (-1, 2, "skin"), (-2, 2, "skin"), (-3, 2, "outline"),
        (-1, 3, "skin"), (-2, 3, "skin"), (-3, 3, "outline"),
        (-1, 4, "skin_shade"), (-2, 4, "skin_shade"), (-3, 4, "outline"),
        (-1, 5, "skin_shade"), (-2, 5, "skin_shade"), (-3, 5, "outline"),
    ],
    "swing_fwd":  [
        (-1, -1, "skin"), (-2, -1, "skin"), (-3, -1, "outline"),
        (-1, 0, "skin"), (-2, 0, "skin"), (-3, 0, "outline"),
        (-1, 1, "skin"), (-2, 1, "skin"), (-3, 1, "outline"),
        (-1, 2, "skin_shade"), (-2, 2, "skin_shade"), (-3, 2, "outline"),
        (-1, 3, "skin_shade"), (-2, 3, "skin_shade"), (-3, 3, "outline"),
    ],
    "swing_back": [
        (-1, 1, "skin"), (-2, 1, "skin"), (-3, 1, "outline"),
        (-1, 2, "skin"), (-2, 2, "skin"), (-3, 2, "outline"),
        (-1, 3, "skin"), (-2, 3, "skin"), (-3, 3, "outline"),
        (-1, 4, "skin"), (-2, 4, "skin"), (-3, 4, "outline"),
        (-1, 5, "skin_shade"), (-2, 5, "skin_shade"), (-3, 5, "outline"),
        (-1, 6, "skin_shade"), (-2, 6, "skin_shade"), (-3, 6, "outline"),
    ],
    "raised":     [
        (-1, 0, "skin"), (-2, 0, "skin"), (-3, 0, "outline"),
        (-2, -1, "skin"), (-3, -1, "skin"), (-4, -1, "outline"),
        (-3, -2, "skin"), (-4, -2, "skin"), (-5, -2, "outline"),
        (-4, -3, "skin"), (-5, -3, "skin"), (-6, -3, "outline"),
    ],
    "reach_up":   [
        (-1, 0, "skin"), (-2, 0, "skin"), (-3, 0, "outline"),
        (-2, -1, "skin"), (-3, -1, "skin"), (-4, -1, "outline"),
        (-3, -2, "skin"), (-4, -2, "skin"), (-5, -2, "outline"),
        (-3, -3, "skin"), (-4, -3, "skin"), (-5, -3, "outline"),
    ],
    # Side views — 3px wide
    "side_hang":  [
        (-1, 0, "skin"), (-2, 0, "skin"), (-3, 0, "outline"),
        (-1, 1, "skin"), (-2, 1, "skin"), (-3, 1, "outline"),
        (-1, 2, "skin"), (-2, 2, "skin"), (-3, 2, "outline"),
        (-1, 3, "skin"), (-2, 3, "skin"), (-3, 3, "outline"),
        (-1, 4, "skin_shade"), (-2, 4, "skin_shade"), (-3, 4, "outline"),
        (-1, 5, "skin_shade"), (-2, 5, "skin_shade"), (-3, 5, "outline"),
    ],
    "side_fwd":   [
        (-1, -1, "skin"), (-2, -1, "skin"), (-3, -1, "outline"),
        (-1, 0, "skin"), (-2, 0, "skin"), (-3, 0, "outline"),
        (-1, 1, "skin"), (-2, 1, "skin"), (-3, 1, "outline"),
        (-1, 2, "skin_shade"), (-2, 2, "skin_shade"), (-3, 2, "outline"),
    ],
    "side_back":  [
        (-1, 1, "skin"), (-2, 1, "skin"), (-3, 1, "outline"),
        (-1, 2, "skin"), (-2, 2, "skin"), (-3, 2, "outline"),
        (-1, 3, "skin"), (-2, 3, "skin"), (-3, 3, "outline"),
        (-1, 4, "skin_shade"), (-2, 4, "skin_shade"), (-3, 4, "outline"),
        (-1, 5, "skin_shade"), (-2, 5, "skin_shade"), (-3, 5, "outline"),
    ],
    "side_raise": [
        (-1, 0, "skin"), (-2, 0, "skin"), (-3, 0, "outline"),
        (-2, -1, "skin"), (-3, -1, "skin"), (-4, -1, "outline"),
        (-3, -2, "skin"), (-4, -2, "skin"), (-5, -2, "outline"),
        (-4, -3, "skin"), (-5, -3, "skin"), (-6, -3, "outline"),
    ],
    # Interact poses — arm rotates forward from side
    "side_interact_45": [
        # -45° from vertical: diagonal, each segment shifts 1px forward
        (-1, 0, "skin"), (-2, 0, "skin"), (-3, 0, "outline"),
        (-2, 1, "skin"), (-3, 1, "skin"), (-4, 1, "outline"),
        (-3, 2, "skin"), (-4, 2, "skin"), (-5, 2, "outline"),
        (-4, 3, "skin"), (-5, 3, "skin"), (-6, 3, "outline"),
        (-5, 4, "skin_shade"), (-6, 4, "skin_shade"), (-7, 4, "outline"),
    ],
    "side_interact_90": [
        # -90° from vertical: horizontal, arm points forward
        # Width (3px) now in dy, length in dx
        (-1, -1, "outline"), (-1, 0, "skin"), (-1, 1, "skin"),
        (-2, -1, "outline"), (-2, 0, "skin"), (-2, 1, "skin"),
        (-3, -1, "outline"), (-3, 0, "skin"), (-3, 1, "skin"),
        (-4, -1, "outline"), (-4, 0, "skin"), (-4, 1, "skin"),
        (-5, -1, "outline"), (-5, 0, "skin_shade"), (-5, 1, "skin_shade"),
        (-6, -1, "outline"), (-6, 0, "skin_shade"), (-6, 1, "skin_shade"),
    ],
}


def _mirror_arm_pose(pose):
    """Mirror a left-arm pose for the right arm (flip dx)."""
    return [(-dx, dy, c) for dx, dy, c in pose]


def _get_arm_pixels(direction, animation, frame_idx):
    """Return arm overlay pixels as list of (x, y, color_key)."""
    l_sh, r_sh = _SHOULDERS[direction]

    l_pose_name, r_pose_name = _ARM_ANIM_POSES[animation][direction][frame_idx]

    l_offsets = _ARM_POSE_LEFT.get(l_pose_name, [])
    r_offsets = _mirror_arm_pose(_ARM_POSE_LEFT.get(r_pose_name, []))

    pixels = []
    for dx, dy, color_key in l_offsets:
        ax, ay = l_sh[0] + dx, l_sh[1] + dy
        if 0 <= ax < FRAME_W and 0 <= ay < FRAME_H:
            pixels.append((ax, ay, color_key))

    for dx, dy, color_key in r_offsets:
        ax, ay = r_sh[0] + dx, r_sh[1] + dy
        if 0 <= ax < FRAME_W and 0 <= ay < FRAME_H:
            pixels.append((ax, ay, color_key))

    return pixels


# Arm pose schedule per animation.
_ARM_ANIM_POSES = {
    "walk": {
        "down": [
            ("hang",      "hang"),
            ("swing_fwd", "swing_back"),
            ("hang",      "hang"),
            ("swing_back", "swing_fwd"),
        ],
        "up": [
            ("hang",      "hang"),
            ("swing_fwd", "swing_back"),
            ("hang",      "hang"),
            ("swing_back", "swing_fwd"),
        ],
        "left": [
            ("side_hang", "rest"),
            ("side_fwd",  "rest"),
            ("side_hang", "rest"),
            ("side_back", "rest"),
        ],
        "right": [
            ("rest", "side_hang"),
            ("rest", "side_fwd"),
            ("rest", "side_hang"),
            ("rest", "side_back"),
        ],
    },
    "jump": {
        "down": [
            ("hang",   "hang"),
            ("swing_fwd", "swing_fwd"),
            ("raised", "raised"),
            ("swing_fwd", "swing_fwd"),
        ],
        "up": [
            ("hang",   "hang"),
            ("swing_fwd", "swing_fwd"),
            ("raised", "raised"),
            ("swing_fwd", "swing_fwd"),
        ],
        "left": [
            ("side_hang",  "rest"),
            ("side_fwd",   "rest"),
            ("side_raise", "rest"),
            ("side_fwd",   "rest"),
        ],
        "right": [
            ("rest", "side_hang"),
            ("rest", "side_fwd"),
            ("rest", "side_raise"),
            ("rest", "side_fwd"),
        ],
    },
    "crouch": {
        "down": [
            ("hang",       "hang"),
            ("swing_back", "swing_back"),
            ("swing_back", "swing_back"),
            ("swing_back", "swing_back"),
        ],
        "up": [
            ("hang",       "hang"),
            ("swing_back", "swing_back"),
            ("swing_back", "swing_back"),
            ("swing_back", "swing_back"),
        ],
        "left": [
            ("side_hang", "rest"),
            ("side_back", "rest"),
            ("side_back", "rest"),
            ("side_back", "rest"),
        ],
        "right": [
            ("rest", "side_hang"),
            ("rest", "side_back"),
            ("rest", "side_back"),
            ("rest", "side_back"),
        ],
    },
    "interact": {
        "down": [
            ("hang", "hang"),
            ("hang", "swing_fwd"),
            ("hang", "raised"),
            ("hang", "swing_fwd"),
        ],
        "up": [
            ("hang", "hang"),
            ("hang", "swing_fwd"),
            ("hang", "raised"),
            ("hang", "swing_fwd"),
        ],
        "left": [
            ("side_hang",          "rest"),
            ("side_interact_45",   "rest"),
            ("side_interact_90",   "rest"),
            ("side_hang",          "rest"),
        ],
        "right": [
            ("rest", "side_hang"),
            ("rest", "side_interact_45"),
            ("rest", "side_interact_90"),
            ("rest", "side_hang"),
        ],
    },
}


# ---------------------------------------------------------------------------
# ANIMATION OFFSETS (body region movement) — scaled for 32x32
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
            "head":  [(0, 1),  (0, -1), (0, -3), (0, 0)],
            "body":  [(0, 1),  (0, -1), (0, -3), (0, 0)],
            "leg_l": [(0, 1),  (0, 0),  (0, -2), (0, 1)],
            "leg_r": [(0, 1),  (0, 0),  (0, -2), (0, 1)],
        },
        "up": {
            "head":  [(0, 1),  (0, -1), (0, -3), (0, 0)],
            "body":  [(0, 1),  (0, -1), (0, -3), (0, 0)],
            "leg_l": [(0, 1),  (0, 0),  (0, -2), (0, 1)],
            "leg_r": [(0, 1),  (0, 0),  (0, -2), (0, 1)],
        },
        "left": {
            "head":  [(0, 1),  (0, -1), (0, -3), (0, 0)],
            "body":  [(0, 1),  (0, -1), (0, -3), (0, 0)],
            "leg_l": [(0, 1),  (0, 0),  (0, -2), (0, 1)],
            "leg_r": [(0, 1),  (0, 0),  (0, -2), (0, 1)],
        },
        "right": {
            "head":  [(0, 1),  (0, -1), (0, -3), (0, 0)],
            "body":  [(0, 1),  (0, -1), (0, -3), (0, 0)],
            "leg_l": [(0, 1),  (0, 0),  (0, -2), (0, 1)],
            "leg_r": [(0, 1),  (0, 0),  (0, -2), (0, 1)],
        },
    },
    "crouch": {
        "down": {
            "head":  [(0, 0), (0, 2),  (0, 3),  (0, 2)],
            "body":  [(0, 0), (0, 1),  (0, 2),  (0, 1)],
            "leg_l": [(0, 0), (0, 0),  (0, 1),  (0, 0)],
            "leg_r": [(0, 0), (0, 0),  (0, 1),  (0, 0)],
        },
        "up": {
            "head":  [(0, 0), (0, 2),  (0, 3),  (0, 2)],
            "body":  [(0, 0), (0, 1),  (0, 2),  (0, 1)],
            "leg_l": [(0, 0), (0, 0),  (0, 1),  (0, 0)],
            "leg_r": [(0, 0), (0, 0),  (0, 1),  (0, 0)],
        },
        "left": {
            "head":  [(0, 0), (0, 2),  (0, 3),  (0, 2)],
            "body":  [(0, 0), (0, 1),  (0, 2),  (0, 1)],
            "leg_l": [(0, 0), (0, 0),  (0, 1),  (0, 0)],
            "leg_r": [(0, 0), (0, 0),  (0, 1),  (0, 0)],
        },
        "right": {
            "head":  [(0, 0), (0, 2),  (0, 3),  (0, 2)],
            "body":  [(0, 0), (0, 1),  (0, 2),  (0, 1)],
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
    """Render a single 32x32 frame."""
    img = Image.new("RGBA", (FRAME_W, FRAME_H), (0, 0, 0, 0))

    body_pixels = BODY_TEMPLATES[direction]
    offsets = ANIM_OFFSETS[animation][direction]

    # 1. Draw body template pixels (head + torso, no legs)
    for bx, by, color_key in body_pixels:
        region = _region_for_pixel(bx, by, direction)
        dx, dy = offsets[region][frame_idx]
        px, py = bx + dx, by + dy
        if 0 <= px < FRAME_W and 0 <= py < FRAME_H:
            img.putpixel((px, py), palette[color_key])

    # 2. Draw legs
    walk_leg_poses = _WALK_LEGS.get(direction) if animation == "walk" else None
    if walk_leg_poses is not None:
        # Side-view walk: use per-frame stride poses (rotated leg columns)
        for lx, ly, color_key in walk_leg_poses[frame_idx]:
            if 0 <= lx < FRAME_W and 0 <= ly < FRAME_H:
                img.putpixel((lx, ly), palette[color_key])
    elif animation == "walk":
        # Down/Up walk: standing legs with original per-leg Y offsets
        for lx, ly, color_key in _STANDING_LEGS[direction]:
            region = _region_for_pixel(lx, ly, direction)
            dx, dy = offsets[region][frame_idx]
            px, py = lx + dx, ly + dy
            if 0 <= px < FRAME_W and 0 <= py < FRAME_H:
                img.putpixel((px, py), palette[color_key])
    else:
        # Non-walk animations: standing legs with uniform Y offset
        leg_dy = _LEG_Y_OFFSETS[animation][frame_idx]
        for lx, ly, color_key in _STANDING_LEGS[direction]:
            py = ly + leg_dy
            if 0 <= lx < FRAME_W and 0 <= py < FRAME_H:
                img.putpixel((lx, py), palette[color_key])

    # 3. Draw arm overlay (shoulder-pivot rotation)
    body_dx, body_dy = offsets["body"][frame_idx]
    arm_pixels = _get_arm_pixels(direction, animation, frame_idx)
    for ax, ay, color_key in arm_pixels:
        px, py = ax + body_dx, ay + body_dy
        if 0 <= px < FRAME_W and 0 <= py < FRAME_H:
            img.putpixel((px, py), palette[color_key])

    # 4. Draw hair (moves with head)
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
    # Derive enhanced palette with catchlights, highlights, belt, sel-out colors
    palette = _derive_palette(palette)
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
            "version": "9.0",
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
<p class="info">v9 — 32x32 enhanced face + torso ({TILE_SIZE}px grid, {scale}x render)</p>

<canvas id="anim" width="{FRAME_W * 6}" height="{FRAME_H * 6}"></canvas>

<div class="controls" id="animBtns">
  <label>Anim:</label>
</div>
<div class="controls" id="dirBtns">
  <label>Dir:</label>
</div>

<p class="info">Full spritesheet (3x zoom):</p>
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
  document.getElementById("sheetImg").style.width = (img.width * 3) + "px";
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
    parser = argparse.ArgumentParser(description="Generate a 32x32 chibi character spritesheet.")
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
        print(f"Frame size:   {FRAME_W}x{FRAME_H}px ({TILE_SIZE}px grid)")
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
    print(f"  Frames:      {total} | Frame: {FRAME_W}x{FRAME_H}px\n")


if __name__ == "__main__":
    main()
