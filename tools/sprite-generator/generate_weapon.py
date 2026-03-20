#!/usr/bin/env python3
"""
Medieval/fantasy weapon sprite generator for Phaser 3.

Generates 32x32 weapon sprites in 4 orientations (E/S/W/N).
Spritesheet layout: 128x32 (4 frames side by side: E, S, W, N).

Weapons: sword, axe, spear, staff, bow, dagger, mace, greatsword

Usage:
    python generate_weapon.py --weapon sword
    python generate_weapon.py --all
    python generate_weapon.py --list
"""

import argparse
import json
import os
from PIL import Image

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "generated", "weapons")
FRAME_W = 32
FRAME_H = 32
ORIENTATIONS = ["east", "south", "west", "north"]

# ---------------------------------------------------------------------------
# PALETTES
# ---------------------------------------------------------------------------
WEAPON_PALETTES = {
    "sword": {
        "outline":   (30, 30, 40, 255),
        "blade":     (195, 208, 220, 255),
        "blade_hl":  (238, 245, 255, 255),
        "blade_sh":  (130, 145, 160, 255),
        "guard":     (155, 118, 38, 255),
        "guard_hl":  (215, 175, 75, 255),
        "handle":    (105, 58, 18, 255),
        "handle_hl": (155, 98, 48, 255),
        "pommel":    (155, 118, 38, 255),
        "pommel_hl": (215, 175, 75, 255),
    },
    "axe": {
        "outline":   (30, 30, 40, 255),
        "head":      (165, 172, 182, 255),
        "head_hl":   (218, 225, 235, 255),
        "head_sh":   (95,  102, 112, 255),
        "edge":      (240, 247, 255, 255),
        "handle":    (105, 68, 22, 255),
        "handle_hl": (155, 108, 52, 255),
        "wrap":      (75, 28, 18, 255),
    },
    "spear": {
        "outline":   (30, 30, 40, 255),
        "tip":       (198, 210, 222, 255),
        "tip_hl":    (240, 247, 255, 255),
        "tip_sh":    (125, 138, 152, 255),
        "shaft":     (125, 82, 32, 255),
        "shaft_hl":  (172, 128, 65, 255),
        "shaft_sh":  (78, 48, 18, 255),
        "ring":      (158, 128, 48, 255),
    },
    "staff": {
        "outline":   (30, 30, 40, 255),
        "wood":      (88, 52, 18, 255),
        "wood_hl":   (138, 92, 48, 255),
        "wood_sh":   (52, 28, 8, 255),
        "gem":       (75, 75, 198, 255),
        "gem_hl":    (155, 155, 255, 255),
        "gem_sh":    (28, 28, 118, 255),
        "band":      (158, 128, 48, 255),
        "glow":      (175, 175, 255, 160),
    },
    "bow": {
        "outline":   (30, 30, 40, 255),
        "wood":      (115, 72, 22, 255),
        "wood_hl":   (168, 118, 52, 255),
        "wood_sh":   (68, 38, 8, 255),
        "string":    (218, 208, 178, 255),
        "wrap":      (88, 38, 18, 255),
    },
    "dagger": {
        "outline":   (30, 30, 40, 255),
        "blade":     (198, 210, 222, 255),
        "blade_hl":  (240, 247, 255, 255),
        "blade_sh":  (135, 148, 162, 255),
        "guard":     (138, 98, 28, 255),
        "guard_hl":  (198, 158, 68, 255),
        "handle":    (78, 28, 18, 255),
        "handle_hl": (128, 68, 48, 255),
        "gem":       (178, 38, 38, 255),
        "gem_hl":    (238, 118, 118, 255),
    },
    "mace": {
        "outline":   (30, 30, 40, 255),
        "head":      (148, 152, 162, 255),
        "head_hl":   (198, 205, 215, 255),
        "head_sh":   (88, 92, 102, 255),
        "flange":    (168, 172, 182, 255),
        "flange_hl": (218, 225, 235, 255),
        "handle":    (98, 58, 18, 255),
        "handle_hl": (148, 98, 48, 255),
        "wrap":      (75, 28, 18, 255),
    },
    "greatsword": {
        "outline":   (30, 30, 40, 255),
        "blade":     (192, 205, 215, 255),
        "blade_hl":  (235, 245, 255, 255),
        "blade_sh":  (128, 140, 152, 255),
        "fuller":    (158, 168, 182, 255),
        "guard":     (148, 112, 32, 255),
        "guard_hl":  (208, 168, 72, 255),
        "grip":      (88, 42, 12, 255),
        "grip_hl":   (138, 82, 38, 255),
        "wrap":      (58, 22, 8, 255),
        "pommel":    (148, 112, 32, 255),
        "pommel_hl": (208, 168, 72, 255),
    },
    # ── Modern / Urban ──────────────────────────────────────────────────────
    "pistol": {
        "outline":   (20, 18, 25, 255),
        "slide":     (58, 62, 72, 255),
        "slide_hl":  (92, 96, 110, 255),
        "slide_sh":  (35, 37, 45, 255),
        "frame":     (48, 50, 60, 255),
        "frame_hl":  (72, 75, 88, 255),
        "grip":      (28, 22, 20, 255),
        "grip_hl":   (50, 42, 38, 255),
        "grip_tx":   (18, 14, 12, 255),
        "bore":      (8,  6,  10, 255),
        "guard":     (45, 47, 57, 255),
        "trigger":   (68, 72, 82, 255),
    },
    "shotgun": {
        "outline":   (22, 20, 27, 255),
        "barrel":    (68, 72, 80, 255),
        "barrel_hl": (105, 110, 120, 255),
        "barrel_sh": (40, 42, 50, 255),
        "pump":      (78, 55, 28, 255),
        "pump_hl":   (118, 88, 48, 255),
        "pump_sh":   (50, 32, 12, 255),
        "stock":     (110, 72, 30, 255),
        "stock_hl":  (155, 108, 55, 255),
        "stock_sh":  (68, 42, 15, 255),
        "bore":      (8,  6,  10, 255),
        "guard":     (55, 57, 65, 255),
        "trigger":   (75, 78, 88, 255),
    },
    "rifle": {
        "outline":   (18, 16, 22, 255),
        "body":      (45, 48, 55, 255),
        "body_hl":   (72, 76, 85, 255),
        "body_sh":   (28, 30, 36, 255),
        "stock":     (38, 32, 28, 255),
        "stock_hl":  (62, 53, 46, 255),
        "stock_sh":  (22, 18, 15, 255),
        "barrel":    (65, 68, 76, 255),
        "barrel_hl": (100, 104, 115, 255),
        "barrel_sh": (38, 40, 48, 255),
        "mag":       (55, 58, 65, 255),
        "mag_hl":    (82, 86, 95, 255),
        "mag_sh":    (32, 34, 40, 255),
        "bore":      (8,  6,  10, 255),
        "rail":      (35, 37, 44, 255),
        "guard":     (40, 42, 50, 255),
        "trigger":   (62, 65, 74, 255),
    },
    "bat": {
        "outline":   (28, 22, 16, 255),
        "wood":      (178, 122, 55, 255),
        "wood_hl":   (222, 168, 90, 255),
        "wood_sh":   (118, 78, 28, 255),
        "wood_dk":   (88, 55, 18, 255),
        "tape":      (35, 30, 28, 255),
        "tape_hl":   (58, 50, 46, 255),
        "knob":      (155, 108, 48, 255),
        "knob_hl":   (200, 152, 78, 255),
    },
    "knife": {
        "outline":   (20, 18, 24, 255),
        "blade":     (188, 198, 210, 255),
        "blade_hl":  (232, 240, 250, 255),
        "blade_sh":  (125, 135, 148, 255),
        "serrate":   (158, 168, 180, 255),
        "handle":    (25, 20, 18, 255),
        "handle_hl": (48, 40, 36, 255),
        "handle_tx": (15, 12, 10, 255),
        "guard":     (68, 72, 80, 255),
        "guard_hl":  (100, 105, 115, 255),
        "bolt":      (128, 118, 88, 255),
    },
    "chain": {
        "outline":   (25, 22, 30, 255),
        "metal":     (132, 136, 148, 255),
        "metal_hl":  (182, 188, 200, 255),
        "metal_sh":  (75, 78, 88, 255),
        "link_in":   (108, 112, 122, 255),
    },
    "molotov": {
        "outline":   (25, 20, 18, 255),
        "glass":     (148, 188, 148, 255),
        "glass_hl":  (198, 228, 195, 255),
        "glass_sh":  (88, 128, 88, 255),
        "liquid":    (185, 115, 35, 255),
        "liquid_hl": (225, 155, 65, 255),
        "rag":       (195, 172, 125, 255),
        "rag_sh":    (145, 120, 75, 255),
        "flame":     (225, 95, 25, 255),
        "flame_hl":  (245, 178, 65, 255),
        "flame_tip": (250, 228, 108, 255),
    },
    "taser": {
        "outline":   (20, 18, 25, 255),
        "body":      (48, 52, 162, 255),
        "body_hl":   (82, 88, 205, 255),
        "body_sh":   (28, 32, 112, 255),
        "grip":      (32, 28, 25, 255),
        "grip_hl":   (54, 46, 42, 255),
        "grip_tx":   (18, 15, 12, 255),
        "prong":     (218, 198, 68, 255),
        "prong_hl":  (250, 238, 120, 255),
        "arc":       (165, 188, 252, 255),
        "arc_hl":    (222, 235, 255, 255),
        "trigger":   (65, 68, 78, 255),
        "label":     (200, 200, 220, 255),
    },
}

