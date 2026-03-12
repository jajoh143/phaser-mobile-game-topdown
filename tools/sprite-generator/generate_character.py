#!/usr/bin/env python3
"""
Top-down humanoid character sprite generator for Phaser 3.

Generates a 16x16 walk cycle spritesheet (4 directions x 4 frames)
with JSON texture atlas and browser preview.

Usage:
    python generate_character.py --palette real --name player
    python generate_character.py --palette fantasy --name player
"""

import argparse
import json
import os
from PIL import Image, ImageDraw

# ---------------------------------------------------------------------------
# OUTPUT CONFIG
# ---------------------------------------------------------------------------
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "generated")
FRAME_W = 16
FRAME_H = 16
PADDING = 0  # px between frames in the spritesheet

# Directions in spritesheet row order
DIRECTIONS = ["down", "left", "right", "up"]
FRAMES_PER_DIR = 4

# ---------------------------------------------------------------------------
# PALETTES
# Each palette is a dict mapping semantic body-part keys to RGBA tuples.
# Swap palettes via --palette without touching any drawing logic.
# ---------------------------------------------------------------------------
PALETTES = {
    "real": {
        "name": "Real-World Chicago",
        "skin": (210, 180, 150, 255),       # warm beige
        "hair": (60, 45, 30, 255),           # dark brown
        "shirt": (100, 115, 130, 255),       # slate blue-gray
        "pants": (65, 65, 75, 255),          # dark charcoal
        "shoes": (50, 42, 38, 255),          # dark leather
        "outline": (35, 30, 28, 255),        # near-black
        "eye": (30, 30, 30, 255),            # black
    },
    "fantasy": {
        "name": "Fantasy / Alternate",
        "skin": (190, 210, 230, 255),        # pale icy blue
        "hair": (180, 130, 255, 255),        # lavender-purple
        "shirt": (40, 160, 160, 255),        # deep teal
        "pants": (55, 45, 90, 255),          # dark purple
        "shoes": (200, 170, 60, 255),        # burnished gold
        "outline": (20, 15, 40, 255),        # deep indigo-black
        "eye": (255, 200, 50, 255),          # glowing gold
    },
}

# ---------------------------------------------------------------------------
# BODY PART DEFINITIONS
# Each body part has a *base* rect (x, y, w, h) relative to a 16x16 frame.
# These are the defaults; animation frames apply per-frame offsets on top.
# All values are in pixels. (0,0) is top-left of the frame.
# ---------------------------------------------------------------------------
BODY_PARTS = {
    # part_name: { "rect": (x, y, w, h), "color_key": <palette key> }
    "head":  {"rect": (5, 1, 6, 5), "color_key": "skin"},
    "hair":  {"rect": (5, 0, 6, 3), "color_key": "hair"},
    "eye_l": {"rect": (6, 3, 1, 1), "color_key": "eye"},
    "eye_r": {"rect": (9, 3, 1, 1), "color_key": "eye"},
    "torso": {"rect": (5, 6, 6, 4), "color_key": "shirt"},
    "arm_l": {"rect": (3, 6, 2, 4), "color_key": "shirt"},
    "arm_r": {"rect": (11, 6, 2, 4), "color_key": "shirt"},
    "leg_l": {"rect": (5, 10, 3, 3), "color_key": "pants"},
    "leg_r": {"rect": (8, 10, 3, 3), "color_key": "pants"},
    "foot_l": {"rect": (5, 13, 3, 2), "color_key": "shoes"},
    "foot_r": {"rect": (8, 13, 3, 2), "color_key": "shoes"},
}

# ---------------------------------------------------------------------------
# ANIMATION FRAME DATA
#
# Structure: ANIM_FRAMES[direction][frame_index] = dict of per-part offsets.
# Each entry is { "part_name": (dx, dy) } — pixel offset from that part's
# base rect position for this specific frame.
#
# Parts not listed in a frame use (0, 0) offset (rest position).
# This is where ALL spatial/animation reasoning lives.
# ---------------------------------------------------------------------------

