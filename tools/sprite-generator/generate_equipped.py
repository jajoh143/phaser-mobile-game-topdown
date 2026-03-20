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
# Pixel positions of the weapon-hand (forearm tip center) inside the 32×32
# frame for each animation frame. Derived from the shoulder-pivot arm system
# in generate_character.py:
#
#   Weapon arm per direction:
#     down  → right arm, shoulder at (22, 18)
#     up    → right arm, shoulder at (22, 18)   [back view, same screen side]
#     left  → left  arm, shoulder at (16, 18)   [front arm in side view]
#     right → right arm, shoulder at (15, 18)   [front arm in side view, mirrored]
#
#   Forearm tip = center of the outermost 3-4 px row of the arm pose.
#   All coordinates are in the native 32×32 pixel space.
#
#   Weapon orient frames in the weapon spritesheet:
#     0=east (tip→right), 1=south (tip→down), 2=west (tip→left), 3=north (tip→up)
#
# ---------------------------------------------------------------------------

# Slash animation frame anchor positions per direction.
# F0=windup  F1=strike  F2=follow  F3=recover
#
# Calculated from actual arm-pose pixel offsets in generate_character.py:
#   "down"  R-arm mirrored: slash_windup→(24,13)  slash_strike→(28,22)
#                           slash_follow→(27,22)  hang→(24,23)
#   "up"    R-arm same positions as down (same shoulder x=22)
#   "left"  L-arm direct:   side_slash_windup→(13,14)  side_slash_strike→(10,22)
#                           side_slash_follow→(10,19)  side_hang→(13,23)
#   "right" R-arm mirrored: side_slash_windup→(18,14)  side_slash_strike→(21,22)
#                           side_slash_follow→(21,19)  side_hang→(18,23)
_SLASH_HAND_ANCHORS = {
    "down": {
        "orient": "east",
        "anchors": [
            (24, 13),   # F0 windup:  arm raised, hand upper-right
            (28, 22),   # F1 strike:  arm fully extended diagonal right-down
            (27, 22),   # F2 follow:  arm settling, slightly in
            (24, 23),   # F3 recover: arm hanging at side
        ],
        "angle": [
            -80,   # weapon tip pointing up (near-vertical)
             20,   # weapon tip pointing lower-right (arm extended down-right)
              5,   # weapon tip just past horizontal
              0,   # neutral hang
        ],
    },
    "up": {
        # Back view — weapon arm is still screen-right (same shoulder x=22).
        "orient": "east",
        "anchors": [
            (24, 13),
            (28, 22),
            (27, 22),
            (24, 23),
        ],
        "angle": [-80, 20, 5, 0],
    },
    "left": {
        # Left-facing: front (left) arm swings; shoulder at (16, 18).
        "orient": "west",
        "anchors": [
            (13, 14),   # F0 windup:  arm raised above head
            (10, 22),   # F1 strike:  arm fully extended forward-down
            (10, 19),   # F2 follow:  arm horizontal forward
            (13, 23),   # F3 recover: arm hanging
        ],
        "angle": [
             80,   # (west+80°CW ≈ pointing up-left)
            -20,   # weapon tip leading slightly above forward
             -5,
              0,
        ],
    },
    "right": {
        # Right-facing: front (right) arm swings (mirrored); shoulder at (15, 18).
        "orient": "east",
        "anchors": [
            (18, 14),   # F0 windup
            (21, 22),   # F1 strike
            (21, 19),   # F2 follow
            (18, 23),   # F3 recover
        ],
        "angle": [-80, 20, 5, 0],
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


# ---------------------------------------------------------------------------
# CARRY ANCHORS  (non-slash animations: walk, jump, crouch, interact)
#
# The weapon rests in the character's hand in a "carry" pose.
# Walk frames add a small bob/sway delta on top of the carry position.
# ---------------------------------------------------------------------------

_CARRY_ANCHORS = {
    # Forearm-tip center of the hanging arm in the 32×32 pixel frame.
    # "down"  R-arm shoulder(22,18) + hang offsets(+2,+5) → (24, 23)
    # "up"    same shoulder x, back view                  → (24, 23)
    # "left"  L-arm shoulder(16,18) + side_hang(-3,+5)   → (13, 23)
    # "right" R-arm shoulder(15,18) + mirrored(+3,+5)    → (18, 23)
    "down":  {"orient": "east",  "x": 24, "y": 23, "angle":  0},
    "left":  {"orient": "west",  "x": 13, "y": 23, "angle":  0},
    "right": {"orient": "east",  "x": 18, "y": 23, "angle":  0},
    "up":    {"orient": "east",  "x": 24, "y": 23, "angle":  0},
}

# Per-frame walk delta (dx, dy) added to the carry anchor.
# Based on actual arm-pose forearm tip y per walk frame:
#   "down"  R: F0=mid_back(y22) F1=swing_back(y23) F2=mid_fwd(y22) F3=swing_fwd(y21)
#   "left"  L: F0=side_hang(y23) F1=side_fwd(y22) F2=side_hang(y23) F3=side_back(y24)
#   "right" mirrored — same y variation as "left"
#   "up"    same as "down"
_WALK_DELTAS = {
    "down":  [(0, -1), (0,  0), (0, -1), (0, -2)],
    "left":  [(0,  0), (0, -1), (0,  0), (0,  1)],
    "right": [(0,  0), (0, -1), (0,  0), (0,  1)],
    "up":    [(0, -1), (0,  0), (0, -1), (0, -2)],
}


def build_anchor_data() -> dict:
    """
    Build a complete hand-anchor data structure for all animations, directions,
    and frames. Used by the Phaser runtime to position a weapon sprite overlay.

    Returns a nested dict:
        {
          "walk": {
            "down": [
              {"x": 22, "y": 19, "angle": -20, "orient": "east"},  # frame 0
              ...
            ],
            ...
          },
          "slash": { ... },
          ...
        }

    Coordinates are in the native 32×32 pixel space.
    The Phaser scene multiplies these by the character's display scale to get
    screen-space offsets from the character sprite's origin.
    """
    anchors: dict = {}

    for anim in ANIMATIONS:
        anchors[anim] = {}
        for direction in DIRECTIONS:
            frames = []
            if anim == "slash":
                slash_data = _SLASH_HAND_ANCHORS[direction]
                orient     = slash_data["orient"]
                for frame_idx in range(FRAMES_PER_DIR):
                    hx, hy = slash_data["anchors"][frame_idx]
                    angle  = slash_data["angle"][frame_idx]
                    frames.append({
                        "x":      hx,
                        "y":      hy,
                        "angle":  angle,
                        "orient": orient,
                    })
            else:
                carry  = _CARRY_ANCHORS[direction]
                deltas = _WALK_DELTAS[direction] if anim == "walk" else [(0, 0)] * FRAMES_PER_DIR
                for frame_idx in range(FRAMES_PER_DIR):
                    dx, dy = deltas[frame_idx]
                    frames.append({
                        "x":      carry["x"] + dx,
                        "y":      carry["y"] + dy,
                        "angle":  carry["angle"],
                        "orient": carry["orient"],
                    })
            anchors[anim][direction] = frames

    return anchors


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