# ---------------------------------------------------------------------------
# PIXEL HELPERS
# ---------------------------------------------------------------------------

def _row(y, x0, x1, color):
    """Inclusive row of pixels."""
    return [(x, y, color) for x in range(x0, x1 + 1)]


def _col(x, y0, y1, color):
    """Inclusive column of pixels."""
    return [(x, y, color) for y in range(y0, y1 + 1)]


# ---------------------------------------------------------------------------
# WEAPON PIXEL DEFINITIONS  (East orientation — tip pointing right)
# All coordinates are absolute within the 32x32 frame.
# Center of frame = (15, 15).  Grip area near center, tip to the right.
# ---------------------------------------------------------------------------

def _sword_pixels():
    """One-handed arming sword — 22px total length."""
    p = []

    # ---- Pommel (2×2 rounded gold cap, far left) ----
    p += [(5, 14, "pommel_hl"), (5, 15, "pommel")]
    p += [(6, 14, "pommel_hl"), (6, 15, "pommel")]
    p += [(5, 13, "outline"),   (5, 16, "outline")]
    p += [(6, 13, "outline"),   (6, 16, "outline")]
    p += [(4, 14, "outline"),   (4, 15, "outline")]
    p += [(7, 14, "outline"),   (7, 15, "outline")]

    # ---- Handle (5px brown grip) ----
    for x in range(7, 12):
        p += [(x, 13, "outline"), (x, 14, "handle_hl"),
              (x, 15, "handle"),  (x, 16, "outline")]

    # ---- Cross-guard (3px tall, 2px wide gold) ----
    for dy in range(-3, 4):
        c = "guard_hl" if dy < 0 else "guard"
        p += [(12, 15 + dy, c), (13, 15 + dy, c)]
    p += [(12, 11, "outline"), (13, 11, "outline")]
    p += [(12, 19, "outline"), (13, 19, "outline")]
    p += [(11, 12, "outline"), (11, 13, "outline")]
    p += [(14, 12, "outline"), (14, 13, "outline")]
    p += [(11, 17, "outline"), (11, 18, "outline")]
    p += [(14, 17, "outline"), (14, 18, "outline")]

    # ---- Blade (14px, 3px thick: hl/base/shade) ----
    for x in range(14, 28):
        p += [(x, 12, "outline"), (x, 13, "blade_hl"),
              (x, 14, "blade_hl"), (x, 15, "blade"),
              (x, 16, "blade_sh"), (x, 17, "outline")]

    # ---- Tip (tapers to a point) ----
    p += [(28, 13, "outline"), (28, 14, "blade_hl"), (28, 15, "blade"),
          (28, 16, "outline")]
    p += [(29, 14, "outline"), (29, 15, "blade_hl"), (29, 16, "outline")]
    p += [(30, 15, "blade_hl"), (30, 16, "outline")]
    p += [(31, 15, "outline")]

    return p


