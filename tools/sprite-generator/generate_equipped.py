#!/usr/bin/env python3
"""
Equipped character compositor for Phaser 3.

Composites a character spritesheet with a weapon sprite to produce an
"equipped" spritesheet that includes:
  - All original character animations (walk, jump, crouch, interact) unchanged
  - A "slash" animation set with the weapon overlaid on the character's hand

The weapon is positioned relative to the character's "weapon hand" pivot, which
shifts per-frame to follow the arm pose during the slash animation.

Output:
  generated/equipped/<char_name>_with_<weapon>_preset<N>.png   — spritesheet
  generated/equipped/<char_name>_with_<weapon>_preset<N>.json  — Phaser atlas
  generated/equipped/<char_name>_with_<weapon>_preset<N>_preview.html

Usage:
    python generate_equipped.py --preset 0 --weapon sword
    python generate_equipped.py --preset 2 --weapon greatsword --name hero
    python generate_equipped.py --all-weapons --preset 0
"""

import argparse
import json
import os
import sys
from PIL import Image

# Ensure the script directory is on the path so sibling modules are importable
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

import generate_character as _gc
import generate_weapon    as _gw

# Paths
CHAR_DIR     = os.path.join(_SCRIPT_DIR, "generated")
WEAPON_DIR   = os.path.join(_SCRIPT_DIR, "generated", "weapons")
OUTPUT_DIR   = os.path.join(_SCRIPT_DIR, "generated", "equipped")

FRAME_W, FRAME_H = 32, 32
DIRECTIONS = ["down", "left", "right", "up"]
ANIMATIONS = ["walk", "jump", "crouch", "interact", "slash"]
FRAMES_PER_DIR = 4
ORIENTATIONS = ["east", "south", "west", "north"]

# Weapons are drawn at 32×32 but the chibi character body only occupies
# roughly half the frame height. Scale weapons down so they feel proportional.
WEAPON_SCALE = 0.5

# ---------------------------------------------------------------------------
# WEAPON HAND ANCHORS
#
# For each slash frame and direction, defines where to place the weapon
# sprite's "grip center" relative to the frame origin (0,0).
#
# The grip is placed at the character's weapon-hand position during each
# slash frame, and the weapon sprite is centered on that point.
#
# Directions:
#   down  → character faces forward; weapon hand = right arm (east-ish)
#   up    → character faces back;    weapon hand = right arm (east-ish from back)
#   left  → character faces left;    weapon hand = front arm
#   right → character faces right;   weapon hand = front arm
#
# Weapon orientation per direction:
#   down  → "south"  (tip points down/forward in front view)
#   up    → "north"  (tip points away/back in back view)
#   left  → "west"   (tip points left in side view)
#   right → "east"   (tip points right in side view)
#
# Each entry: (hand_x, hand_y) — pixel position of weapon grip in the frame.
# The weapon sprite is pasted with its center at this point.
# ---------------------------------------------------------------------------

# Slash animation frame anchor positions per direction.
# F0=windup, F1=strike, F2=follow, F3=recover
_SLASH_HAND_ANCHORS = {
    "down": {
        # Weapon in right hand, shoulder at ~(22,18), arm swings up then forward-down
        "orient": "east",
        "anchors": [
            (27, 12),   # F0 windup: hand raised upper-right
            (28, 22),   # F1 strike: hand extended right-down (strike point)
            (26, 22),   # F2 follow: hand slightly in from full extension
            (23, 22),   # F3 recover: hand returning to rest
        ],
        "angle": [
            -70,   # F0: weapon angled up (windup)
            -20,   # F1: weapon angled forward-down (strike)
             10,   # F2: weapon tilting past horizontal
              0,   # F3: neutral
        ],
    },
    "up": {
        # Back view, same arm position mirrored
        "orient": "west",
        "anchors": [
            (4, 12),    # F0 windup: hand raised upper-left (back view)
            (3, 22),    # F1 strike
            (5, 22),    # F2 follow
            (8, 22),    # F3 recover
        ],
        "angle": [
            -70, -20, 10, 0,
        ],
    },
    "left": {
        # Front arm swings; character faces left, arm extends to the left
        "orient": "west",
        "anchors": [
            (12, 10),   # F0 windup: hand up (raised above head area)
            (5,  22),   # F1 strike: arm extended forward-down
            (4,  20),   # F2 follow: arm horizontal forward
            (13, 22),   # F3 recover: arm returning
        ],
        "angle": [
            -80,   # F0: weapon near-vertical (windup)
            -30,   # F1: weapon angled forward-down
             10,   # F2: weapon tilting forward
              0,   # F3: neutral
        ],
    },
    "right": {
        # Front arm swings; character faces right, arm extends to the right
        "orient": "east",
        "anchors": [
            (19, 10),   # F0 windup
            (26, 22),   # F1 strike
            (27, 20),   # F2 follow
            (18, 22),   # F3 recover
        ],
        "angle": [
            -80, -30, 10, 0,
        ],
    },
}

