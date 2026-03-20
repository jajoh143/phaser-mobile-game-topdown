#!/usr/bin/env python3
"""
Glass alcohol bottle spritesheet generator for Phaser 3.

Generates a 128x32 PNG with 4 bottle sprites side-by-side (each 32x32).
Top-down RPG perspective: bottles are sitting on the bar, viewed from slightly
above — we see the bottle cap/cork at top, an oval-ish body with liquid color
showing through semi-transparent glass, and shading to suggest the round form.

Bottle lineup (left to right, x offsets 0/32/64/96):
  0 – Whiskey : square/angular amber bottle, cork top, cream label stripe
  1 – Wine    : tall narrow dark bottle, long neck, cork, gold foil capsule
  2 – Gin     : shorter wide bottle, pale blue-green tinted glass, metal cap
  3 – Beer    : classic dark brown beer bottle, crown cap, amber liquid

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
SHEET_W = BOTTLE_W * NUM_BOTTLES   # 128
SHEET_H = BOTTLE_H                 # 32

# ---------------------------------------------------------------------------
# BOTTLE NAMES (used by atlas)
# ---------------------------------------------------------------------------
BOTTLE_NAMES = ["whiskey", "wine", "gin", "beer"]


# ---------------------------------------------------------------------------
# PIXEL HELPERS  (operate on pixel tuples list, like other generators)
# ---------------------------------------------------------------------------

def _row(pixels, y, x0, x1, color):
    """Fill an inclusive horizontal span."""
    for x in range(x0, x1 + 1):
        pixels.append((x, y, color))


def _col(pixels, x, y0, y1, color):
    """Fill an inclusive vertical span."""
    for y in range(y0, y1 + 1):
        pixels.append((x, y, color))


def _rect(pixels, x0, y0, x1, y1, color):
    """Fill an inclusive solid rectangle."""
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            pixels.append((x, y, color))


# ---------------------------------------------------------------------------
# BOTTLE PIXEL DEFINITIONS
#
# Top-down perspective notes:
#   - We look slightly downward at the bottle.
#   - The neck/cap is at the top of the sprite (y=0 = farthest/back of cap).
#   - The body is the oval below, widening then rounding off.
#   - Left edge of body gets a glass shine highlight (light source upper-left).
#   - Right edge and bottom are shadowed.
#   - Liquid color shows through the glass as the dominant body fill.
#   - Cork/cap appears as a small circle or square at the very top center.
#
# All x coords are LOCAL (0-31) and will be offset by the bottle's ox when
# composited onto the spritesheet.
# ---------------------------------------------------------------------------

def _whiskey_pixels():
    """
    Whiskey bottle: square/angular silhouette (not round), amber glass.
    Top-down: slightly square body oval, square-ish cork/stopper.
    Cream label band in the middle third.
    """
    p = []

    # Palette
    OUTLINE    = (25,  12,   4, 255)
    GLASS_BODY = (140,  65,  15, 255)   # amber glass (base)
    GLASS_DARK = (95,   40,   8, 255)   # shadow side of glass
    GLASS_HL   = (195, 115,  40, 255)   # glass highlight
    LIQUID     = (185, 100,  22, 200)   # amber liquid (semi-opaque)
    LIQUID_HL  = (218, 145,  55, 180)   # liquid highlight
    LABEL_BG   = (228, 210, 168, 255)   # cream label
    LABEL_LINE = (95,   50,  18, 255)   # dark label text lines
    CORK       = (182, 150,  92, 255)   # cork top face
    CORK_SH    = (138, 108,  60, 255)   # cork shadow/edge
    SHINE      = (255, 228, 165, 210)   # glass shine dot

    # --- Body: squarish oval, 18px wide x 22px tall, centered (x=7-24, y=7-28) ---
    # We represent the angular shape by filling a slightly-rounded rectangle.
    bx0, bx1 = 7, 24
    by0, by1 = 7, 28

    # Fill liquid (interior)
    _rect(p, bx0 + 1, by0 + 1, bx1 - 1, by1 - 1, LIQUID)

    # Liquid highlight: top-left interior
    for y in range(by0 + 1, by0 + 6):
        for x in range(bx0 + 1, bx0 + 4):
            p.append((x, y, LIQUID_HL))

    # Glass shell overlay (4 thin walls)
    _row(p, by0, bx0, bx1, GLASS_BODY)          # top glass edge
    _row(p, by1, bx0, bx1, GLASS_DARK)          # bottom glass (shadow)
    _col(p, bx0, by0 + 1, by1 - 1, GLASS_HL)   # left wall (lit)
    _col(p, bx1, by0 + 1, by1 - 1, GLASS_DARK) # right wall (shadow)
    # Second shadow column
    _col(p, bx1 - 1, by0 + 2, by1 - 1, GLASS_DARK)
    # Second highlight column
    _col(p, bx0 + 1, by0 + 2, by1 - 2, GLASS_HL)

    # Glass shine dot (upper-left)
    p.append((bx0 + 2, by0 + 2, SHINE))
    p.append((bx0 + 2, by0 + 3, SHINE))
    p.append((bx0 + 3, by0 + 2, SHINE))

    # Body outline
    _row(p, by0 - 1, bx0, bx1, OUTLINE)         # outline above top wall
    _row(p, by1 + 1, bx0, bx1, OUTLINE)         # outline below bottom wall
    _col(p, bx0 - 1, by0, by1, OUTLINE)         # left outline
    _col(p, bx1 + 1, by0, by1, OUTLINE)         # right outline
    # Corner outlines (rounded corners feel)
    p.append((bx0 - 1, by0 - 1, OUTLINE))
    p.append((bx1 + 1, by0 - 1, OUTLINE))
    p.append((bx0 - 1, by1 + 1, OUTLINE))
    p.append((bx1 + 1, by1 + 1, OUTLINE))

    # --- Label band (rows 13-20, inset 2px from body sides) ---
    _rect(p, bx0 + 2, 13, bx1 - 2, 20, LABEL_BG)
    # Label lines (decorative text impression)
    _row(p, 15, bx0 + 3, bx1 - 3, LABEL_LINE)
    _row(p, 17, bx0 + 3, bx1 - 3, LABEL_LINE)
    _row(p, 19, bx0 + 3, bx1 - 3, LABEL_LINE)

    # --- Shoulder taper at top (rows 4-6): body narrows to neck ---
    for dy, width_shrink in [(6, 0), (5, 1), (4, 2)]:
        x0s = bx0 + width_shrink
        x1s = bx1 - width_shrink
        _row(p, dy, x0s, x1s, GLASS_BODY)
        p.append((x0s, dy, GLASS_HL))
        p.append((x1s, dy, GLASS_DARK))
        p.append((x0s - 1, dy, OUTLINE))
        p.append((x1s + 1, dy, OUTLINE))

    # --- Cork (square stopper): centered at top, rows 0-3 ---
    # Cork is 6px wide, 4px tall, centered at x=13-18
    cx0, cx1 = 13, 18
    _rect(p, cx0, 1, cx1, 3, CORK)
    _row(p, 1, cx0, cx1, CORK)       # top face of cork
    _row(p, 0, cx0, cx1, CORK_SH)    # very top edge (shadow rim)
    _col(p, cx0, 0, 3, CORK_SH)      # left shadow
    _col(p, cx1, 0, 3, CORK_SH)      # right shadow
    # Cork highlight (top-left)
    p.append((cx0 + 1, 1, CORK))
    p.append((cx0 + 1, 2, CORK))
    # Cork outline
    _row(p, 0, cx0 - 1, cx1 + 1, OUTLINE)
    p.append((cx0 - 1, 1, OUTLINE))
    p.append((cx0 - 1, 2, OUTLINE))
    p.append((cx0 - 1, 3, OUTLINE))
    p.append((cx1 + 1, 1, OUTLINE))
    p.append((cx1 + 1, 2, OUTLINE))
    p.append((cx1 + 1, 3, OUTLINE))
    _row(p, 4, cx0 - 1, cx1 + 1, OUTLINE)

    return p


def _wine_pixels():
    """
    Wine bottle: narrow dark bottle, long neck, cork, gold foil capsule.
    Top-down: slim oval body, distinctive burgundy/dark-purple color.
    """
    p = []

    # Palette
    OUTLINE    = (12,   8,  18, 255)
    GLASS_BODY = (40,   18,  52, 255)  # deep dark purple-black glass
    GLASS_DARK = (22,    8,  28, 255)  # glass shadow
    GLASS_HL   = (72,   38,  90, 255)  # glass highlight (purple-tinted)
    LIQUID     = (115,  18,  38, 200)  # deep burgundy wine
    LIQUID_HL  = (155,  38,  55, 180)  # wine highlight
    FOIL       = (172, 155,  22, 255)  # gold foil capsule
    FOIL_HL    = (215, 198,  55, 255)  # foil highlight
    FOIL_SH    = (120, 108,  14, 255)  # foil shadow
    CORK       = (192, 158,  88, 255)  # cork (natural wood tone)
    CORK_SH    = (145, 112,  55, 255)  # cork shadow
    SHINE      = (148, 115, 185, 215)  # purple glass shine

    # --- Body: slim oval, 14px wide x 18px tall, rows 12-29, x=9-22 ---
    bx0, bx1 = 9, 22
    by0, by1 = 12, 29

    # Liquid fill
    _rect(p, bx0 + 1, by0 + 1, bx1 - 1, by1 - 1, LIQUID)

    # Liquid highlights
    for y in range(by0 + 1, by0 + 4):
        p.append((bx0 + 1, y, LIQUID_HL))
        p.append((bx0 + 2, y, LIQUID_HL))

    # Glass walls
    _row(p, by0, bx0, bx1, GLASS_BODY)
    _row(p, by1, bx0, bx1, GLASS_DARK)
    _col(p, bx0, by0 + 1, by1 - 1, GLASS_HL)
    _col(p, bx1, by0 + 1, by1 - 1, GLASS_DARK)
    _col(p, bx1 - 1, by0 + 2, by1 - 1, GLASS_DARK)
    _col(p, bx0 + 1, by0 + 2, by1 - 2, GLASS_HL)

    # Rounded bottom corners
    p.append((bx0, by1, GLASS_DARK))
    p.append((bx1, by1, GLASS_DARK))
    p.append((bx0, by1 - 1, GLASS_DARK))

    # Glass shine
    p.append((bx0 + 2, by0 + 2, SHINE))
    p.append((bx0 + 2, by0 + 3, SHINE))

    # Body outline
    _row(p, by0 - 1, bx0, bx1, OUTLINE)
    _row(p, by1 + 1, bx0, bx1, OUTLINE)
    _col(p, bx0 - 1, by0, by1, OUTLINE)
    _col(p, bx1 + 1, by0, by1, OUTLINE)

    # --- Shoulder taper (rows 8-11): slim body up to narrow neck ---
    shoulder_widths = [(11, 1), (10, 2), (9, 3), (8, 4)]
    for (y, shrink) in shoulder_widths:
        x0s = bx0 + shrink
        x1s = bx1 - shrink
        _row(p, y, x0s, x1s, GLASS_BODY)
        p.append((x0s, y, GLASS_HL))
        p.append((x1s, y, GLASS_DARK))
        p.append((x0s - 1, y, OUTLINE))
        p.append((x1s + 1, y, OUTLINE))
    # Liquid visible in shoulder too
    for (y, shrink) in shoulder_widths:
        x0s = bx0 + shrink + 1
        x1s = bx1 - shrink - 1
        if x0s <= x1s:
            _row(p, y, x0s, x1s, LIQUID)

    # --- Long neck (rows 3-7): very narrow, 6px wide, x=13-18 ---
    nx0, nx1 = 13, 18
    _rect(p, nx0, 3, nx1, 7, GLASS_BODY)
    _col(p, nx0, 3, 7, GLASS_HL)
    _col(p, nx1, 3, 7, GLASS_DARK)
    _row(p, 3, nx0, nx1, OUTLINE)
    _row(p, 7, nx0, nx1, OUTLINE)
    _col(p, nx0 - 1, 3, 7, OUTLINE)
    _col(p, nx1 + 1, 3, 7, OUTLINE)

    # --- Gold foil capsule (rows 4-7 on neck, slightly wider) ---
    fx0, fx1 = nx0 - 1, nx1 + 1
    _rect(p, fx0, 5, fx1, 7, FOIL)
    _row(p, 5, fx0, fx1, FOIL_HL)   # bright top of foil
    _row(p, 7, fx0, fx1, FOIL_SH)   # bottom shadow of foil
    _col(p, fx0, 5, 7, FOIL_SH)
    _col(p, fx1, 5, 7, FOIL_SH)
    # Foil outline
    _row(p, 4, fx0 - 1, fx1 + 1, OUTLINE)
    _row(p, 8, fx0 - 1, fx1 + 1, OUTLINE)
    p.append((fx0 - 1, 5, OUTLINE))
    p.append((fx0 - 1, 6, OUTLINE))
    p.append((fx0 - 1, 7, OUTLINE))
    p.append((fx1 + 1, 5, OUTLINE))
    p.append((fx1 + 1, 6, OUTLINE))
    p.append((fx1 + 1, 7, OUTLINE))

    # --- Cork (top of neck): rows 0-2, 4px wide, x=14-17 ---
    cx0, cx1 = 14, 17
    _rect(p, cx0, 0, cx1, 2, CORK)
    _row(p, 0, cx0, cx1, CORK)
    _col(p, cx0, 0, 2, CORK_SH)
    _col(p, cx1, 0, 2, CORK_SH)
    # Cork outline
    p.append((cx0 - 1, 0, OUTLINE))
    p.append((cx0 - 1, 1, OUTLINE))
    p.append((cx0 - 1, 2, OUTLINE))
    p.append((cx1 + 1, 0, OUTLINE))
    p.append((cx1 + 1, 1, OUTLINE))
    p.append((cx1 + 1, 2, OUTLINE))
    _row(p, 3, cx0 - 1, cx1 + 1, OUTLINE)

    return p


def _gin_pixels():
    """
    Gin bottle: wider, shorter body; pale blue-green tinted glass; metal cap.
    Top-down: wide oval body, very clear/pale liquid visible through glass.
    """
    p = []

    # Palette
    OUTLINE    = (18,  30,  35, 255)
    GLASS_BODY = (130, 188, 190, 210)  # pale teal glass (semi-opaque)
    GLASS_DARK = (72,  120, 125, 210)  # glass shadow
    GLASS_HL   = (200, 235, 238, 225)  # strong glass highlight
    LIQUID     = (165, 218, 210, 175)  # very pale gin/clear spirit
    LIQUID_HL  = (215, 245, 242, 155)  # liquid highlight
    LABEL_BG   = (245, 245, 240, 255)  # white-ish label
    LABEL_LINE = (18,  58,  75, 255)   # dark teal label text
    CAP_BASE   = (172, 172, 172, 255)  # metal cap (silver)
    CAP_HL     = (225, 225, 225, 255)  # cap highlight
    CAP_SH     = (110, 110, 110, 255)  # cap shadow
    CAP_RING   = (90,  90,  90, 255)   # cap thread ring
    SHINE      = (255, 255, 255, 215)  # white shine dot

    # --- Wide body: 20px wide x 20px tall, rows 10-29, x=6-25 ---
    bx0, bx1 = 6, 25
    by0, by1 = 10, 29

    # Liquid fill
    _rect(p, bx0 + 1, by0 + 1, bx1 - 1, by1 - 1, LIQUID)

    # Liquid highlights
    for y in range(by0 + 1, by0 + 5):
        for x in range(bx0 + 1, bx0 + 4):
            p.append((x, y, LIQUID_HL))

    # Glass walls
    _row(p, by0, bx0, bx1, GLASS_BODY)
    _row(p, by1, bx0, bx1, GLASS_DARK)
    _col(p, bx0, by0 + 1, by1 - 1, GLASS_HL)
    _col(p, bx1, by0 + 1, by1 - 1, GLASS_DARK)
    _col(p, bx1 - 1, by0 + 2, by1 - 1, GLASS_DARK)
    _col(p, bx0 + 1, by0 + 2, by1 - 2, GLASS_HL)

    # Glass shine dots
    p.append((bx0 + 2, by0 + 2, SHINE))
    p.append((bx0 + 2, by0 + 3, SHINE))
    p.append((bx0 + 3, by0 + 2, SHINE))

    # Body outline
    _row(p, by0 - 1, bx0, bx1, OUTLINE)
    _row(p, by1 + 1, bx0, bx1, OUTLINE)
    _col(p, bx0 - 1, by0, by1, OUTLINE)
    _col(p, bx1 + 1, by0, by1, OUTLINE)
    p.append((bx0 - 1, by0 - 1, OUTLINE))
    p.append((bx1 + 1, by0 - 1, OUTLINE))

    # --- Label band (rows 16-23, inset) ---
    _rect(p, bx0 + 2, 16, bx1 - 2, 23, LABEL_BG)
    _row(p, 18, bx0 + 3, bx1 - 3, LABEL_LINE)
    _row(p, 20, bx0 + 3, bx1 - 3, LABEL_LINE)
    _row(p, 22, bx0 + 3, bx1 - 3, LABEL_LINE)

    # --- Shoulder taper (rows 6-9): wide body to shorter neck ---
    for dy, shrink in [(9, 1), (8, 2), (7, 4), (6, 5)]:
        x0s = bx0 + shrink
        x1s = bx1 - shrink
        _row(p, dy, x0s, x1s, GLASS_BODY)
        p.append((x0s, dy, GLASS_HL))
        p.append((x1s, dy, GLASS_DARK))
        p.append((x0s - 1, dy, OUTLINE))
        p.append((x1s + 1, dy, OUTLINE))
    # Liquid in shoulder
    for dy, shrink in [(9, 1), (8, 2), (7, 4), (6, 5)]:
        for x in range(bx0 + shrink + 1, bx1 - shrink):
            p.append((x, dy, LIQUID))

    # --- Short neck (rows 3-5): 8px wide, x=12-19 ---
    nx0, nx1 = 12, 19
    _rect(p, nx0, 3, nx1, 5, GLASS_BODY)
    _col(p, nx0, 3, 5, GLASS_HL)
    _col(p, nx1, 3, 5, GLASS_DARK)
    _row(p, 3, nx0, nx1, OUTLINE)
    _col(p, nx0 - 1, 3, 5, OUTLINE)
    _col(p, nx1 + 1, 3, 5, OUTLINE)

    # --- Metal screw cap (rows 0-2): 8px wide matches neck ---
    cx0, cx1 = nx0, nx1
    _rect(p, cx0, 0, cx1, 2, CAP_BASE)
    _row(p, 0, cx0, cx1, CAP_HL)      # top catch-light
    _row(p, 2, cx0, cx1, CAP_SH)      # bottom shadow
    _col(p, cx0, 0, 2, CAP_SH)        # left edge
    _col(p, cx1, 0, 2, CAP_SH)        # right edge
    # Cap thread lines (horizontal engraved rings)
    _row(p, 1, cx0 + 1, cx1 - 1, CAP_RING)
    # Cap outline
    _row(p, 0, cx0 - 1, cx1 + 1, OUTLINE)
    p.append((cx0 - 1, 1, OUTLINE))
    p.append((cx0 - 1, 2, OUTLINE))
    p.append((cx1 + 1, 1, OUTLINE))
    p.append((cx1 + 1, 2, OUTLINE))
    _row(p, 3, cx0 - 1, cx1 + 1, OUTLINE)

    return p


def _beer_pixels():
    """
    Beer bottle: classic dark brown bottle, red/silver crown cap.
    Top-down: slim oval body (dark brown glass), amber liquid showing through.
    """
    p = []

    # Palette
    OUTLINE    = (18,   8,   3, 255)
    GLASS_BODY = (65,   30,   5, 255)  # dark brown glass
    GLASS_DARK = (32,   12,   2, 255)  # deep shadow
    GLASS_HL   = (105,  58,  12, 255)  # glass highlight
    LIQUID     = (172,  95,  18, 205)  # amber beer
    LIQUID_HL  = (208, 135,  38, 185)  # beer highlight
    CAP_RED    = (175,  25,  18, 255)  # red crown cap
    CAP_RED_HL = (215,  70,  55, 255)  # cap highlight
    CAP_METAL  = (155, 150, 145, 255)  # cap metal rim
    CAP_CRIMP  = (115, 110, 108, 255)  # crimped edge detail
    SHINE      = (195, 162,  88, 215)  # amber glass shine

    # --- Body: slim oval, 14px wide x 18px tall, rows 12-29, x=9-22 ---
    bx0, bx1 = 9, 22
    by0, by1 = 12, 29

    # Liquid fill
    _rect(p, bx0 + 1, by0 + 1, bx1 - 1, by1 - 1, LIQUID)

    # Liquid highlights
    for y in range(by0 + 1, by0 + 4):
        p.append((bx0 + 1, y, LIQUID_HL))
        p.append((bx0 + 2, y, LIQUID_HL))

    # Glass walls
    _row(p, by0, bx0, bx1, GLASS_BODY)
    _row(p, by1, bx0, bx1, GLASS_DARK)
    _col(p, bx0, by0 + 1, by1 - 1, GLASS_HL)
    _col(p, bx1, by0 + 1, by1 - 1, GLASS_DARK)
    _col(p, bx1 - 1, by0 + 2, by1 - 1, GLASS_DARK)
    _col(p, bx0 + 1, by0 + 2, by1 - 2, GLASS_HL)

    # Bottom rounded shadow
    _row(p, by1 - 1, bx0 + 1, bx1 - 1, GLASS_DARK)

    # Glass shine
    p.append((bx0 + 2, by0 + 2, SHINE))
    p.append((bx0 + 2, by0 + 3, SHINE))

    # Body outline
    _row(p, by0 - 1, bx0, bx1, OUTLINE)
    _row(p, by1 + 1, bx0, bx1, OUTLINE)
    _col(p, bx0 - 1, by0, by1, OUTLINE)
    _col(p, bx1 + 1, by0, by1, OUTLINE)

    # --- Shoulder taper (rows 8-11) ---
    shoulder = [(11, 1), (10, 2), (9, 3), (8, 4)]
    for (y, shrink) in shoulder:
        x0s = bx0 + shrink
        x1s = bx1 - shrink
        _row(p, y, x0s, x1s, GLASS_BODY)
        p.append((x0s, y, GLASS_HL))
        p.append((x1s, y, GLASS_DARK))
        p.append((x0s - 1, y, OUTLINE))
        p.append((x1s + 1, y, OUTLINE))
    # Liquid in shoulder
    for (y, shrink) in shoulder:
        for x in range(bx0 + shrink + 1, bx1 - shrink):
            p.append((x, y, LIQUID))

    # --- Neck (rows 3-7): 6px wide, x=13-18 ---
    nx0, nx1 = 13, 18
    _rect(p, nx0, 3, nx1, 7, GLASS_BODY)
    _col(p, nx0, 3, 7, GLASS_HL)
    _col(p, nx1, 3, 7, GLASS_DARK)
    _row(p, 3, nx0, nx1, OUTLINE)
    _col(p, nx0 - 1, 3, 7, OUTLINE)
    _col(p, nx1 + 1, 3, 7, OUTLINE)

    # --- Crown cap (rows 0-3): 8px wide (slightly wider than neck) ---
    # The classic pry-off crown cap: red top with metal crimped rim
    cx0, cx1 = nx0 - 1, nx1 + 1   # 8px wide: x=12-19
    _rect(p, cx0, 0, cx1, 2, CAP_RED)
    _row(p, 0, cx0, cx1, CAP_RED_HL)   # bright top highlight
    _row(p, 2, cx0, cx1, CAP_RED)

    # Crimped metal rim around cap edge
    _row(p, 3, cx0, cx1, CAP_METAL)    # bottom rim
    _col(p, cx0, 0, 3, CAP_METAL)      # left rim
    _col(p, cx1, 0, 3, CAP_METAL)      # right rim
    # Crimp texture (alternating dots on rim)
    for x in range(cx0, cx1 + 1, 2):
        p.append((x, 3, CAP_CRIMP))
    p.append((cx0, 1, CAP_METAL))
    p.append((cx0, 2, CAP_METAL))
    p.append((cx1, 1, CAP_METAL))
    p.append((cx1, 2, CAP_METAL))

    # Cap outline
    _row(p, 0, cx0 - 1, cx1 + 1, OUTLINE)
    _row(p, 4, cx0 - 1, cx1 + 1, OUTLINE)
    _col(p, cx0 - 1, 0, 3, OUTLINE)
    _col(p, cx1 + 1, 0, 3, OUTLINE)

    return p


# ---------------------------------------------------------------------------
# BOTTLE PAINTERS REGISTRY
# ---------------------------------------------------------------------------
BOTTLE_PIXELS = {
    "whiskey": _whiskey_pixels,
    "wine":    _wine_pixels,
    "gin":     _gin_pixels,
    "beer":    _beer_pixels,
}


# ---------------------------------------------------------------------------
# GENERATE
# ---------------------------------------------------------------------------
def generate() -> Image.Image:
    """
    Generate and return the 128x32 alcohol bottles spritesheet as RGBA PIL Image.

    Each bottle occupies a 32x32 cell. Pixel lists use local (0-31) x coords,
    which are offset by the bottle's column when composited.
    """
    sheet = Image.new("RGBA", (SHEET_W, SHEET_H), (0, 0, 0, 0))
    px = sheet.load()

    for i, name in enumerate(BOTTLE_NAMES):
        ox = i * BOTTLE_W   # x offset for this bottle cell
        pixel_fn = BOTTLE_PIXELS[name]
        raw_pixels = pixel_fn()

        # Use a dict for last-write-wins compositing within this cell
        canvas = {}
        for (x_local, y, color) in raw_pixels:
            x_abs = x_local + ox
            if 0 <= x_abs < SHEET_W and 0 <= y < SHEET_H:
                canvas[(x_abs, y)] = color

        for (x, y), color in canvas.items():
            px[x, y] = color

    return sheet


# ---------------------------------------------------------------------------
# ATLAS / JSON
# ---------------------------------------------------------------------------
def build_atlas(image_file: str) -> dict:
    """Return a Phaser-compatible JSON texture atlas for the bottles spritesheet."""
    frames = {}
    for i, name in enumerate(BOTTLE_NAMES):
        frames[name] = {
            "frame":            {"x": i * BOTTLE_W, "y": 0, "w": BOTTLE_W, "h": BOTTLE_H},
            "rotated":          False,
            "trimmed":          False,
            "spriteSourceSize": {"x": 0, "y": 0, "w": BOTTLE_W, "h": BOTTLE_H},
            "sourceSize":       {"w": BOTTLE_W, "h": BOTTLE_H},
        }
    return {
        "meta": {
            "image": image_file,
            "size": {"w": SHEET_W, "h": SHEET_H},
            "scale": "1",
        },
        "frames": frames,
        "animations": {
            name: [name] for name in BOTTLE_NAMES
        },
    }


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(PUBLIC_DIR, exist_ok=True)

    image_file = "alcohol_bottles.png"
    atlas_file = "alcohol_bottles.json"

    # Generate spritesheet
    sheet = generate()

    # Save to generated/
    out_png = os.path.join(OUTPUT_DIR, image_file)
    sheet.save(out_png)
    print(f"  Spritesheet : {out_png}  ({SHEET_W}x{SHEET_H})")

    # Save atlas JSON
    atlas = build_atlas(image_file)
    out_json = os.path.join(OUTPUT_DIR, atlas_file)
    with open(out_json, "w") as f:
        json.dump(atlas, f, indent=2)
    print(f"  Atlas       : {out_json}")

    # Export to public/assets/sprites/
    pub_png = os.path.join(PUBLIC_DIR, image_file)
    shutil.copy2(out_png, pub_png)
    print(f"  Exported    : {pub_png}")