# fmt: off
ANIM_FRAMES = {
    # ------------------------------------------------------------------
    # DOWN  — character faces the camera
    # ------------------------------------------------------------------
    "down": [
        # Frame 0 — neutral standing
        {},
        # Frame 1 — left step: left leg forward, right arm forward, slight bob
        {
            "leg_l": (0, 1), "foot_l": (0, 1),
            "leg_r": (0, -1), "foot_r": (0, -1),
            "arm_l": (0, -1), "arm_r": (0, 1),
            "head": (0, -1), "hair": (0, -1),
            "eye_l": (0, -1), "eye_r": (0, -1),
        },
        # Frame 2 — neutral (passing)
        {},
        # Frame 3 — right step: mirror of frame 1
        {
            "leg_r": (0, 1), "foot_r": (0, 1),
            "leg_l": (0, -1), "foot_l": (0, -1),
            "arm_r": (0, -1), "arm_l": (0, 1),
            "head": (0, -1), "hair": (0, -1),
            "eye_l": (0, -1), "eye_r": (0, -1),
        },
    ],

    # ------------------------------------------------------------------
    # UP  — character faces away
    # ------------------------------------------------------------------
    "up": [
        {},
        {
            "leg_l": (0, 1), "foot_l": (0, 1),
            "leg_r": (0, -1), "foot_r": (0, -1),
            "arm_l": (0, -1), "arm_r": (0, 1),
            "head": (0, -1), "hair": (0, -1),
        },
        {},
        {
            "leg_r": (0, 1), "foot_r": (0, 1),
            "leg_l": (0, -1), "foot_l": (0, -1),
            "arm_r": (0, -1), "arm_l": (0, 1),
            "head": (0, -1), "hair": (0, -1),
        },
    ],

    # ------------------------------------------------------------------
    # LEFT  — character faces left
    # Body parts shift to show side profile
    # ------------------------------------------------------------------
    "left": [
        # Frame 0 — standing left
        {
            "arm_r": (-3, 0),  # hidden behind torso
            "eye_r": (-2, 0),  # hidden
            "leg_r": (-2, 0),
            "foot_r": (-2, 0),
        },
        # Frame 1 — left step
        {
            "arm_r": (-3, 0),
            "eye_r": (-2, 0),
            "leg_l": (0, 1), "foot_l": (0, 1),
            "leg_r": (-2, -1), "foot_r": (-2, -1),
            "arm_l": (0, 1), "arm_r": (-3, -1),
            "head": (0, -1), "hair": (0, -1),
            "eye_l": (0, -1),
        },
        # Frame 2 — passing
        {
            "arm_r": (-3, 0),
            "eye_r": (-2, 0),
            "leg_r": (-2, 0),
            "foot_r": (-2, 0),
        },
        # Frame 3 — right step
        {
            "arm_r": (-3, 0),
            "eye_r": (-2, 0),
            "leg_r": (-2, 1), "foot_r": (-2, 1),
            "leg_l": (0, -1), "foot_l": (0, -1),
            "arm_r": (-3, 1), "arm_l": (0, -1),
            "head": (0, -1), "hair": (0, -1),
            "eye_l": (0, -1),
        },
    ],

    # ------------------------------------------------------------------
    # RIGHT — character faces right (mirror of left)
    # ------------------------------------------------------------------
    "right": [
        {
            "arm_l": (3, 0),
            "eye_l": (2, 0),
            "leg_l": (2, 0),
            "foot_l": (2, 0),
        },
        {
            "arm_l": (3, 0),
            "eye_l": (2, 0),
            "leg_r": (0, 1), "foot_r": (0, 1),
            "leg_l": (2, -1), "foot_l": (2, -1),
            "arm_r": (0, 1), "arm_l": (3, -1),
            "head": (0, -1), "hair": (0, -1),
            "eye_r": (0, -1),
        },
        {
            "arm_l": (3, 0),
            "eye_l": (2, 0),
            "leg_l": (2, 0),
            "foot_l": (2, 0),
        },
        {
            "arm_l": (3, 0),
            "eye_l": (2, 0),
            "leg_l": (2, 1), "foot_l": (2, 1),
            "leg_r": (0, -1), "foot_r": (0, -1),
            "arm_l": (3, 1), "arm_r": (0, -1),
            "head": (0, -1), "hair": (0, -1),
            "eye_r": (0, -1),
        },
    ],
}
# fmt: on

# Draw order per direction — controls which parts render on top.
# Later entries are drawn on top of earlier ones.
DRAW_ORDER = {
    "down":  ["leg_l", "leg_r", "foot_l", "foot_r", "arm_l", "torso", "arm_r", "head", "hair", "eye_l", "eye_r"],
    "up":    ["leg_l", "leg_r", "foot_l", "foot_r", "arm_l", "torso", "arm_r", "hair", "head"],
    "left":  ["arm_r", "leg_r", "foot_r", "leg_l", "foot_l", "torso", "arm_l", "head", "hair", "eye_l"],
    "right": ["arm_l", "leg_l", "foot_l", "leg_r", "foot_r", "torso", "arm_r", "head", "hair", "eye_r"],
}

