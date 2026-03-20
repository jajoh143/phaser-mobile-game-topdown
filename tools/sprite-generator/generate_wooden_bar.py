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
    "top_base":      (52,  28,  12, 255),   # very dark mahogany base
    "top_mid":       (68,  38,  16, 255),   # mid-tone wood
    "top_hl":        (92,  55,  22, 255),   # warm highlight on top surface
    "top_edge_hl":   (115, 72,  30, 255),   # bright front-edge catch-light
    "top_shadow":    (32,  16,   6, 255),   # deep shadow (back of surface)

    # Wood grain lines on counter top
    "grain_dk":      (40,  20,   8, 255),   # dark grain streak
    "grain_lt":      (78,  48,  20, 255),   # light grain streak

    # Front face of bar (paneling)
    "face_base":     (44,  22,   8, 255),   # dark front-face wood
    "face_mid":      (58,  30,  12, 255),   # mid panel tone
    "face_hl":       (72,  42,  16, 255),   # panel highlight
    "face_shadow":   (28,  12,   4, 255),   # shadow in recesses

    # Trim / molding
    "trim_top":      (88,  55,  22, 255),   # top molding strip (warm)
    "trim_top_hl":   (108, 70,  30, 255),   # molding highlight
    "trim_bot":      (62,  35,  12, 255),   # bottom base trim
    "trim_bot_hl":   (80,  48,  18, 255),   # bottom trim highlight

    # Panel divider grooves
    "groove":        (22,  10,   3, 255),   # recessed groove (very dark)

    # Outlines
    "outline":       (18,   8,   2, 255),   # darkest near-black outline
    "outline_soft":  (38,  18,   8, 255),   # softer interior outline
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
# COUNTER TOP  (rows 0–31, top-down view of the bar surface)
# ---------------------------------------------------------------------------
def _counter_top_pixels():
    """
    Top 32x32: bar counter surface viewed from slightly above.

    Perspective cues:
      - Back edge (y=0) is darkest — farthest from viewer.
      - Front edge (y=31) gets the brightest highlight — nearest the viewer /
        slightly overhang lip.
      - Light source from upper-left: left columns slightly lighter.
      - Wood grain runs left-right (horizontal streaks).
    """
    p = []

    # --- Base fill: gradient from back (dark) to front (mid) ---
    # Rows 0-3: deep shadow at back wall edge
    for y in range(0, 4):
        _row(p, y, 0, 31, "top_shadow")

    # Rows 4-7: dark base transitioning
    for y in range(4, 8):
        _row(p, y, 0, 31, "top_base")

    # Rows 8-19: main surface — base with slight mid highlights
    for y in range(8, 20):
        _row(p, y, 0, 31, "top_base")
        # Left side slightly lighter (light source upper-left)
        for x in range(0, 5):
            p.append((x, y, "top_mid"))

    # Rows 20-26: warming toward front edge
    for y in range(20, 27):
        _row(p, y, 0, 31, "top_mid")
        for x in range(0, 6):
            p.append((x, y, "top_hl"))

    # Rows 27-29: bright front-lip bevel
    for y in range(27, 30):
        _row(p, y, 0, 31, "top_hl")

    # Row 30-31: brightest catch-light on the lip edge
    _row(p, 30, 0, 31, "top_edge_hl")
    _row(p, 31, 0, 31, "top_edge_hl")

    # --- Wood grain streaks (horizontal, slight irregularity) ---
    # Dark grain lines
    grain_dark_rows = [5, 10, 14, 18, 23]
    for gy in grain_dark_rows:
        # Full-width dark grain with gaps (not perfectly solid)
        for x in range(0, 32):
            if x % 7 != 3:  # small gap breaks realism
                p.append((x, gy, "grain_dk"))

    # Light grain lines (between dark ones)
    grain_light_rows = [7, 12, 16, 21, 25]
    for gy in grain_light_rows:
        for x in range(0, 32):
            if x % 9 != 5:
                p.append((x, gy, "grain_lt"))

    # --- Back edge outline ---
    _row(p, 0, 0, 31, "outline")

    # --- Left and right edge outlines (tileable sides — very subtle) ---
    _col(p, 0,  0, 31, "outline_soft")
    _col(p, 31, 0, 31, "outline_soft")

    # --- Front lip outline (between top surface and front face) ---
    _row(p, 31, 0, 31, "outline")

    return p


