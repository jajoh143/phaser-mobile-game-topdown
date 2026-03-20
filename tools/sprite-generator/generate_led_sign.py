#!/usr/bin/env python3
"""
LED rainbow sign generator for Phaser 3.

Generates a 128×32 pixel-art LED sign sprite with the text "BAR" rendered
in a dot-matrix font against a dark cabinet, lit in a sweeping left-to-right
rainbow gradient.  The surrounding frame has a brushed-metal look with
corner screws.

Output:
    generated/led_sign.png
    generated/led_sign.json
    public/assets/sprites/led_sign.png

Usage:
    python generate_led_sign.py
"""

import json
import os
import math
from PIL import Image

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT   = os.path.abspath(os.path.join(_SCRIPT_DIR, "..", ".."))

OUTPUT_DIR  = os.path.join(_SCRIPT_DIR, "generated")
PUBLIC_DIR  = os.path.join(_REPO_ROOT, "public", "assets", "sprites")

IMAGE_FILE = "led_sign.png"
JSON_FILE  = "led_sign.json"

W = 128
H = 32

# ---------------------------------------------------------------------------
# PALETTE
# ---------------------------------------------------------------------------
CABINET     = (18,  16, 22, 255)   # outer cabinet / background
BEZEL       = (38,  34, 46, 255)   # inner bezel around LED grid
METAL_DARK  = (28,  26, 34, 255)
METAL_MID   = (52,  48, 62, 255)
METAL_LIGHT = (72,  68, 86, 255)
SCREW       = (80,  76, 96, 255)
LED_OFF     = (28,  24, 32, 255)   # unlit LED dot
LED_GLOW_R  = 12                   # extra radius brightness for lit LEDs (added to base)

# ---------------------------------------------------------------------------
# DOT-MATRIX FONT  (5-wide × 7-tall, each char as list of 5 column bitmasks)
# Bitmask bit 0 = top row, bit 6 = bottom row.
# ---------------------------------------------------------------------------
FONT: dict[str, list[int]] = {
    'B': [0b1111110, 0b1001001, 0b1001001, 0b1001001, 0b0110110],
    'A': [0b0111111, 0b1001000, 0b1001000, 0b1001000, 0b0111111],
    'R': [0b1111111, 0b1001000, 0b1001100, 0b1001010, 0b0110001],
}

TEXT = "BAR"
CHAR_W = 5
CHAR_H = 7
CHAR_GAP = 2        # pixels between characters
TEXT_SCALE = 2      # each dot is 2×2 pixels

# The LED grid sits inside a 2-px bezel that's inside a 2-px metal frame.
FRAME_PX = 2
BEZEL_PX = 2
INNER_X = FRAME_PX + BEZEL_PX   # x where LED area starts
INNER_Y = FRAME_PX + BEZEL_PX

LED_AREA_W = W - 2 * INNER_X
LED_AREA_H = H - 2 * INNER_Y

# Total text width in LED-scale pixels
TEXT_TOTAL_W = len(TEXT) * CHAR_W * TEXT_SCALE + (len(TEXT) - 1) * CHAR_GAP * TEXT_SCALE
TEXT_TOTAL_H = CHAR_H * TEXT_SCALE

# Top-left corner of the text block within LED area (centred)
TEXT_X0 = INNER_X + (LED_AREA_W - TEXT_TOTAL_W) // 2
TEXT_Y0 = INNER_Y + (LED_AREA_H - TEXT_TOTAL_H) // 2


def _rainbow_color(x: int, total_w: int, brightness: float = 1.0) -> tuple:
    """
    Return an RGBA colour for a horizontal position x across total_w pixels,
    cycling through the full rainbow hue spectrum.
    brightness ∈ [0, 1].
    """
    hue = x / max(total_w - 1, 1)  # 0.0 → 1.0
    # Convert hue to RGB (simplified HSV with S=1, V=brightness)
    h6 = hue * 6.0
    i = int(h6) % 6
    f = h6 - int(h6)
    v = brightness
    p = 0.0
    q = v * (1 - f)
    t = v * f

    if   i == 0: r, g, b = v, t, p
    elif i == 1: r, g, b = q, v, p
    elif i == 2: r, g, b = p, v, t
    elif i == 3: r, g, b = p, q, v
    elif i == 4: r, g, b = t, p, v
    else:        r, g, b = v, p, q

    return (int(r * 255), int(g * 255), int(b * 255), 255)