# Parts to skip per direction (e.g., no eyes when facing away)
HIDDEN_PARTS = {
    "down":  [],
    "up":    ["eye_l", "eye_r"],
    "left":  ["eye_r"],
    "right": ["eye_l"],
}


# ---------------------------------------------------------------------------
# RENDERING
# ---------------------------------------------------------------------------

def render_frame(direction: str, frame_idx: int, palette: dict) -> Image.Image:
    """Render a single 16x16 frame for the given direction and frame index."""
    img = Image.new("RGBA", (FRAME_W, FRAME_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    offsets = ANIM_FRAMES[direction][frame_idx]
    hidden = HIDDEN_PARTS[direction]
    order = DRAW_ORDER[direction]

    for part_name in order:
        if part_name in hidden:
            continue

        part = BODY_PARTS[part_name]
        bx, by, bw, bh = part["rect"]
        dx, dy = offsets.get(part_name, (0, 0))

        x = bx + dx
        y = by + dy
        color = palette[part["color_key"]]

        draw.rectangle([x, y, x + bw - 1, y + bh - 1], fill=color)

    return img


def build_spritesheet(palette: dict) -> tuple[Image.Image, dict]:
    """
    Build the full spritesheet and return (image, atlas_data).

    Layout: one row per direction, FRAMES_PER_DIR columns.
    """
    cols = FRAMES_PER_DIR
    rows = len(DIRECTIONS)
    sheet_w = cols * (FRAME_W + PADDING) - PADDING
    sheet_h = rows * (FRAME_H + PADDING) - PADDING

    sheet = Image.new("RGBA", (sheet_w, sheet_h), (0, 0, 0, 0))
    frames_meta: dict = {}

    for row, direction in enumerate(DIRECTIONS):
        for col in range(FRAMES_PER_DIR):
            frame_img = render_frame(direction, col, palette)
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
    """Build a Phaser-compatible JSON texture atlas (TexturePacker format)."""
    return {
        "frames": frames_meta,
        "meta": {
            "app": "sprite-generator",
            "version": "1.0",
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
<p class="info">Generated spritesheet preview</p>

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
    parser = argparse.ArgumentParser(description="Generate a top-down character spritesheet.")
    parser.add_argument("--palette", choices=list(PALETTES.keys()), default="real",
                        help="Color palette to use (default: real)")
    parser.add_argument("--name", default="player",
                        help="Sprite name used in filenames and atlas keys (default: player)")
    args = parser.parse_args()

    palette = PALETTES[args.palette]
    sprite_name = args.name

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Build
    sheet_img, frames_meta = build_spritesheet(palette)

    image_file = f"{sprite_name}_{args.palette}.png"
    atlas_file = f"{sprite_name}_{args.palette}.json"
    preview_file = f"{sprite_name}_{args.palette}_preview.html"

    # Save spritesheet
    sheet_path = os.path.join(OUTPUT_DIR, image_file)
    sheet_img.save(sheet_path)
    print(f"  Spritesheet: {sheet_path}  ({sheet_img.width}x{sheet_img.height})")

    # Save atlas JSON
    atlas = build_atlas(sprite_name, image_file, frames_meta, sheet_img.size)
    atlas_path = os.path.join(OUTPUT_DIR, atlas_file)
    with open(atlas_path, "w") as f:
        json.dump(atlas, f, indent=2)
    print(f"  Atlas:       {atlas_path}")

    # Save preview HTML
    preview_path = os.path.join(OUTPUT_DIR, preview_file)
    with open(preview_path, "w") as f:
        f.write(build_preview_html(sprite_name, image_file, atlas_file))
    print(f"  Preview:     {preview_path}")

    # Summary
    total_frames = len(DIRECTIONS) * FRAMES_PER_DIR
    print(f"\n  Palette:     {palette['name']}")
    print(f"  Frames:      {total_frames} ({len(DIRECTIONS)} dirs x {FRAMES_PER_DIR} frames)")
    print(f"  Frame size:  {FRAME_W}x{FRAME_H}px")
    print(f"  Done!")


if __name__ == "__main__":
    main()