# ---------------------------------------------------------------------------
# FRONT FACE  (rows 32–63, the vertical front panel of the bar)
# ---------------------------------------------------------------------------
def _front_face_pixels():
    """
    Bottom 32x32: the front face of the bar viewed from slightly above.

    Features:
      - Horizontal top molding strip (rows 32-35): slightly protruding, bright
      - Recessed panel fields (two stacked panels with grooves between)
      - Vertical panel divider groove at x=15/16 (center)
      - Horizontal grooves between panels
      - Bottom base trim strip (rows 60-63)
    """
    p = []

    # Offset: all y coordinates for this section are in absolute image space
    # (y=32 is the first pixel of the front face section)
    Y0 = 32  # offset so we can write natural local coords

    def fy(local_y):
        return local_y + Y0

    # --- Full background fill ---
    _rect(p, 0, Y0, 31, Y0 + 31, "face_base")

    # --- Top molding strip (local y 0-4): protruding horizontal rail ---
    # This is the underside of the counter lip casting a shadow then bright molding
    _row(p, fy(0), 0, 31, "outline")        # shadow line from lip overhang
    _row(p, fy(1), 0, 31, "trim_top_hl")    # bright catch on molding top
    _row(p, fy(2), 0, 31, "trim_top")       # molding face
    _row(p, fy(3), 0, 31, "trim_top")
    _row(p, fy(4), 0, 31, "face_shadow")    # shadow below molding

    # --- Upper recessed panel (local y 5-18) ---
    # Panel field
    for y in range(5, 19):
        abs_y = fy(y)
        _row(p, abs_y, 1, 30, "face_mid")
        # Left panel highlight
        p.append((1, abs_y, "face_hl"))
        p.append((2, abs_y, "face_hl"))

    # Panel inset shadow edges (groove look)
    _row(p, fy(5),  1, 30, "face_shadow")   # top of panel recess
    _row(p, fy(18), 1, 30, "face_shadow")   # bottom of panel recess
    _col(p, 1,  fy(5), fy(18), "face_shadow")   # left recess shadow
    _col(p, 30, fy(5), fy(18), "groove")         # right inner groove

    # --- Center vertical groove divider (between two panel columns) ---
    _col(p, 15, fy(5),  fy(28), "groove")
    _col(p, 16, fy(5),  fy(28), "face_shadow")

    # --- Horizontal groove between upper and lower panels (local y 18-21) ---
    _row(p, fy(19), 0, 31, "groove")
    _row(p, fy(20), 0, 31, "face_shadow")
    _row(p, fy(21), 1, 30, "face_mid")

    # --- Lower recessed panel (local y 22-28) ---
    for y in range(22, 29):
        abs_y = fy(y)
        _row(p, abs_y, 1, 30, "face_mid")
        p.append((1, abs_y, "face_hl"))
        p.append((2, abs_y, "face_hl"))

    # Lower panel inset shadow
    _row(p, fy(22), 1, 30, "face_shadow")
    _row(p, fy(28), 1, 30, "face_shadow")
    _col(p, 1,  fy(22), fy(28), "face_shadow")
    _col(p, 30, fy(22), fy(28), "groove")

    # --- Bottom base trim (local y 29-31) ---
    _row(p, fy(29), 0, 31, "face_shadow")   # shadow above base trim
    _row(p, fy(30), 0, 31, "trim_bot_hl")   # base trim highlight
    _row(p, fy(31), 0, 31, "trim_bot")      # base trim base

    # --- Left/right edge outlines on front face ---
    _col(p, 0,  Y0,      Y0 + 31, "outline")
    _col(p, 31, Y0,      Y0 + 31, "outline")

    # Bottom outline
    _row(p, fy(31), 0, 31, "outline")

    return p


# ---------------------------------------------------------------------------
# GENERATE
# ---------------------------------------------------------------------------
def generate() -> Image.Image:
    """Generate and return the 32x64 wooden bar counter sprite as RGBA PIL Image."""
    img = Image.new("RGBA", (SPRITE_W, SPRITE_H), (0, 0, 0, 0))
    px = img.load()

    # Gather all pixel definitions
    all_pixels = []
    all_pixels.extend(_counter_top_pixels())
    all_pixels.extend(_front_face_pixels())

    # Draw (last write wins — later entries override earlier ones)
    # We use a dict to implement "last-write-wins" semantics for overlapping defs
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