def _build_lit_set() -> set[tuple[int, int]]:
    """Return the set of (px, py) pixel coordinates that should be lit."""
    lit: set[tuple[int, int]] = set()

    for ci, ch in enumerate(TEXT):
        col_masks = FONT.get(ch)
        if col_masks is None:
            continue
        char_pixel_x = TEXT_X0 + ci * (CHAR_W + CHAR_GAP) * TEXT_SCALE

        for col_idx, mask in enumerate(col_masks):
            for row_idx in range(CHAR_H):
                if mask & (1 << row_idx):
                    # Scale 2×: each logical dot = TEXT_SCALE × TEXT_SCALE pixels
                    for sy in range(TEXT_SCALE):
                        for sx in range(TEXT_SCALE):
                            px = char_pixel_x + col_idx * TEXT_SCALE + sx
                            py = TEXT_Y0 + row_idx * TEXT_SCALE + sy
                            lit.add((px, py))
    return lit


def generate() -> Image.Image:
    img = Image.new("RGBA", (W, H), CABINET)
    pix = img.load()

    # ---- Metal frame border ------------------------------------------------
    for y in range(H):
        for x in range(W):
            on_frame = (x < FRAME_PX or x >= W - FRAME_PX or
                        y < FRAME_PX or y >= H - FRAME_PX)
            if on_frame:
                # Simple gradient: top-left lighter, bottom-right darker
                if x < FRAME_PX or y < FRAME_PX:
                    pix[x, y] = METAL_LIGHT
                else:
                    pix[x, y] = METAL_DARK

    # ---- Bezel inside frame ------------------------------------------------
    for y in range(FRAME_PX, H - FRAME_PX):
        for x in range(FRAME_PX, W - FRAME_PX):
            on_bezel = (x < INNER_X or x >= W - INNER_X or
                        y < INNER_Y or y >= H - INNER_Y)
            if on_bezel:
                pix[x, y] = BEZEL

    # ---- LED grid background (unlit dots) ----------------------------------
    # We draw a dot every 2 pixels within the inner area (dot pitch = 2px)
    for y in range(INNER_Y, H - INNER_Y):
        for x in range(INNER_X, W - INNER_X):
            pix[x, y] = LED_OFF

    # ---- Lit LEDs with rainbow colour --------------------------------------
    lit_set = _build_lit_set()
    for (px, py) in lit_set:
        if 0 <= px < W and 0 <= py < H:
            # x position relative to text block for hue mapping
            hue_x = px - TEXT_X0
            base_col = _rainbow_color(hue_x, TEXT_TOTAL_W, brightness=1.0)
            pix[px, py] = base_col

    # ---- Glow halo: one pixel surround around each lit LED, dimmer ---------
    for (px, py) in lit_set:
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = px + dx, py + dy
            if (nx, ny) in lit_set:
                continue
            if not (INNER_X <= nx < W - INNER_X and INNER_Y <= ny < H - INNER_Y):
                continue
            hue_x = px - TEXT_X0
            glow_col = _rainbow_color(hue_x, TEXT_TOTAL_W, brightness=0.35)
            # Blend with existing (may already have a glow from a neighbour)
            existing = pix[nx, ny]
            r = min(255, existing[0] + glow_col[0])
            g = min(255, existing[1] + glow_col[1])
            b = min(255, existing[2] + glow_col[2])
            pix[nx, ny] = (r, g, b, 255)

    # ---- Corner screws -----------------------------------------------------
    screw_positions = [
        (1, 1), (W - 2, 1), (1, H - 2), (W - 2, H - 2)
    ]
    for sx, sy in screw_positions:
        if 0 <= sx < W and 0 <= sy < H:
            pix[sx, sy] = SCREW
            # Cross notch on screw head
            for dd in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = sx + dd[0], sy + dd[1]
                if 0 <= nx < W and 0 <= ny < H:
                    pix[nx, ny] = METAL_MID

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
            "led_sign": {
                "frame":            {"x": 0, "y": 0, "w": W, "h": H},
                "rotated":          False,
                "trimmed":          False,
                "spriteSourceSize": {"x": 0, "y": 0, "w": W, "h": H},
                "sourceSize":       {"w": W, "h": H},
            }
        },
        "animations": {
            "led_sign": ["led_sign"]
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
    print(f"  Sign image : {png_path}  ({W}x{H})")

    atlas = build_atlas()
    with open(json_path, "w") as f:
        json.dump(atlas, f, indent=2)
    print(f"  Atlas JSON : {json_path}")

    pub_path = os.path.join(PUBLIC_DIR, IMAGE_FILE)
    img.save(pub_path)
    print(f"  Public     : {pub_path}")
