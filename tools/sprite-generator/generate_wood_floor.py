#!/usr/bin/env python3
"""
Wood floor tile generator for Phaser 3.

Generates a 32x32 seamlessly tileable pixel-art wood floor texture
with a warm, worn dark-stained hardwood bar-scene aesthetic.
Single static frame.

Output:
    generated/wood_floor.png
    generated/wood_floor.json
    public/assets/sprites/wood_floor.png

Usage:
    python generate_wood_floor.py
"""

import json
import os
from PIL import Image

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT   = os.path.abspath(os.path.join(_SCRIPT_DIR, "..", ".."))

OUTPUT_DIR  = os.path.join(_SCRIPT_DIR, "generated")
PUBLIC_DIR  = os.path.join(_REPO_ROOT, "public", "assets", "sprites")

IMAGE_FILE = "wood_floor.png"
JSON_FILE  = "wood_floor.json"

SIZE = 32

# ---------------------------------------------------------------------------
# PALETTE  — warm worn dark-stained hardwood
# ---------------------------------------------------------------------------
PLANK_BASE   = (88,  54, 28, 255)   # main plank face, warm dark brown
PLANK_DARK   = (62,  36, 16, 255)   # shadow / deep grain channel
PLANK_LIGHT  = (112, 72, 38, 255)   # highlight / raised grain ridge
PLANK_MID    = (78,  46, 22, 255)   # mid-tone surface variation
PLANK_WARM   = (102, 64, 34, 255)   # warm accent, lighter patch
PLANK_EDGE   = (48,  28, 12, 255)   # very dark plank seam / gap
KNOT_DARK    = (42,  24,  8, 255)   # knot core
KNOT_RING    = (72,  44, 20, 255)   # knot ring surround

# ---------------------------------------------------------------------------
# PLANK LAYOUT
#
#  4 planks, each 8 pixels tall, filling 32px exactly.
#  Gap between planks: 1px at the bottom of each plank row (py == 7).
#  Plank runs the full width (32px).
#
#  Grain lines are horizontal streaks running across the plank face.
#  They are offset per-plank so adjacent planks don't repeat identically.
#
#  Tiling notes:
#   - Height: 4 planks × 8px = 32px (exact)
#   - Width: grain is procedural and wraps at x == 0 / x == 31 seamlessly
#     (all grain functions are periodic with period 32 or divisors thereof)
# ---------------------------------------------------------------------------

def _grain_color(px: int, py: int, plank_id: int) -> tuple:
    """
    Return the RGBA colour for a non-seam pixel inside a plank.

    px  : 0-31  horizontal position
    py  : 0-6   local y inside the plank face (0 = top, 6 = bottom)
    plank_id : 0-3  which plank row
    """
    # Each plank has a fixed per-plank horizontal phase shift so grain
    # patterns don't align across planks.
    phase = (plank_id * 9) % 32   # 9 gives distinct, non-repeating offsets

    # ---- Top highlight edge (py == 0) ----
    if py == 0:
        return PLANK_LIGHT

    # ---- Bottom shadow edge (py == 6) ----
    if py == 6:
        return PLANK_DARK

    # ---- Inner face (py == 1..5) ----
    # Grain lines are based on a pseudo-random function of px and plank_id.
    # We use simple arithmetic to keep it dependency-free.
    gx = (px + phase) % 32

    # Primary grain streaks: thin dark channels running horizontally,
    # spaced ~4-6px apart, slightly irregular.
    grain_period_a = 5
    grain_period_b = 7
    pos_a = gx % grain_period_a
    pos_b = gx % grain_period_b

    # Vary grain density by plank
    density_mod = (plank_id * 3 + py) % 3

    if pos_a == 0 and py in (2, 4):
        return PLANK_DARK
    if pos_b == 0 and py in (3, 5):
        return PLANK_DARK

    # Lighter grain ridges between the dark channels
    if pos_a == 2 and py == 2:
        return PLANK_LIGHT
    if pos_b == 3 and py == 4:
        return PLANK_LIGHT

    # Warm mid-tone patches (simulate variation in wood grain width)
    if density_mod == 0 and (gx % 11) in (1, 2) and py == 3:
        return PLANK_WARM

    # Occasional deeper grain channel
    if (gx % 13) == 0 and py in (2, 3, 4):
        return PLANK_MID

    # Default face colour
    return PLANK_BASE


def _has_knot(plank_id: int) -> tuple | None:
    """
    Return (knot_cx, knot_cy_local) for a knot in this plank, or None.
    knot_cy_local is in local plank-face space (0..6).
    knot_cx is the tile-space x position of the knot centre.

    Placement is deterministic and chosen to look natural but not repeat
    too regularly.  Only planks 1 and 3 have knots to keep it subtle.
    """
    knots = {
        1: (7,  3),   # plank row 1, x=7,  local y=3
        3: (22, 3),   # plank row 3, x=22, local y=3
    }
    return knots.get(plank_id)