def _axe_pixels():
    """Single-bladed war-axe — blade edge points right."""
    p = []

    # ---- Handle (8px, centered) ----
    for x in range(5, 13):
        p += [(x, 13, "outline"), (x, 14, "handle_hl"),
              (x, 15, "handle"),  (x, 16, "handle"),
              (x, 17, "outline")]
    # Leather wrap bands
    for wx in [7, 10]:
        p += [(wx, 14, "wrap"), (wx, 15, "wrap"), (wx, 16, "wrap")]

    # ---- Axe head (angular body) ----
    # Top curve of head
    for x in range(13, 20):
        spread = max(0, (x - 13) // 2)
        top_y = 10 - spread
        p += [(x, top_y, "outline"), (x, top_y + 1, "head_hl"), (x, top_y + 2, "head")]
    # Bottom curve of head (mirror)
    for x in range(13, 20):
        spread = max(0, (x - 13) // 2)
        bot_y = 20 + spread
        p += [(x, bot_y, "outline"), (x, bot_y - 1, "head"), (x, bot_y - 2, "head_sh")]
    # Solid fill between top and bottom curves
    for x in range(13, 22):
        spread = min(5, max(0, (x - 13) // 2))
        for y in range(11 + spread, 20 - spread + 1):
            c = "head_hl" if y < 15 else ("head" if y < 17 else "head_sh")
            p.append((x, y, c))
    # Back of axe head (left edge flush with handle end)
    p += _col(13, 12, 18, "head_sh")
    p += [(12, 12, "outline"), (12, 13, "outline"), (12, 17, "outline"), (12, 18, "outline")]

    # ---- Blade edge (bright on right side) ----
    for y in range(8, 23):
        p += [(21, y, "edge"), (22, y, "outline")]

    # Outlines across top and bottom of head
    p += [(x, 9, "outline") for x in range(14, 22)]
    p += [(x, 22, "outline") for x in range(14, 22)]

    return p


def _spear_pixels():
    """Long spear — tip points right."""
    p = []

    # ---- Shaft (long wooden pole, left ~2/3 of frame) ----
    for x in range(2, 22):
        p += [(x, 13, "outline"), (x, 14, "shaft_hl"),
              (x, 15, "shaft"),   (x, 16, "shaft_sh"),
              (x, 17, "outline")]

    # Gold binding rings
    for rx in [6, 13]:
        for dy in range(-1, 2):
            p.append((rx, 15 + dy, "ring"))
        p += [(rx, 13, "outline"), (rx, 17, "outline")]

    # ---- Spear tip (leaf-blade) ----
    for x in range(22, 30):
        t = x - 22
        spread = max(0, 3 - t // 2)
        for dy in range(-spread, spread + 1):
            c = "tip_hl" if dy < 0 else ("tip" if dy == 0 else "tip_sh")
            p.append((x, 15 + dy, c))
        p += [(x, 15 - spread - 1, "outline"), (x, 15 + spread + 1, "outline")]
    # Absolute point
    p += [(30, 15, "tip_hl"), (30, 16, "outline")]

    # Socket where shaft meets blade
    for dy in range(-2, 3):
        p.append((22, 15 + dy, "ring"))

    return p


def _staff_pixels():
    """Magic staff — orb end points right."""
    p = []

    # ---- Wooden shaft ----
    for x in range(2, 22):
        p += [(x, 13, "outline"), (x, 14, "wood_hl"),
              (x, 15, "wood"),    (x, 16, "wood_sh"),
              (x, 17, "outline")]

    # Decorative bands
    for bx in [5, 12, 18]:
        for dy in range(-2, 3):
            p.append((bx, 15 + dy, "band"))
        p += [(bx, 12, "outline"), (bx, 18, "outline")]

    # ---- Orb (magic gem, 7×7 circle) ----
    gx, gy = 26, 15
    # Glow halo (semi-transparent, behind gem)
    halo = [(-4,0),(4,0),(0,-4),(0,4),(-3,-2),(-3,2),(3,-2),(3,2),
            (-2,-3),(-2,3),(2,-3),(2,3)]
    for dx, dy in halo:
        p.append((gx+dx, gy+dy, "glow"))
    # Gem fill (3×3 inner)
    for dx in range(-1, 2):
        for dy in range(-1, 2):
            c = "gem_hl" if dy < 0 and dx < 0 else ("gem_sh" if dy > 0 else "gem")
            p.append((gx+dx, gy+dy, c))
    # Gem ring
    ring = [(-2,-1),(-2,0),(-2,1),(-1,-2),(0,-2),(1,-2),
            (2,-1),(2,0),(2,1),(-1,2),(0,2),(1,2)]
    for dx, dy in ring:
        c = "gem_hl" if dy < -1 else ("gem_sh" if dy > 1 else "gem")
        p.append((gx+dx, gy+dy, c))
    # Catchlight
    p += [(gx-1, gy-1, "gem_hl")]
    # Outline
    outline_ring = [(-3,-1),(-3,0),(-3,1),(-1,-3),(0,-3),(1,-3),
                    (3,-1),(3,0),(3,1),(-1,3),(0,3),(1,3),
                    (-2,-2),(2,-2),(-2,2),(2,2)]
    for dx, dy in outline_ring:
        p.append((gx+dx, gy+dy, "outline"))

    # Socket connecting orb to shaft
    for dy in range(-2, 3):
        p.append((22, gy+dy, "band"))

    return p


def _bow_pixels():
    """Strung longbow — nock faces right (bowstring at right)."""
    p = []

    cx, cy = 16, 15

    # String (vertical line near right)
    sx = cx + 6
    for y in range(cy - 7, cy + 8):
        p.append((sx, y, "string"))

    # Upper limb (curved, from center-left to upper-right)
    for i in range(8):
        bx = cx - 1 - (i * i) // 9
        by = cy - i
        p += [(bx,   by, "wood_hl"),
              (bx-1, by, "wood"),
              (bx-2, by, "wood_sh"),
              (bx+1, by, "outline"),
              (bx-3, by, "outline")]

    # Lower limb (mirror of upper)
    for i in range(8):
        bx = cx - 1 - (i * i) // 9
        by = cy + i
        p += [(bx,   by, "wood_hl"),
              (bx-1, by, "wood"),
              (bx-2, by, "wood_sh"),
              (bx+1, by, "outline"),
              (bx-3, by, "outline")]

    # Center grip wrap
    for dy in range(-2, 3):
        p += [(cx-1, cy+dy, "wrap"), (cx, cy+dy, "wrap")]

    # String connecting limb tips to string line
    tip_x = cx - 1 - (7 * 7) // 9
    # Upper string segment
    for x in range(tip_x, sx):
        t = (x - tip_x) / max(1, sx - tip_x)
        y = round((cy - 7) * (1-t) + (cy - 7) * t)
        # Linear from tip to string top
    steps = sx - tip_x
    for i in range(steps + 1):
        t = i / max(1, steps)
        x = tip_x + i
        y = round((cy - 7) + t * 7)
        p.append((x, y, "string"))
    for i in range(steps + 1):
        t = i / max(1, steps)
        x = tip_x + i
        y = round((cy + 7) - t * 7)
        p.append((x, y, "string"))

    return p


def _dagger_pixels():
    """Short dagger — tip points right."""
    p = []
    cx, cy = 14, 15

    # ---- Pommel (ruby gem cap) ----
    p += [(cx-5, cy-1, "gem_hl"), (cx-5, cy, "gem"),
          (cx-4, cy-1, "gem_hl"), (cx-4, cy, "gem")]
    p += [(cx-6, cy-1, "outline"), (cx-6, cy, "outline"), (cx-6, cy+1, "outline")]
    p += [(cx-5, cy-2, "outline"), (cx-4, cy-2, "outline")]
    p += [(cx-5, cy+1, "outline"), (cx-4, cy+1, "outline")]
    p += [(cx-3, cy-1, "outline"), (cx-3, cy, "outline")]

    # ---- Handle ----
    for x in range(cx-3, cx+1):
        p += [(x, cy-2, "outline"), (x, cy-1, "handle_hl"),
              (x, cy,   "handle"),  (x, cy+1, "outline")]

    # ---- Guard (2px wide, 5px tall) ----
    for dy in range(-2, 3):
        c = "guard_hl" if dy < 0 else "guard"
        p += [(cx+1, cy+dy, c), (cx+2, cy+dy, c)]
    p += [(cx+1, cy-3, "outline"), (cx+2, cy-3, "outline")]
    p += [(cx+1, cy+3, "outline"), (cx+2, cy+3, "outline")]
    p += [(cx,   cy-2, "outline"), (cx,   cy-1, "outline")]
    p += [(cx+3, cy-2, "outline"), (cx+3, cy-1, "outline")]
    p += [(cx,   cy+1, "outline"), (cx,   cy+2, "outline")]
    p += [(cx+3, cy+1, "outline"), (cx+3, cy+2, "outline")]

    # ---- Blade (tapered) ----
    for x in range(cx+3, cx+12):
        t = x - (cx+3)
        spread = max(1, 2 - t // 3)
        for dy in range(-spread, spread+1):
            c = "blade_hl" if dy < 0 else ("blade" if dy == 0 else "blade_sh")
            p.append((x, cy+dy, c))
        p += [(x, cy-spread-1, "outline"), (x, cy+spread+1, "outline")]
    # Tip
    p += [(cx+12, cy, "blade_hl"), (cx+12, cy+1, "outline")]

    return p


def _mace_pixels():
    """Flanged mace — head points right."""
    p = []
    cx, cy = 10, 15

    # ---- Handle ----
    for x in range(cx-5, cx+5):
        p += [(x, cy-2, "outline"), (x, cy-1, "handle_hl"),
              (x, cy,   "handle"),  (x, cy+1, "handle"),
              (x, cy+2, "outline")]
    # Leather wraps
    for wx in [cx-3, cx]:
        for dy in range(-1, 2):
            p.append((wx, cy+dy, "wrap"))

    # ---- Mace head core (hex/cylindrical) ----
    hx = cx + 5
    for dy in range(-3, 4):
        w = 5 - abs(dy) // 2
        for dx in range(0, w):
            c = "head_hl" if dx == 0 else ("head" if dx < w-1 else "head_sh")
            p.append((hx+dx, cy+dy, c))

    # ---- Flanges (top, bottom, right, diagonals) ----
    # Top flange
    for dy in range(-5, -2):
        p += [(hx+1, cy+dy, "flange"), (hx+2, cy+dy, "flange_hl")]
        p += [(hx,   cy+dy, "outline"), (hx+3, cy+dy, "outline")]
    p += [(hx+1, cy-6, "outline"), (hx+2, cy-6, "outline")]
    # Bottom flange
    for dy in range(3, 6):
        p += [(hx+1, cy+dy, "flange"), (hx+2, cy+dy, "flange_hl")]
        p += [(hx,   cy+dy, "outline"), (hx+3, cy+dy, "outline")]
    p += [(hx+1, cy+6, "outline"), (hx+2, cy+6, "outline")]
    # Right flange
    for dx in range(5, 9):
        p += [(hx+dx, cy-1, "flange_hl"), (hx+dx, cy, "flange"),
              (hx+dx, cy+1, "flange")]
        p += [(hx+dx, cy-2, "outline"), (hx+dx, cy+2, "outline")]
    p += [(hx+9, cy-1, "outline"), (hx+9, cy, "outline"), (hx+9, cy+1, "outline")]
    # Top-right diagonal flange
    for i in range(3):
        p += [(hx+4+i, cy-3-i, "flange_hl"), (hx+5+i, cy-3-i, "flange")]
        p += [(hx+3+i, cy-3-i, "outline"), (hx+6+i, cy-3-i, "outline")]
    # Bottom-right diagonal flange
    for i in range(3):
        p += [(hx+4+i, cy+3+i, "flange"), (hx+5+i, cy+3+i, "flange")]
        p += [(hx+3+i, cy+3+i, "outline"), (hx+6+i, cy+3+i, "outline")]

    # Core outlines
    p += [(hx-1, cy+dy, "outline") for dy in range(-3, 4)]
    p += [(hx+dx, cy-4, "outline") for dx in range(0, 6)]
    p += [(hx+dx, cy+4, "outline") for dx in range(0, 6)]

    return p


def _greatsword_pixels():
    """Two-handed greatsword — very long, tip points right."""
    p = []
    cx, cy = 15, 15

    # ---- Pommel (wide diamond) ----
    p += [(cx-13, cy-1, "pommel_hl"), (cx-13, cy, "pommel")]
    p += [(cx-12, cy-2, "pommel_hl"), (cx-12, cy-1, "pommel_hl"),
          (cx-12, cy,   "pommel"),    (cx-12, cy+1, "pommel")]
    p += [(cx-11, cy-1, "pommel_hl"), (cx-11, cy, "pommel")]
    p += [(cx-14, cy-1, "outline"), (cx-14, cy, "outline")]
    p += [(cx-13, cy-2, "outline"), (cx-13, cy+1, "outline")]
    p += [(cx-12, cy-3, "outline"), (cx-12, cy+2, "outline")]
    p += [(cx-11, cy-2, "outline"), (cx-11, cy+1, "outline")]
    p += [(cx-10, cy-1, "outline"), (cx-10, cy, "outline")]

    # ---- Grip (6px with wrap) ----
    for x in range(cx-10, cx-4):
        p += [(x, cy-2, "outline"), (x, cy-1, "grip_hl"),
              (x, cy,   "grip"),    (x, cy+1, "wrap" if (x % 2 == 0) else "grip"),
              (x, cy+2, "outline")]

    # ---- Guard (wider, 8px tall, 2px wide) ----
    for dy in range(-4, 5):
        c = "guard_hl" if dy < 0 else "guard"
        p += [(cx-4, cy+dy, c), (cx-3, cy+dy, c)]
    p += [(cx-4, cy-5, "outline"), (cx-3, cy-5, "outline")]
    p += [(cx-4, cy+5, "outline"), (cx-3, cy+5, "outline")]
    p += [(cx-5, cy-4, "outline"), (cx-5, cy-3, "outline")]
    p += [(cx-2, cy-4, "outline"), (cx-2, cy-3, "outline")]
    p += [(cx-5, cy+3, "outline"), (cx-5, cy+4, "outline")]
    p += [(cx-2, cy+3, "outline"), (cx-2, cy+4, "outline")]

    # ---- Blade (3px thick with fuller groove, tapers to point) ----
    for x in range(cx-2, cx+15):
        p += [(x, cy-3, "outline"),
              (x, cy-2, "blade_hl"),
              (x, cy-1, "blade_hl"),
              (x, cy,   "fuller"),
              (x, cy+1, "blade"),
              (x, cy+2, "blade_sh"),
              (x, cy+3, "outline")]

    # Taper section
    for x in range(cx+15, cx+18):
        t = x - (cx+15)
        spread = max(1, 3 - t)
        for dy in range(-spread, spread+1):
            c = "blade_hl" if dy < 0 else ("fuller" if dy == 0 else "blade")
            p.append((x, cy+dy, c))
        p += [(x, cy-spread-1, "outline"), (x, cy+spread+1, "outline")]
    # Very tip
    p += [(cx+18, cy, "blade_hl"), (cx+18, cy+1, "outline")]

    return p


# ---------------------------------------------------------------------------
# MODERN WEAPON PIXEL DEFINITIONS  (East orientation — barrel/tip points right)
# ---------------------------------------------------------------------------

def _pistol_pixels():
    """Semi-auto handgun — barrel points east (right), grip hangs south."""
    p = []
    SL, SR = 8, 27   # slide left/right x
    ST, SB = 12, 16  # slide top/bottom y (barrel centerline at y=13-14)

    # ---- Slide (horizontal body) ----
    p += [(x, ST - 1, "outline") for x in range(SL, SR + 1)]
    p += [(x, ST,     "slide_hl") for x in range(SL, SR)]
    p += [(x, ST + 1, "slide")    for x in range(SL, SR)]
    p += [(x, ST + 2, "slide")    for x in range(SL, SR)]
    p += [(x, ST + 3, "frame")    for x in range(SL, SL + 10)]
    p += [(x, ST + 3, "slide_sh") for x in range(SL + 10, SR)]
    p += [(x, SB, "outline")  for x in range(SL - 1, SR + 2)]
    p += [(SL - 1, y, "outline") for y in range(ST, SB)]

    # ---- Muzzle ----
    p += [(SR, ST, "bore"), (SR, ST + 1, "bore"), (SR, ST + 2, "bore")]
    p += [(SR + 1, y, "outline") for y in range(ST, SB)]

    # ---- Sights ----
    p += [(SL + 1, ST - 2, "outline"), (SL + 2, ST - 2, "slide_hl")]  # rear
    p += [(SR - 3, ST - 2, "outline"), (SR - 3, ST - 1, "slide_hl")]  # front

    # ---- Ejection port slot ----
    for x in range(SL + 8, SL + 11):
        p.append((x, ST, "bore"))

    # ---- Frame (lower receiver) ----
    FL, FR = SL, SL + 10
    for y in range(SB, SB + 4):
        c = "frame_hl" if y == SB else "frame"
        p += [(x, y, c) for x in range(FL, FR + 1)]
        p += [(FL - 1, y, "outline"), (FR + 1, y, "outline")]
    p += [(x, SB + 4, "outline") for x in range(FL - 1, FR + 2)]

    # ---- Trigger guard ----
    TGL, TGR = FL + 3, FL + 8
    for y in range(SB, SB + 7):
        p += [(TGL, y, "guard"), (TGR, y, "guard")]
    p += [(x, SB + 7, "guard") for x in range(TGL + 1, TGR)]
    p += [(x, SB + 8, "outline") for x in range(TGL, TGR + 1)]
    p += [(TGL - 1, SB, "outline"), (TGR + 1, SB, "outline")]

    # ---- Trigger ----
    TX = TGL + 2
    p += [(TX, SB + 1, "trigger"), (TX, SB + 2, "trigger"), (TX, SB + 3, "trigger")]

    # ---- Grip ----
    GX0, GX1 = FL, FL + 4
    for y in range(SB + 3, SB + 12):
        for x in range(GX0, GX1 + 1):
            c = "grip_hl" if x == GX0 else ("grip_tx" if (x + y) % 3 == 0 else "grip")
            p.append((x, y, c))
        p += [(GX0 - 1, y, "outline"), (GX1 + 1, y, "outline")]
    p += [(x, SB + 12, "outline") for x in range(GX0 - 1, GX1 + 2)]

    return p


def _shotgun_pixels():
    """Pump-action shotgun — barrel points east, wood stock on west."""
    p = []
    CY = 14  # barrel center y

    # ---- Wood stock (x=2-9) ----
    for x in range(2, 10):
        spread = 4 - max(0, (x - 2) // 3)
        for dy in range(-spread, spread + 1):
            c = "stock_hl" if dy < 0 else ("stock_sh" if dy >= spread - 1 else "stock")
            p.append((x, CY + dy, c))
        p += [(x, CY - spread - 1, "outline"), (x, CY + spread + 1, "outline")]
    p += [(1, CY + dy, "outline") for dy in range(-3, 4)]

    # ---- Receiver / action body (x=9-14) ----
    for x in range(9, 15):
        p += [(x, CY - 3, "outline"),
              (x, CY - 2, "barrel_hl"),
              (x, CY - 1, "barrel"),
              (x, CY,     "barrel"),
              (x, CY + 1, "barrel"),
              (x, CY + 2, "barrel_sh"),
              (x, CY + 3, "outline")]

    # ---- Barrel (x=14-28) ----
    for x in range(14, 29):
        p += [(x, CY - 2, "outline"),
              (x, CY - 1, "barrel_hl"),
              (x, CY,     "barrel"),
              (x, CY + 1, "barrel_sh"),
              (x, CY + 2, "outline")]

    # ---- Muzzle ----
    p += [(29, CY - 1, "bore"), (29, CY, "bore")]
    p += [(29, CY - 2, "outline"), (29, CY + 1, "outline")]
    p += [(30, CY - 1, "outline"), (30, CY, "outline"), (30, CY + 1, "outline")]

    # ---- Pump foregrip (under barrel, x=15-21) ----
    for x in range(15, 22):
        p += [(x, CY + 2, "outline"),
              (x, CY + 3, "pump_hl"),
              (x, CY + 4, "pump"),
              (x, CY + 5, "pump_sh"),
              (x, CY + 6, "outline")]
    p += [(14, y, "outline") for y in range(CY + 3, CY + 6)]
    p += [(22, y, "outline") for y in range(CY + 3, CY + 6)]

    # ---- Trigger guard ----
    TGL, TGR = 10, 14
    for y in range(CY + 3, CY + 8):
        p += [(TGL, y, "guard"), (TGR, y, "guard")]
    p += [(x, CY + 8, "guard") for x in range(TGL + 1, TGR)]
    p += [(x, CY + 9, "outline") for x in range(TGL, TGR + 1)]
    p += [(TGL - 1, CY + 3, "outline"), (TGR + 1, CY + 3, "outline")]

    # ---- Trigger ----
    p += [(12, CY + 4, "trigger"), (12, CY + 5, "trigger"), (12, CY + 6, "trigger")]

    return p


def _rifle_pixels():
    """AR-style assault rifle — barrel points east, stock on west."""
    p = []
    CY = 13  # barrel/receiver center y

    # ---- Collapsible stock (x=2-8) ----
    for y in range(CY - 1, CY + 5):
        c = "stock_hl" if y == CY - 1 else ("stock_sh" if y >= CY + 3 else "stock")
        p += [(x, y, c) for x in range(2, 9)]
    p += [(x, CY - 2, "outline") for x in range(2, 9)]
    p += [(x, CY + 5, "outline") for x in range(2, 9)]
    p += [(1, y, "outline") for y in range(CY - 1, CY + 5)]
    p += [(9, y, "outline") for y in range(CY - 1, CY + 5)]
    # Stock skeleton cut-outs
    p += [(4, CY + 1, "body_sh"), (4, CY + 2, "body_sh")]
    p += [(6, CY + 1, "body_sh"), (6, CY + 2, "body_sh")]

    # ---- Upper receiver + flat-top rail (x=8-18) ----
    p += [(x, CY - 4, "rail") for x in range(8, 19)]       # Picatinny rail
    p += [(x, CY - 5, "outline") for x in range(8, 19)]
    for x in range(9, 18, 2):                                # Rail teeth
        p.append((x, CY - 4, "outline"))
    for x in range(8, 19):
        p += [(x, CY - 3, "outline"),
              (x, CY - 2, "body_hl"),
              (x, CY - 1, "body"),
              (x, CY,     "body"),
              (x, CY + 1, "body"),
              (x, CY + 2, "body_sh"),
              (x, CY + 3, "outline")]

    # ---- Barrel (x=18-29) ----
    for x in range(18, 30):
        p += [(x, CY - 2, "outline"),
              (x, CY - 1, "barrel_hl"),
              (x, CY,     "barrel"),
              (x, CY + 1, "barrel_sh"),
              (x, CY + 2, "outline")]
    p += [(30, CY - 1, "bore"), (30, CY, "bore")]
    p += [(30, CY - 2, "outline"), (30, CY + 1, "outline")]

    # ---- Pistol grip (x=8-12, below receiver) ----
    GX0, GX1 = 8, 12
    for y in range(CY + 3, CY + 10):
        for x in range(GX0, GX1 + 1):
            c = "body_hl" if x == GX0 else "body"
            p.append((x, y, c))
        p += [(GX0 - 1, y, "outline"), (GX1 + 1, y, "outline")]
    p += [(x, CY + 10, "outline") for x in range(GX0 - 1, GX1 + 2)]

    # ---- Trigger guard ----
    TGL, TGR = 12, 17
    for y in range(CY + 3, CY + 8):
        p += [(TGL, y, "guard"), (TGR, y, "guard")]
    p += [(x, CY + 8, "guard") for x in range(TGL + 1, TGR)]
    p += [(x, CY + 9, "outline") for x in range(TGL, TGR + 1)]

    # ---- Trigger ----
    p += [(14, CY + 4, "trigger"), (14, CY + 5, "trigger")]

    # ---- Magazine (x=12-17, hangs down) ----
    MX0, MX1 = 12, 17
    for y in range(CY + 8, CY + 16):
        for x in range(MX0, MX1 + 1):
            c = "mag_hl" if x == MX0 else ("mag_sh" if x == MX1 else "mag")
            p.append((x, y, c))
        p += [(MX0 - 1, y, "outline"), (MX1 + 1, y, "outline")]
    p += [(x, CY + 16, "outline") for x in range(MX0 - 1, MX1 + 2)]
    # Mag curve bottom
    p += [(MX0, CY + 15, "body_sh"), (MX1, CY + 15, "body_sh")]

    # ---- Charging handle ----
    p += [(9, CY - 3, "body_hl"), (9, CY - 5, "outline")]

    return p


def _bat_pixels():
    """Baseball bat — barrel (thick end) points east, knob on west."""
    p = []
    CY = 15

    # ---- Knob (rounded cap on grip end) ----
    p += [(3, CY - 1, "knob_hl"), (3, CY, "knob"),    (3, CY + 1, "knob")]
    p += [(4, CY - 2, "knob_hl"), (4, CY - 1, "knob"), (4, CY, "knob"),
          (4, CY + 1, "knob"),    (4, CY + 2, "outline")]
    p += [(2, CY - 1, "outline"), (2, CY, "outline"), (2, CY + 1, "outline")]
    p += [(3, CY - 2, "outline"), (3, CY + 2, "outline")]
    p += [(5, CY - 2, "outline"), (5, CY + 2, "outline")]

    # ---- Handle with grip tape (x=5-12) ----
    for x in range(5, 13):
        p += [(x, CY - 2, "outline"),
              (x, CY - 1, "tape_hl" if x % 2 == 1 else "wood_hl"),
              (x, CY,     "tape"    if x % 2 == 1 else "wood"),
              (x, CY + 1, "tape"    if x % 2 == 0 else "wood_sh"),
              (x, CY + 2, "outline")]

    # ---- Taper zone (handle to barrel, x=12-17) ----
    for x in range(12, 18):
        t = x - 12
        spread = 1 + t // 2
        for dy in range(-spread, spread + 1):
            c = "wood_hl" if dy < 0 else ("wood_sh" if dy == spread else "wood")
            p.append((x, CY + dy, c))
        p += [(x, CY - spread - 1, "outline"), (x, CY + spread + 1, "outline")]

    # ---- Barrel (thick hitting zone, x=17-29) ----
    for x in range(17, 30):
        for dy in range(-3, 4):
            c = "wood_hl" if dy < 0 else ("wood_sh" if dy >= 2 else "wood")
            p.append((x, CY + dy, c))
        p += [(x, CY - 4, "outline"), (x, CY + 4, "outline")]
    # Wood grain streaks
    for x in range(18, 28, 3):
        p.append((x, CY + 1, "wood_dk"))

    # ---- Barrel end (rounded tip) ----
    p += [(30, CY - 2, "outline"), (30, CY - 1, "wood"), (30, CY, "wood"),
          (30, CY + 1, "wood_sh"),  (30, CY + 2, "outline")]
    p += [(31, CY - 1, "outline"),  (31, CY, "wood_sh"),  (31, CY + 1, "outline")]

    return p


def _knife_pixels():
    """Modern combat knife — clip-point blade, tip points east."""
    p = []
    CX, CY = 13, 15

    # ---- Tactical handle (finger-groove rubber, x=CX-8 to CX-1) ----
    for x in range(CX - 8, CX):
        groove = (x - CX) % 2 == 0
        p += [(x, CY - 3, "outline"),
              (x, CY - 2, "handle_hl"),
              (x, CY - 1, "handle"),
              (x, CY,     "handle_tx" if groove else "handle"),
              (x, CY + 1, "handle"),
              (x, CY + 2, "outline")]
    # Retaining bolts
    for bx in [CX - 7, CX - 3]:
        p += [(bx, CY - 1, "bolt"), (bx, CY, "bolt")]

    # ---- Finger guard ----
    for dy in range(-3, 4):
        c = "guard_hl" if dy < 0 else "guard"
        p += [(CX - 1, CY + dy, c), (CX, CY + dy, c)]
    p += [(CX - 1, CY - 4, "outline"), (CX, CY - 4, "outline")]
    p += [(CX - 1, CY + 4, "outline"), (CX, CY + 4, "outline")]
    p += [(CX - 2, CY - 3, "outline"), (CX - 2, CY - 2, "outline")]
    p += [(CX + 1, CY - 3, "outline"), (CX + 1, CY - 2, "outline")]
    p += [(CX - 2, CY + 2, "outline"), (CX - 2, CY + 3, "outline")]
    p += [(CX + 1, CY + 2, "outline"), (CX + 1, CY + 3, "outline")]

    # ---- Blade spine (top/back edge, straight) ----
    # ---- Blade belly (bottom edge, curves to clip point at tip) ----
    # Main blade body (x=CX+1 to CX+10)
    for x in range(CX + 1, CX + 11):
        p += [(x, CY - 3, "outline"),
              (x, CY - 2, "blade_hl"),
              (x, CY - 1, "blade_hl"),
              (x, CY,     "blade"),
              (x, CY + 1, "blade_sh"),
              (x, CY + 2, "outline")]
    # Serration on spine
    for x in range(CX + 2, CX + 9, 2):
        p.append((x, CY - 3, "serrate"))

    # Clip taper (x=CX+10 to CX+15, spine drops to meet edge)
    for x in range(CX + 10, CX + 15):
        t = x - (CX + 10)
        top_s = max(0, 2 - t)   # spine clips down
        bot_s = max(0, 2 - t)   # edge also closes
        for dy in range(-top_s, bot_s + 1):
            c = "blade_hl" if dy < 0 else ("blade" if dy == 0 else "blade_sh")
            p.append((x, CY + dy, c))
        if top_s >= 0:
            p += [(x, CY - top_s - 1, "outline"), (x, CY + bot_s + 1, "outline")]

    # Tip
    p += [(CX + 15, CY, "blade_hl"), (CX + 15, CY + 1, "outline")]

    return p


def _chain_pixels():
    """Metal chain — alternating H/V oval links extending east."""
    p = []

    # 8 links in a roughly horizontal band, slight wave
    links = [
        (4,  13, "h"), (8,  16, "v"), (12, 13, "h"),
        (16, 16, "v"), (20, 13, "h"), (24, 16, "v"),
        (28, 13, "h"),
    ]

    for (lx, ly, orient) in links:
        if orient == "h":   # horizontal oval (5w × 3h)
            for dx in range(-2, 3):
                p += [(lx + dx, ly - 1, "metal_hl"),
                      (lx + dx, ly,     "metal"),
                      (lx + dx, ly + 1, "metal_sh")]
            # End caps
            p += [(lx - 3, ly - 1, "outline"), (lx - 3, ly, "metal_sh"), (lx - 3, ly + 1, "outline")]
            p += [(lx + 3, ly - 1, "outline"), (lx + 3, ly, "metal"),    (lx + 3, ly + 1, "outline")]
            # Top/bottom outlines
            p += [(lx + dx, ly - 2, "outline") for dx in range(-2, 3)]
            p += [(lx + dx, ly + 2, "outline") for dx in range(-2, 3)]
            # Inner hole
            p += [(lx - 1, ly, "link_in"), (lx, ly, "link_in"), (lx + 1, ly, "link_in")]
        else:               # vertical oval (3w × 5h)
            for dy in range(-2, 3):
                p += [(lx,     ly + dy, "metal_hl"),
                      (lx + 1, ly + dy, "metal"),
                      (lx + 2, ly + dy, "metal_sh")]
            # End caps
            p += [(lx, ly - 3, "outline"), (lx + 1, ly - 3, "metal_hl"),   (lx + 2, ly - 3, "outline")]
            p += [(lx, ly + 3, "outline"), (lx + 1, ly + 3, "metal_sh"),   (lx + 2, ly + 3, "outline")]
            # Side outlines
            p += [(lx - 1, ly + dy, "outline") for dy in range(-2, 3)]
            p += [(lx + 3, ly + dy, "outline") for dy in range(-2, 3)]
            # Inner hole
            p += [(lx + 1, ly - 1, "link_in"), (lx + 1, ly, "link_in"), (lx + 1, ly + 1, "link_in")]

    # Connecting segments between links (thin metal bars)
    for i in range(len(links) - 1):
        x0, y0, _ = links[i]
        x1, y1, _ = links[i + 1]
        # midpoint connector
        mx = (x0 + x1) // 2
        my = (y0 + y1) // 2
        p += [(mx, my, "metal"), (mx, my + 1, "metal_sh")]

    return p


def _molotov_pixels():
    """Molotov cocktail — bottle horizontal, flame tip points east."""
    p = []
    CY = 15

    # ---- Bottle body (x=4-18, oval glass bottle) ----
    for x in range(5, 18):
        spread = 4 if 7 <= x <= 15 else 3
        for dy in range(-spread, spread + 1):
            c = "glass_hl" if dy < -1 else ("glass_sh" if dy >= spread - 1 else "glass")
            p.append((x, CY + dy, c))
        p += [(x, CY - spread - 1, "outline"), (x, CY + spread + 1, "outline")]
    # Left cap
    p += [(4, CY - 2, "outline"), (4, CY - 1, "glass"), (4, CY, "glass"),
          (4, CY + 1, "glass"),   (4, CY + 2, "outline")]
    p += [(3, CY - 1, "outline"), (3, CY, "outline"), (3, CY + 1, "outline")]

    # Liquid inside (fills lower third)
    for x in range(6, 17):
        p += [(x, CY + 1, "liquid"), (x, CY + 2, "liquid_hl" if x % 2 == 0 else "liquid"),
              (x, CY + 3, "liquid")]

    # ---- Bottle neck (x=18-23, narrowing) ----
    for x in range(18, 24):
        p += [(x, CY - 2, "outline"),
              (x, CY - 1, "glass"),
              (x, CY,     "glass"),
              (x, CY + 1, "glass_sh"),
              (x, CY + 2, "outline")]

    # ---- Rag stopper (x=23-27) ----
    for x in range(23, 28):
        p += [(x, CY - 2, "outline"),
              (x, CY - 1, "rag"),
              (x, CY,     "rag"),
              (x, CY + 1, "rag_sh"),
              (x, CY + 2, "outline")]

    # ---- Flame (x=27-31) ----
    # Base of flame (wide)
    p += [(27, CY - 1, "flame"),     (27, CY, "flame"),     (27, CY + 1, "rag")]
    p += [(28, CY - 2, "flame"),     (28, CY - 1, "flame_hl"), (28, CY, "flame")]
    p += [(29, CY - 3, "flame_hl"),  (29, CY - 2, "flame"),    (29, CY - 1, "flame_tip")]
    p += [(30, CY - 3, "flame"),     (30, CY - 2, "flame_tip")]
    p += [(31, CY - 2, "flame_tip"), (31, CY - 1, "flame_tip")]
    # Flame outline/glow
    p += [(26, CY - 2, "outline"),   (26, CY - 1, "flame"),    (26, CY, "rag")]
    p += [(27, CY - 2, "outline"),   (28, CY - 3, "outline"),  (29, CY - 4, "outline")]
    p += [(30, CY - 4, "outline"),   (31, CY - 3, "outline")]

    return p


def _taser_pixels():
    """Electric stun gun (Taser) — prongs point east, grip south."""
    p = []
    CY = 14  # center y of body

    # ---- Body (x=7-24, blue housing) ----
    for x in range(7, 25):
        p += [(x, CY - 3, "outline"),
              (x, CY - 2, "body_hl"),
              (x, CY - 1, "body"),
              (x, CY,     "body"),
              (x, CY + 1, "body_sh"),
              (x, CY + 2, "outline")]
    p += [(6, y, "outline") for y in range(CY - 2, CY + 2)]

    # ---- Yellow label strip on body ----
    for x in range(12, 20):
        p += [(x, CY - 1, "prong"), (x, CY, "prong_hl")]
    p += [(11, CY - 1, "outline"), (20, CY - 1, "outline")]
    p += [(11, CY, "outline"),     (20, CY, "outline")]

    # ---- Trigger button ----
    p += [(15, CY - 3, "trigger"), (15, CY - 2, "label")]
    p += [(14, CY - 3, "outline"), (16, CY - 3, "outline")]

    # ---- Grip (x=7-11, black rubber) ----
    GX0, GX1 = 7, 11
    for y in range(CY + 2, CY + 11):
        for x in range(GX0, GX1 + 1):
            c = "grip_hl" if x == GX0 else ("grip_tx" if (x + y) % 3 == 0 else "grip")
            p.append((x, y, c))
        p += [(GX0 - 1, y, "outline"), (GX1 + 1, y, "outline")]
    p += [(x, CY + 11, "outline") for x in range(GX0 - 1, GX1 + 2)]

    # ---- Prongs (twin electric probes at front) ----
    # Upper prong (x=24-28, y=CY-2)
    for x in range(24, 29):
        c = "prong_hl" if x % 2 == 0 else "prong"
        p += [(x, CY - 2, c)]
    p += [(24, CY - 3, "outline"), (28, CY - 3, "outline")]
    p += [(24, CY - 1, "outline"), (28, CY - 1, "outline")]
    p += [(29, CY - 2, "outline")]

    # Lower prong (x=24-28, y=CY+1)
    for x in range(24, 29):
        c = "prong_hl" if x % 2 == 0 else "prong"
        p += [(x, CY + 1, c)]
    p += [(24, CY, "outline"),     (28, CY, "outline")]
    p += [(24, CY + 2, "outline"), (28, CY + 2, "outline")]
    p += [(29, CY + 1, "outline")]

    # ---- Electric arc between prong tips ----
    p += [(29, CY - 1, "arc_hl"),  (29, CY, "arc")]
    p += [(30, CY - 2, "arc"),     (30, CY - 1, "arc_hl"), (30, CY + 1, "arc_hl")]
    p += [(31, CY - 1, "arc_hl"),  (31, CY, "arc_hl")]

    return p


WEAPON_PIXELS = {
    # Fantasy / Medieval
    "sword":      _sword_pixels,
    "axe":        _axe_pixels,
    "spear":      _spear_pixels,
    "staff":      _staff_pixels,
    "bow":        _bow_pixels,
    "dagger":     _dagger_pixels,
    "mace":       _mace_pixels,
    "greatsword": _greatsword_pixels,
    # Modern / Urban
    "pistol":     _pistol_pixels,
    "shotgun":    _shotgun_pixels,
    "rifle":      _rifle_pixels,
    "bat":        _bat_pixels,
    "knife":      _knife_pixels,
    "chain":      _chain_pixels,
    "molotov":    _molotov_pixels,
    "taser":      _taser_pixels,
}

# Weapon category metadata (used by the web UI)
WEAPON_CATEGORIES = {
    "sword":      "fantasy",
    "axe":        "fantasy",
    "spear":      "fantasy",
    "staff":      "fantasy",
    "bow":        "fantasy",
    "dagger":     "fantasy",
    "mace":       "fantasy",
    "greatsword": "fantasy",
    "pistol":     "modern",
    "shotgun":    "modern",
    "rifle":      "modern",
    "bat":        "modern",
    "knife":      "modern",
    "chain":      "modern",
    "molotov":    "modern",
    "taser":      "modern",
}

# ---------------------------------------------------------------------------
# RENDERING
# ---------------------------------------------------------------------------

def _rotate_cw(pixels, fw=32, fh=32):
    """Rotate pixel positions 90° clockwise in an fw×fh frame.
    (x, y) -> (fh - 1 - y, x)
    """
    return [(fh - 1 - y, x, c) for (x, y, c) in pixels]


def render_weapon(weapon_name: str):
    """Render a 128×32 spritesheet (4 orientations: E, S, W, N)."""
    palette = WEAPON_PALETTES[weapon_name]
    pixels_e = WEAPON_PIXELS[weapon_name]()
    pixels_s = _rotate_cw(pixels_e)
    pixels_w = _rotate_cw(pixels_s)
    pixels_n = _rotate_cw(pixels_w)

    all_frames = [pixels_e, pixels_s, pixels_w, pixels_n]
    sheet = Image.new("RGBA", (FRAME_W * 4, FRAME_H), (0, 0, 0, 0))
    frames_meta = []

    for i, (pixels, orient) in enumerate(zip(all_frames, ORIENTATIONS)):
        frame = Image.new("RGBA", (FRAME_W, FRAME_H), (0, 0, 0, 0))
        drawn = set()
        for (x, y, color_key) in pixels:
            if 0 <= x < FRAME_W and 0 <= y < FRAME_H and (x, y) not in drawn:
                drawn.add((x, y))
                color = palette.get(color_key, (255, 0, 255, 255))
                frame.putpixel((x, y), color)
        sheet.paste(frame, (i * FRAME_W, 0))
        frames_meta.append({
            "name": f"{weapon_name}_{orient}",
            "x": i * FRAME_W, "y": 0,
            "width": FRAME_W, "height": FRAME_H,
        })

    return sheet, frames_meta


def build_atlas(weapon_name, image_file, frames_meta, sheet_size):
    atlas = {
        "meta": {
            "image": image_file,
            "size": {"w": sheet_size[0], "h": sheet_size[1]},
            "scale": "1",
        },
        "frames": {},
        "animations": {},
    }
    for f in frames_meta:
        atlas["frames"][f["name"]] = {
            "frame": {"x": f["x"], "y": f["y"], "w": f["width"], "h": f["height"]},
            "rotated": False, "trimmed": False,
            "spriteSourceSize": {"x": 0, "y": 0, "w": f["width"], "h": f["height"]},
            "sourceSize": {"w": f["width"], "h": f["height"]},
        }
    for orient in ORIENTATIONS:
        key = f"{weapon_name}_{orient}"
        atlas["animations"][key] = [key]
    return atlas


def build_preview_html(weapon_name, image_file):
    orients_json = json.dumps(ORIENTATIONS)
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Weapon: {weapon_name}</title>
<style>
  body {{ background:#1a1a1a; color:#eee; font-family:monospace; padding:2rem; }}
  h1 {{ color:#adf; }}
  .frames {{ display:flex; gap:2rem; flex-wrap:wrap; margin-top:1rem; }}
  .frame-wrap {{ text-align:center; }}
  canvas {{ display:block; border:1px solid #444; image-rendering:pixelated; }}
  p.lbl {{ margin:0.3rem 0 0; font-size:0.8rem; color:#aaa; }}
</style>
</head><body>
<h1>Weapon: {weapon_name}</h1>
<p>{FRAME_W*4}x{FRAME_H}px spritesheet | 4 orientations × 32px</p>
<div class="frames" id="frames"></div>
<img id="src" src="{image_file}" style="display:none">
<script>
const SCALE = 6, FW = {FRAME_W}, FH = {FRAME_H};
const ORIENTATIONS = {orients_json};
const img = document.getElementById("src");
img.onload = () => {{
  const c = document.getElementById("frames");
  ORIENTATIONS.forEach((o, i) => {{
    const w = document.createElement("div"); w.className = "frame-wrap";
    const cv = document.createElement("canvas");
    cv.width = FW*SCALE; cv.height = FH*SCALE;
    const ctx = cv.getContext("2d"); ctx.imageSmoothingEnabled = false;
    ctx.drawImage(img, i*FW, 0, FW, FH, 0, 0, FW*SCALE, FH*SCALE);
    const lbl = document.createElement("p"); lbl.className = "lbl";
    lbl.textContent = o; w.appendChild(cv); w.appendChild(lbl); c.appendChild(w);
  }});
}};
if (img.complete) img.onload();
</script>
</body></html>
"""


def _generate_weapon(weapon_name):
    image_file = f"weapon_{weapon_name}.png"
    atlas_file  = f"weapon_{weapon_name}.json"
    preview_file = f"weapon_{weapon_name}_preview.html"

    sheet, frames_meta = render_weapon(weapon_name)

    sheet_path = os.path.join(OUTPUT_DIR, image_file)
    sheet.save(sheet_path)
    print(f"  Spritesheet : {sheet_path}  ({sheet.width}x{sheet.height})")

    atlas = build_atlas(weapon_name, image_file, frames_meta, sheet.size)
    atlas_path = os.path.join(OUTPUT_DIR, atlas_file)
    with open(atlas_path, "w") as f:
        json.dump(atlas, f, indent=2)
    print(f"  Atlas       : {atlas_path}")

    preview_path = os.path.join(OUTPUT_DIR, preview_file)
    with open(preview_path, "w") as f:
        f.write(build_preview_html(weapon_name, image_file))
    print(f"  Preview     : {preview_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate weapon sprites (fantasy + modern)")
    parser.add_argument("--weapon", choices=list(WEAPON_PIXELS.keys()),
                        help="Weapon type to generate")
    parser.add_argument("--all",  action="store_true", help="Generate all weapon types")
    parser.add_argument("--list", action="store_true", help="List available weapons")
    args = parser.parse_args()

    if args.list:
        print("Available weapons:")
        for w in WEAPON_PIXELS:
            print(f"  {w}")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if args.all:
        for weapon_name in WEAPON_PIXELS:
            print(f"\nGenerating {weapon_name}...")
            _generate_weapon(weapon_name)
        print(f"\nGenerated {len(WEAPON_PIXELS)} weapons.")
        return

    if not args.weapon:
        parser.print_help()
        return

    print(f"Generating {args.weapon}...")
    _generate_weapon(args.weapon)


if __name__ == "__main__":
    main()
