#!/usr/bin/env python3
"""
Export sprites and hand-anchor data for use in Phaser 3 runtime weapon overlay.

Generates into public/assets/sprites/:
  - char_<N>.png          — character spritesheets (one per preset)
  - weapon_<name>.png     — weapon spritesheets (one per weapon)
  - hand_anchors.json     — per-animation, per-direction, per-frame anchor data

The hand_anchors.json format:
  {
    "walk":  { "down": [{"x":22,"y":19,"angle":-20,"orient":"east"}, ...], ... },
    "slash": { ... },
    ...
  }

Coordinates are in the 32×32 pixel space. In Phaser, multiply by charSprite.scaleX
to get the screen-space offset from the character sprite's origin (top-left).

Usage:
    python export_for_game.py                 # export all presets + all weapons
    python export_for_game.py --preset 0      # export only preset 0
    python export_for_game.py --weapon sword  # export only one weapon
"""

import argparse
import json
import os
import sys

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

import generate_character      as gc
import generate_weapon         as gw
import generate_equipped       as ge
import generate_brick_wall     as gbw
import generate_wood_floor     as gwf
import generate_wooden_bar     as gbar
import generate_alcohol_bottles as gab

# Output directory — resolves to  <repo-root>/public/assets/sprites/
_REPO_ROOT  = os.path.abspath(os.path.join(_SCRIPT_DIR, "..", ".."))
OUTPUT_DIR  = os.path.join(_REPO_ROOT, "public", "assets", "sprites")


def export_character(preset_idx: int) -> str:
    """Generate and save a character spritesheet. Returns the output path."""
    if not (0 <= preset_idx < len(gc.PRESETS)):
        raise ValueError(f"preset {preset_idx} out of range (0-{len(gc.PRESETS)-1})")

    palette    = gc.PRESETS[preset_idx]
    hair_style = (gc.DEFAULT_HAIR[preset_idx]
                  if preset_idx < len(gc.DEFAULT_HAIR) else "short")
    sheet, _   = gc.build_spritesheet(palette, hair_style)

    out_path = os.path.join(OUTPUT_DIR, f"char_{preset_idx}.png")
    sheet.save(out_path)
    print(f"  char  → {out_path}  ({sheet.width}×{sheet.height})")
    return out_path


def export_weapon(weapon_name: str) -> str:
    """Generate and save a weapon spritesheet. Returns the output path."""
    if weapon_name not in gw.WEAPON_PIXELS:
        raise ValueError(f"unknown weapon '{weapon_name}'")

    sheet, _ = gw.render_weapon(weapon_name)
    out_path = os.path.join(OUTPUT_DIR, f"weapon_{weapon_name}.png")
    sheet.save(out_path)
    print(f"  wpn   → {out_path}  ({sheet.width}×{sheet.height})")
    return out_path


def export_anchors() -> str:
    """Build and save hand_anchors.json. Returns the output path."""
    anchors  = ge.build_anchor_data()
    out_path = os.path.join(OUTPUT_DIR, "hand_anchors.json")
    with open(out_path, "w") as f:
        json.dump(anchors, f, indent=2)
    print(f"  anchors → {out_path}")
    return out_path


def export_bar_assets() -> None:
    """Generate and export all bar scene environment tiles/sprites."""
    import json, shutil

    assets = [
        ("brick_wall",      gbw.generate,  gbw.build_atlas),
        ("wood_floor",      gwf.generate,  gwf.build_atlas),
        ("wooden_bar",      gbar.generate, gbar.build_atlas),
        ("alcohol_bottles", gab.generate,  gab.build_atlas),
    ]
    for name, gen_fn, atlas_fn in assets:
        img = gen_fn()
        png_path  = os.path.join(OUTPUT_DIR, f"{name}.png")
        json_path = os.path.join(OUTPUT_DIR, f"{name}.json")
        img.save(png_path)
        with open(json_path, "w") as f:
            try:
                atlas = atlas_fn(f"{name}.png")
            except TypeError:
                atlas = atlas_fn()
            json.dump(atlas, f, indent=2)
        print(f"  bar   → {png_path}  ({img.width}×{img.height})")


def main():
    parser = argparse.ArgumentParser(
        description="Export character/weapon sprites + anchor JSON for Phaser 3"
    )
    parser.add_argument("--preset", type=int, default=None,
                        help="Export only this character preset index")
    parser.add_argument("--weapon", default=None,
                        help="Export only this weapon (e.g. sword, pistol)")
    parser.add_argument("--no-anchors", action="store_true",
                        help="Skip exporting hand_anchors.json")
    parser.add_argument("--bar", action="store_true",
                        help="Export only bar scene assets (brick_wall, wood_floor, wooden_bar, alcohol_bottles)")
    args = parser.parse_args()

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"\nExporting to: {OUTPUT_DIR}\n")

    # Bar scene assets (quick export shortcut)
    if args.bar:
        print("Exporting bar scene assets...")
        export_bar_assets()
        print("\nDone.")
        return

    # Characters
    if args.preset is not None:
        export_character(args.preset)
    else:
        print(f"Exporting {len(gc.PRESETS)} character presets...")
        for i in range(len(gc.PRESETS)):
            export_character(i)

    print()

    # Weapons
    all_weapons = list(gw.WEAPON_PIXELS.keys())
    if args.weapon is not None:
        export_weapon(args.weapon)
    else:
        print(f"Exporting {len(all_weapons)} weapons...")
        for w in all_weapons:
            export_weapon(w)

    print()

    # Anchor data
    if not args.no_anchors:
        print("Exporting hand anchors...")
        export_anchors()

    # Bar scene assets
    print("\nExporting bar scene assets...")
    export_bar_assets()

    print("\nDone.")


if __name__ == "__main__":
    main()