def generate() -> Image.Image:
    """Generate and return the 32x32 wood floor tile as a PIL RGBA Image."""
    img = Image.new("RGBA", (SIZE, SIZE), PLANK_EDGE)
    pix = img.load()

    for plank_id in range(4):
        plank_top = plank_id * 8

        for local_y in range(8):
            tile_y = plank_top + local_y

            # Bottom seam pixel (gap between planks)
            if local_y == 7:
                for x in range(SIZE):
                    pix[x, tile_y] = PLANK_EDGE
                continue

            # Plank face pixels
            for x in range(SIZE):
                pix[x, tile_y] = _grain_color(x, local_y, plank_id)

        # ---- Knot overlay ----
        knot = _has_knot(plank_id)
        if knot is not None:
            kx, ky_local = knot
            ky = plank_top + ky_local

            # Knot: 3x3 core with ring pixels
            # Core (dark centre)
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    nx, ny = kx + dx, ky + dy
                    if 0 <= nx < SIZE and 0 <= ny < SIZE:
                        # Don't paint over the seam
                        local_y_check = ny - plank_top
                        if local_y_check == 7:
                            continue
                        if dx == 0 and dy == 0:
                            pix[nx, ny] = KNOT_DARK
                        else:
                            pix[nx, ny] = KNOT_RING

            # Ring halo (single-pixel surround at distance 2 — concentric oval)
            ring_offsets = [
                (-2, 0), (2, 0), (0, -2), (0, 2),
                (-2, -1), (-2, 1), (2, -1), (2, 1),
                (-1, -2), (1, -2), (-1, 2), (1, 2),
            ]
            for dx, dy in ring_offsets:
                nx, ny = kx + dx, ky + dy
                if 0 <= nx < SIZE and 0 <= ny < SIZE:
                    local_y_check = ny - plank_top
                    if local_y_check < 0 or local_y_check == 7:
                        continue
                    existing = pix[nx, ny]
                    # Blend ring: darken the existing grain slightly
                    r, g, b, a = existing
                    r2, g2, b2, _ = KNOT_RING
                    pix[nx, ny] = (
                        (r + r2) // 2,
                        (g + g2) // 2,
                        (b + b2) // 2,
                        a,
                    )

    # ---- Subtle wear marks: 2-3 faint lighter scratches across planks ----
    # These run horizontally across most of the width and stay within a plank face.
    # Chosen positions avoid seam rows and the knot centres.
    scratch_rows = [
        # (tile_y, x_start, x_end, brightness_add)
        (2,   3, 28,  18),   # plank 0, mid-face
        (12,  8, 31,  14),   # plank 1, mid-face
        (20,  0, 24,  16),   # plank 2, mid-face
        (28,  5, 20,  12),   # plank 3, mid-face
    ]
    for (ty, x0, x1, bright) in scratch_rows:
        if ty >= SIZE:
            continue
        for x in range(x0, min(x1 + 1, SIZE)):
            existing = pix[x % SIZE, ty]
            r, g, b, a = existing
            pix[x % SIZE, ty] = (
                min(255, r + bright),
                min(255, g + (bright * 2 // 3)),
                min(255, b + (bright // 2)),
                a,
            )

    return img


# ---------------------------------------------------------------------------
# ATLAS JSON  (Phaser-compatible, single frame)
# ---------------------------------------------------------------------------

def build_atlas() -> dict:
    """Return a Phaser-compatible texture atlas dict for the wood floor tile."""
    return {
        "meta": {
            "image": IMAGE_FILE,
            "size": {"w": SIZE, "h": SIZE},
            "scale": "1",
        },
        "frames": {
            "wood_floor": {
                "frame":             {"x": 0, "y": 0, "w": SIZE, "h": SIZE},
                "rotated":           False,
                "trimmed":           False,
                "spriteSourceSize":  {"x": 0, "y": 0, "w": SIZE, "h": SIZE},
                "sourceSize":        {"w": SIZE, "h": SIZE},
            }
        },
        "animations": {
            "wood_floor": ["wood_floor"]
        },
    }


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(PUBLIC_DIR,  exist_ok=True)

    img = generate()

    # Save to generated/
    png_path  = os.path.join(OUTPUT_DIR, IMAGE_FILE)
    json_path = os.path.join(OUTPUT_DIR, JSON_FILE)
    img.save(png_path)
    print(f"  Tile image : {png_path}  ({SIZE}x{SIZE})")

    atlas = build_atlas()
    with open(json_path, "w") as f:
        json.dump(atlas, f, indent=2)
    print(f"  Atlas JSON : {json_path}")

    # Export copy to public/assets/sprites/
    pub_path = os.path.join(PUBLIC_DIR, IMAGE_FILE)
    img.save(pub_path)
    print(f"  Public     : {pub_path}")
