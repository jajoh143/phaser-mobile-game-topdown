#!/usr/bin/env python3
"""
Wooden bar counter sprite generator for Phaser 3.

Generates a single 32x64 top-down bar counter segment (portrait orientation).
The sprite is designed to tile horizontally to form a long bar counter.

Layout (top-down RPG view, slightly above):
  - Top 32x32:    Bar counter top surface (dark stained wood, grain, highlight)
  - Bottom 32x32: Front face of the bar (dark wood paneling, trim/molding)

Color palette: dark mahogany tones — very dark brown base, warm highlights,
deep shadows. Mood: dim, atmospheric bar scene.

Output:
    generated/wooden_bar.png
    generated/wooden_bar.json
    public/assets/sprites/wooden_bar.png

Usage:
    python generate_wooden_bar.py
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

SPRITE_W = 32
SPRITE_H = 64   # portrait: top half = counter top, bottom half = front face

# ---------------------------------------------------------------------------
# PALETTE  — dark mahogany bar counter
# ---------------------------------------------------------------------------
PAL = {
    # Counter top surface
    "top_shadow":    (28,  13,   5, 255),   # back-edge shadow (deepest, farthest)
    "top_base":      (48,  24,  10, 255),   # very dark mahogany base
    "top_mid":       (65,  36,  15, 255),   # mid-tone wood plank
    "top_hl":        (86,  52,  20, 255),   # warm highlight toward front
    "top_edge_hl":   (112, 70,  26, 255),   # bright catch-light on lip edge
    "top_edge_sh":   (34,  16,   6, 255),   # inner bevel shadow on lip

    # Wood grain lines on counter top
    "grain_dk":      (36,  17,   6, 255),   # dark grain streak
    "grain_lt":      (76,  46,  19, 255),   # light grain streak / wood highlight

    # Front face of bar (paneling)
    "face_shadow":   (22,   9,   3, 255),   # very deep recess shadow
    "face_base":     (42,  21,   8, 255),   # dark front-face wood base
    "face_mid":      (56,  30,  12, 255),   # mid panel tone
    "face_hl":       (70,  42,  16, 255),   # panel highlight (left-face lit)

    # Trim / molding
    "trim_top_hl":   (105, 68,  28, 255),   # top molding bright highlight
    "trim_top":      (82,  50,  20, 255),   # top molding base
    "trim_top_sh":   (52,  28,  10, 255),   # top molding underside shadow
    "trim_bot_hl":   (78,  46,  18, 255),   # bottom trim highlight
    "trim_bot":      (58,  32,  12, 255),   # bottom base trim

    # Panel grooves / recesses
    "groove":        (18,   7,   2, 255),   # deep recessed groove (near-black)
    "groove_lt":     (35,  16,   6, 255),   # groove shoulder (soft inner edge)

    # Outlines
    "outline":       (14,   5,   1, 255),   # darkest outline
    "outline_soft":  (32,  14,   5, 255),   # softer interior edge
}


# ---------------------------------------------------------------------------
# PIXEL HELPERS
# ---------------------------------------------------------------------------
def _row(pixels, y, x0, x1, color_key):
    """Fill an inclusive horizontal span with a palette color key."""
    for x in range(x0, x1 + 1):
        pixels.append((x, y, color_key))


def _col(pixels, x, y0, y1, color_key):
    """Fill an inclusive vertical span with a palette color key."""
    for y in range(y0, y1 + 1):
        pixels.append((x, y, color_key))


def _rect(pixels, x0, y0, x1, y1, color_key):
    """Fill an inclusive solid rectangle."""
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            pixels.append((x, y, color_key))


# ---------------------------------------------------------------------------
# COUNTER TOP  (rows 0-31, top-down view of the bar surface)
# ---------------------------------------------------------------------------
def _counter_top_pixels():
    """
    Top 32x32: bar counter surface viewed from slightly above.

    Perspective / shading cues:
      - Rows 0-2: deepest shadow at back wall edge (farthest from viewer).
      - Rows 3-8: dark base — receding surface.
      - Rows 9-22: main visible surface — alternating plank tones, grain lines.
      - Rows 23-28: surface brightens toward near edge (light catches the top).
      - Rows 29-31: brightest highlight on the overhanging front lip.

    Wood grain runs left-right (horizontal streaks). Three plank seams run
    vertically at x=10, x=21 (two seams = three planks across the 32px width).
    Plank seams are subtle: a single-pixel dark groove.
    """
    p = []

    # --- Background fill by depth zone ---
    # Deep back shadow
    for y in range(0, 3):
        _row(p, y, 0, 31, "top_shadow")

    # Dark base (rows 3-8)
    for y in range(3, 9):
        _row(p, y, 0, 31, "top_base")

    # Main surface (rows 9-22) — interleave base/mid for plank-band feel
    plank_sequence = [
        "top_base", "top_base", "top_mid",  "top_base",  # 9-12
        "top_mid",  "top_base", "top_base", "top_mid",   # 13-16
        "top_base", "top_mid",  "top_base", "top_base",  # 17-20
        "top_mid",  "top_base",                          # 21-22
    ]
    for i, color in enumerate(plank_sequence):
        y = 9 + i
        _row(p, y, 0, 31, color)
        # Left side catch-light (light source upper-left)
        for x in range(0, 4):
            p.append((x, y, "top_mid" if color == "top_base" else "top_hl"))

    # Warming zone toward near edge (rows 23-28)
    for y in range(23, 29):
        _row(p, y, 0, 31, "top_mid")
        for x in range(0, 6):
            p.append((x, y, "top_hl"))

    # Front bevel highlight (rows 29-30)
    _row(p, 29, 0, 31, "top_hl")
    _row(p, 30, 0, 31, "top_edge_hl")

    # Brightest lip catch-light row
    _row(p, 31, 0, 31, "top_edge_hl")

    # --- Wood grain streaks (horizontal) ---
    # Dark grain lines — long continuous streaks with small breaks
    dark_grain_defs = [
        (4,   0, 31),
        (8,   2, 22),
        (8,  25, 31),
        (11,  0, 12),
        (11, 17, 31),
        (15,  4, 28),
        (19,  0, 10),
        (19, 14, 31),
        (22,  6, 26),
    ]
    for (gy, x0, x1) in dark_grain_defs:
        for x in range(x0, x1 + 1):
            # Small gap for texture variation (avoids perfectly solid line)
            if (x + gy) % 11 != 5:
                p.append((x, gy, "grain_dk"))

    # Light grain highlight streaks
    light_grain_defs = [
        (6,   0, 18),
        (6,  24, 31),
        (10,  3, 16),
        (10, 22, 30),
        (13,  0,  8),
        (13, 12, 25),
        (17,  5, 19),
        (17, 27, 31),
        (21,  1, 14),
        (21, 20, 31),
        (24,  8, 28),
    ]
    for (gy, x0, x1) in light_grain_defs:
        for x in range(x0, x1 + 1):
            if (x + gy) % 13 != 7:
                p.append((x, gy, "grain_lt"))

    # --- Plank seam grooves (vertical, subtle) ---
    for seam_x in [10, 21]:
        for y in range(3, 30):
            p.append((seam_x, y, "grain_dk"))
        # Bright shoulder on right side of each seam
        for y in range(3, 30):
            p.append((seam_x + 1, y, "grain_lt"))

    # --- Back edge outline (hard line at the wall) ---
    _row(p, 0, 0, 31, "outline")
    _row(p, 1, 0, 31, "outline_soft")

    # --- Left/right edge outlines (very soft — these edges tile) ---
    _col(p, 0,  2, 29, "outline_soft")
    _col(p, 31, 2, 29, "outline_soft")

    # --- Front lip bevel shadow (thin inner shadow above catch-light) ---
    _row(p, 28, 0, 31, "top_edge_sh")

    # --- Bottom edge of top section (hard divide between top and face) ---
    _row(p, 31, 0, 31, "outline")

    return p


# ---------------------------------------------------------------------------
# FRONT FACE  (rows 32-63, the vertical front panel of the bar)
# ---------------------------------------------------------------------------
def _front_face_pixels():
    """
    Bottom 32x32: front face of the bar counter, viewed from slightly above.

    Visual layout (local y 0-31, absolute y = local + 32):
      y  0    : shadow line directly under lip overhang
      y  1- 3 : top molding strip (horizontal protruding rail)
      y  4    : shadow below molding
      y  5-17 : upper recessed panel field
      y 18-20 : horizontal groove/rail between upper and lower panels
      y 21-27 : lower recessed panel field
      y 28    : shadow above bottom baseboard
      y 29-30 : bottom baseboard strip
      y 31    : bottom edge outline

    Vertical dividers at x=15-16 split the face into left and right halves,
    creating two columns of stacked recessed panels — a classic bar aesthetic.
    """
    p = []
    Y0 = 32  # absolute y offset for this section

    def ay(local_y):
        """Convert local y (0-31) to absolute image y."""
        return local_y + Y0

    # --- Full background fill ---
    _rect(p, 0, Y0, 31, Y0 + 31, "face_base")

    # --- Shadow line at top (under counter lip overhang) ---
    _row(p, ay(0), 0, 31, "outline")

    # --- Top molding strip (local y 1-3) ---
    _row(p, ay(1), 0, 31, "trim_top_hl")   # bright top face of molding
    _row(p, ay(2), 0, 31, "trim_top")      # molding body
    _row(p, ay(3), 0, 31, "trim_top_sh")   # bottom/shadow face of molding

    # --- Shadow below molding (local y 4) ---
    _row(p, ay(4), 0, 31, "face_shadow")

    # --- Upper recessed panels (local y 5-17) ---
    # Background fill
    for y_l in range(5, 18):
        _row(p, ay(y_l), 1, 30, "face_mid")

    # Left column highlight (suggests light hitting from upper-left)
    for y_l in range(5, 18):
        p.append((1, ay(y_l), "face_hl"))
        p.append((2, ay(y_l), "face_hl"))

    # Panel inset shadow edges (make it look recessed)
    _row(p, ay(5),  2, 30, "face_shadow")       # top of panel inset
    _row(p, ay(17), 2, 30, "groove_lt")          # bottom highlight of panel
    _col(p, 2,  ay(6),  ay(16), "face_shadow")  # left edge shadow
    _col(p, 30, ay(6),  ay(16), "groove_lt")    # right edge light

    # Horizontal wood grain inside upper panel
    upper_panel_grain = [
        ("grain_dk",  7, 3, 13),
        ("grain_dk",  7, 18, 28),
        ("grain_lt",  8, 3, 12),
        ("grain_lt",  8, 19, 27),
        ("grain_dk", 11, 3, 10),
        ("grain_dk", 11, 21, 28),
        ("grain_lt", 13, 4, 14),
        ("grain_lt", 13, 17, 27),
        ("grain_dk", 15, 3, 12),
        ("grain_dk", 15, 20, 28),
    ]
    for (ckey, y_l, x0, x1) in upper_panel_grain:
        for x in range(x0, x1 + 1):
            p.append((x, ay(y_l), ckey))

    # --- Central vertical groove (x=15-16): splits face into two columns ---
    _col(p, 14, ay(5),  ay(27), "groove_lt")    # left shoulder of groove
    _col(p, 15, ay(5),  ay(27), "groove")       # main groove (dark)
    _col(p, 16, ay(5),  ay(27), "face_shadow")  # shadow side of groove
    _col(p, 17, ay(5),  ay(27), "face_hl")      # right lit shoulder

    # --- Horizontal groove rail between panels (local y 18-20) ---
    _row(p, ay(18), 0, 31, "groove")         # top groove line
    _row(p, ay(19), 1, 30, "face_shadow")    # shadow in groove
    _row(p, ay(20), 1, 30, "groove_lt")      # bright rail face
    # Left/right edge of rail
    for y_l in range(18, 21):
        p.append((0, ay(y_l), "outline"))
        p.append((31, ay(y_l), "outline"))

    # --- Lower recessed panels (local y 21-27) ---
    for y_l in range(21, 28):
        _row(p, ay(y_l), 1, 30, "face_mid")

    for y_l in range(21, 28):
        p.append((1, ay(y_l), "face_hl"))
        p.append((2, ay(y_l), "face_hl"))

    _row(p, ay(21), 2, 30, "face_shadow")       # panel top inset
    _row(p, ay(27), 2, 30, "groove_lt")          # panel bottom highlight
    _col(p, 2,  ay(22), ay(26), "face_shadow")
    _col(p, 30, ay(22), ay(26), "groove_lt")

    # Horizontal grain inside lower panel
    lower_panel_grain = [
        ("grain_dk", 23, 3, 12),
        ("grain_dk", 23, 18, 28),
        ("grain_lt", 24, 3, 10),
        ("grain_lt", 24, 20, 27),
        ("grain_dk", 26, 4, 14),
        ("grain_dk", 26, 17, 27),
    ]
    for (ckey, y_l, x0, x1) in lower_panel_grain:
        for x in range(x0, x1 + 1):
            p.append((x, ay(y_l), ckey))

    # --- Shadow above bottom baseboard (local y 28) ---
    _row(p, ay(28), 0, 31, "face_shadow")

    # --- Bottom baseboard strip (local y 29-30) ---
    _row(p, ay(29), 0, 31, "trim_bot_hl")   # bright top of baseboard
    _row(p, ay(30), 0, 31, "trim_bot")      # baseboard body

    # --- Bottom edge outline ---
    _row(p, ay(31), 0, 31, "outline")

    # --- Left/right edge outlines on front face ---
    _col(p, 0,  Y0, Y0 + 31, "outline")
    _col(p, 31, Y0, Y0 + 31, "outline")

    return p


# ---------------------------------------------------------------------------
# GENERATE
# ---------------------------------------------------------------------------
def generate() -> Image.Image:
    """Generate and return the 32x64 wooden bar counter sprite as RGBA PIL Image."""
    img = Image.new("RGBA", (SPRITE_W, SPRITE_H), (0, 0, 0, 0))
    px = img.load()

    # Collect all pixel definitions
    all_pixels = []
    all_pixels.extend(_counter_top_pixels())
    all_pixels.extend(_front_face_pixels())

    # Composite: use dict so later entries override earlier ones (last-write-wins)
    canvas = {}
    for (x, y, color_key) in all_pixels:
        if 0 <= x < SPRITE_W and 0 <= y < SPRITE_H:
            canvas[(x, y)] = PAL.get(color_key, (255, 0, 255, 255))

    for (x, y), color in canvas.items():
        px[x, y] = color

    return img


# ---------------------------------------------------------------------------
# ATLAS / JSON
# ---------------------------------------------------------------------------
def build_atlas(image_file: str) -> dict:
    """Return a Phaser-compatible JSON texture atlas for the bar counter sprite."""
    return {
        "meta": {
            "image": image_file,
            "size": {"w": SPRITE_W, "h": SPRITE_H},
            "scale": "1",
        },
        "frames": {
            "wooden_bar": {
                "frame":            {"x": 0, "y": 0, "w": SPRITE_W, "h": SPRITE_H},
                "rotated":          False,
                "trimmed":          False,
                "spriteSourceSize": {"x": 0, "y": 0, "w": SPRITE_W, "h": SPRITE_H},
                "sourceSize":       {"w": SPRITE_W, "h": SPRITE_H},
            },
        },
        "animations": {
            "wooden_bar": ["wooden_bar"],
        },
    }


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(PUBLIC_DIR, exist_ok=True)

    image_file = "wooden_bar.png"
    atlas_file = "wooden_bar.json"

    # Generate sprite
    sprite = generate()

    # Save to generated/
    out_png = os.path.join(OUTPUT_DIR, image_file)
    sprite.save(out_png)
    print(f"  Sprite      : {out_png}  ({sprite.width}x{sprite.height})")

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