# Slash row index within the spritesheet for each direction.
# Spritesheet is: animations × directions × frames (row = anim_idx * 4 + dir_idx)
_ANIM_IDX = {a: i for i, a in enumerate(ANIMATIONS)}
_DIR_IDX  = {d: i for i, d in enumerate(DIRECTIONS)}


def _slash_row(direction):
    return _ANIM_IDX["slash"] * len(DIRECTIONS) + _DIR_IDX[direction]


def _get_char_frame(sheet: Image.Image, anim: str, direction: str, frame: int) -> Image.Image:
    """Extract a single 32×32 frame from the character spritesheet."""
    row = _ANIM_IDX[anim] * len(DIRECTIONS) + _DIR_IDX[direction]
    x = frame * FRAME_W
    y = row * FRAME_H
    return sheet.crop((x, y, x + FRAME_W, y + FRAME_H))


def _get_weapon_frame(weapon_sheet: Image.Image, orient: str) -> Image.Image:
    """Extract a single orientation frame from the weapon spritesheet."""
    idx = ORIENTATIONS.index(orient)
    x = idx * FRAME_W
    return weapon_sheet.crop((x, 0, x + FRAME_W, FRAME_H))


def _rotate_weapon(frame: Image.Image, angle_deg: float) -> Image.Image:
    """Rotate a weapon frame by angle_deg around its center (expand=False)."""
    if angle_deg == 0:
        return frame
    # Use BICUBIC for rotation but keep pixel art sharpness via nearest resize
    rotated = frame.rotate(-angle_deg, resample=Image.NEAREST, expand=False)
    return rotated


def _overlay_weapon(char_frame: Image.Image, weapon_frame: Image.Image,
                    hand_x: int, hand_y: int, angle_deg: float) -> Image.Image:
    """
    Overlay a scaled + rotated weapon onto a character frame.
    The weapon is scaled to WEAPON_SCALE, rotated, then placed so its
    center is at (hand_x, hand_y).
    """
    result = char_frame.copy()

    # Scale weapon down to match chibi character proportions
    if WEAPON_SCALE != 1.0:
        new_w = max(1, round(weapon_frame.width  * WEAPON_SCALE))
        new_h = max(1, round(weapon_frame.height * WEAPON_SCALE))
        weapon_frame = weapon_frame.resize((new_w, new_h), Image.NEAREST)

    rot_weapon = _rotate_weapon(weapon_frame, angle_deg)

    # Center the rotated weapon at the hand anchor
    paste_x = hand_x - rot_weapon.width  // 2
    paste_y = hand_y - rot_weapon.height // 2

    # Paste with alpha masking (weapon drawn on top of character)
    result.paste(rot_weapon, (paste_x, paste_y), mask=rot_weapon)
    return result


def _char_sheet_size(num_animations: int) -> tuple:
    return (FRAMES_PER_DIR * FRAME_W, num_animations * len(DIRECTIONS) * FRAME_H)


def composite_equipped(char_sheet: Image.Image, weapon_sheet: Image.Image,
                       char_name: str, weapon_name: str) -> tuple:
    """
    Build the equipped spritesheet.

    Copies all frames from char_sheet unchanged, then re-renders the
    slash animation rows with the weapon overlaid.

    Returns (equipped_sheet, frames_meta).
    """
    sheet_w = char_sheet.width
    sheet_h = char_sheet.height
    equipped = char_sheet.copy()

    frames_meta = {}

    for anim_idx, anim in enumerate(ANIMATIONS):
        for dir_idx, direction in enumerate(DIRECTIONS):
            row = anim_idx * len(DIRECTIONS) + dir_idx
            for frame_idx in range(FRAMES_PER_DIR):
                x = frame_idx * FRAME_W
                y = row * FRAME_H

                if anim == "slash":
                    # Overlay weapon on this frame
                    anchor_data = _SLASH_HAND_ANCHORS[direction]
                    orient      = anchor_data["orient"]
                    hand_x, hand_y = anchor_data["anchors"][frame_idx]
                    angle       = anchor_data["angle"][frame_idx]

                    char_frame   = equipped.crop((x, y, x + FRAME_W, y + FRAME_H))
                    weapon_frame = _get_weapon_frame(weapon_sheet, orient)
                    composited   = _overlay_weapon(char_frame, weapon_frame,
                                                   hand_x, hand_y, angle)
                    equipped.paste(composited, (x, y))

                frame_name = f"{anim}_{direction}_{frame_idx}"
                frames_meta[frame_name] = {
                    "frame": {"x": x, "y": y, "w": FRAME_W, "h": FRAME_H},
                    "rotated": False,
                    "trimmed": False,
                    "spriteSourceSize": {"x": 0, "y": 0, "w": FRAME_W, "h": FRAME_H},
                    "sourceSize": {"w": FRAME_W, "h": FRAME_H},
                }

    return equipped, frames_meta


def build_atlas(sprite_name: str, image_file: str,
                frames_meta: dict, sheet_size: tuple) -> dict:
    anim_groups = {}
    for anim in ANIMATIONS:
        for direction in DIRECTIONS:
            key = f"{anim}_{direction}"
            anim_groups[key] = [f"{anim}_{direction}_{i}" for i in range(FRAMES_PER_DIR)]

    return {
        "frames": frames_meta,
        "animations": anim_groups,
        "meta": {
            "app": "generate-equipped",
            "version": "1.0",
            "image": image_file,
            "format": "RGBA8888",
            "size": {"w": sheet_size[0], "h": sheet_size[1]},
            "scale": "1",
            "frameSize": {"w": FRAME_W, "h": FRAME_H},
            "tileSize": FRAME_W,
        },
    }


def build_preview_html(sprite_name: str, image_file: str, atlas_file: str) -> str:
    animations_json = json.dumps(ANIMATIONS)
    directions_json = json.dumps(DIRECTIONS)
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>{sprite_name} — Equipped Preview</title>
<style>
  body {{ background:#1a1a2e; color:#eee; font-family:monospace;
          display:flex; flex-direction:column; align-items:center; padding:2rem; }}
  h1 {{ margin-bottom:0.5rem; }}
  .info {{ color:#888; margin-bottom:1rem; }}
  canvas {{ image-rendering:pixelated; border:2px solid #444; }}
  .controls {{ display:flex; gap:0.5rem; margin:0.5rem 0; flex-wrap:wrap; justify-content:center; }}
  button {{ background:#333; color:#eee; border:1px solid #555;
            padding:0.4rem 0.8rem; cursor:pointer; font-family:monospace; }}
  button:hover {{ background:#555; }}
  button.active {{ background:#0a7; color:#fff; }}
  .sheet-preview {{ margin-top:1rem; border:1px solid #333; }}
</style>
</head><body>
<h1>{sprite_name}</h1>
<p class="info">Equipped spritesheet — all animations with weapon overlay on slash frames</p>
<canvas id="anim" width="{FRAME_W * 6}" height="{FRAME_H * 6}"></canvas>
<div class="controls" id="animBtns"><label>Anim:</label></div>
<div class="controls" id="dirBtns"><label>Dir:</label></div>
<p class="info">Full spritesheet (3x zoom):</p>
<img class="sheet-preview" id="sheetImg" />
<script>
const FW={FRAME_W}, FH={FRAME_H}, COLS={FRAMES_PER_DIR}, SCALE=6, FPS=6;
const ANIMATIONS={animations_json};
const DIRECTIONS={directions_json};
const canvas=document.getElementById("anim"), ctx=canvas.getContext("2d");
ctx.imageSmoothingEnabled=false;
const img=new Image(); img.src="{image_file}";
const sheetImg=document.getElementById("sheetImg"); sheetImg.src="{image_file}";
sheetImg.style.width=(128*3)+"px"; sheetImg.style.imageRendering="pixelated";
let animIdx=0, dirIdx=0, frameIdx=0;
function getRow(){{ return animIdx*DIRECTIONS.length+dirIdx; }}
function makeButtons(id,labels,setter){{
  const c=document.getElementById(id);
  labels.forEach((l,i)=>{{
    const b=document.createElement("button");
    b.textContent=l; b.onclick=()=>{{ setter(i); updateButtons(); }};
    if(i===0) b.classList.add("active");
    c.appendChild(b);
  }});
}}
function updateButtons(){{
  ["animBtns","dirBtns"].forEach((id,dim)=>{{
    [...document.getElementById(id).querySelectorAll("button")]
      .forEach((b,i)=>b.classList.toggle("active",i===(dim===0?animIdx:dirIdx)));
  }});
}}
makeButtons("animBtns",ANIMATIONS,i=>{{ animIdx=i; frameIdx=0; }});
makeButtons("dirBtns",DIRECTIONS,i=>{{ dirIdx=i; frameIdx=0; }});
function draw(){{
  ctx.clearRect(0,0,canvas.width,canvas.height);
  if(!img.complete) return;
  const sx=frameIdx*FW, sy=getRow()*FH;
  ctx.drawImage(img,sx,sy,FW,FH,0,0,FW*SCALE,FH*SCALE);
  frameIdx=(frameIdx+1)%COLS;
}}
img.onload=()=>setInterval(draw,1000/FPS);
if(img.complete) setInterval(draw,1000/FPS);
</script>
</body></html>
"""


def _load_char_sheet(preset_idx: int, char_name: str) -> Image.Image:
    """Load character sheet, auto-generating it (and saving to disk) if missing."""
    tag  = f"preset{preset_idx}"
    path = os.path.join(CHAR_DIR, f"{char_name}_{tag}.png")
    if not os.path.exists(path):
        print(f"  [auto] Generating character sheet for preset {preset_idx}...")
        if preset_idx < 0 or preset_idx >= len(_gc.PRESETS):
            raise ValueError(f"Invalid preset index {preset_idx}; "
                             f"valid range is 0-{len(_gc.PRESETS)-1}")
        palette    = _gc.PRESETS[preset_idx]
        hair_style = (_gc.DEFAULT_HAIR[preset_idx]
                      if preset_idx < len(_gc.DEFAULT_HAIR) else "short")
        sheet, _   = _gc.build_spritesheet(palette, hair_style)
        os.makedirs(CHAR_DIR, exist_ok=True)
        sheet.save(path)
        print(f"  [auto] Saved: {path}")
        return sheet.convert("RGBA")
    return Image.open(path).convert("RGBA")


def _load_weapon_sheet(weapon_name: str) -> Image.Image:
    """Load weapon sheet, auto-generating it (and saving to disk) if missing."""
    path = os.path.join(WEAPON_DIR, f"weapon_{weapon_name}.png")
    if not os.path.exists(path):
        print(f"  [auto] Generating weapon sheet for {weapon_name}...")
        sheet, _ = _gw.render_weapon(weapon_name)
        os.makedirs(WEAPON_DIR, exist_ok=True)
        sheet.save(path)
        print(f"  [auto] Saved: {path}")
        return sheet.convert("RGBA")
    return Image.open(path).convert("RGBA")


def generate_equipped(preset_idx: int, weapon_name: str, char_name: str):
    char_sheet   = _load_char_sheet(preset_idx, char_name)
    weapon_sheet = _load_weapon_sheet(weapon_name)

    sprite_name  = f"{char_name}_with_{weapon_name}_preset{preset_idx}"
    image_file   = f"{sprite_name}.png"
    atlas_file   = f"{sprite_name}.json"
    preview_file = f"{sprite_name}_preview.html"

    equipped_sheet, frames_meta = composite_equipped(
        char_sheet, weapon_sheet, char_name, weapon_name
    )

    sheet_path = os.path.join(OUTPUT_DIR, image_file)
    equipped_sheet.save(sheet_path)
    print(f"  Spritesheet : {sheet_path}  ({equipped_sheet.width}x{equipped_sheet.height})")

    atlas = build_atlas(sprite_name, image_file, frames_meta, equipped_sheet.size)
    atlas_path = os.path.join(OUTPUT_DIR, atlas_file)
    with open(atlas_path, "w") as f:
        json.dump(atlas, f, indent=2)
    print(f"  Atlas       : {atlas_path}")

    preview_path = os.path.join(OUTPUT_DIR, preview_file)
    with open(preview_path, "w") as f:
        f.write(build_preview_html(sprite_name, image_file, atlas_file))
    print(f"  Preview     : {preview_path}")


WEAPON_NAMES = [
    "sword", "axe", "spear", "staff", "bow", "dagger", "mace", "greatsword"
]


def main():
    parser = argparse.ArgumentParser(
        description="Composite a character + weapon into an equipped spritesheet"
    )
    parser.add_argument("--preset", type=int, default=0,
                        help="Character preset index (0-7)")
    parser.add_argument("--name", default=None,
                        help="Character base name (default: char_<preset>)")
    parser.add_argument("--weapon", choices=WEAPON_NAMES,
                        help="Weapon type to equip")
    parser.add_argument("--all-weapons", action="store_true",
                        help="Generate equipped sheets for all weapon types")
    args = parser.parse_args()

    char_name = args.name or f"char_{args.preset}"
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if args.all_weapons:
        for w in WEAPON_NAMES:
            print(f"\nEquipping {char_name} (preset {args.preset}) with {w}...")
            try:
                generate_equipped(args.preset, w, char_name)
            except FileNotFoundError as e:
                print(f"  SKIP: {e}")
        return

    if not args.weapon:
        parser.print_help()
        return

    print(f"Equipping {char_name} (preset {args.preset}) with {args.weapon}...")
    generate_equipped(args.preset, args.weapon, char_name)


if __name__ == "__main__":
    main()
