#!/usr/bin/env python3
"""
Interactive character builder — walks the user through creating a sprite
step-by-step via console prompts instead of requiring CLI flags.

Run:
    python create_character.py
"""
# v6 — 16x16 top-heavy chibi style (renders at 2x on 32x32 world grid)

import os
import sys
import re
import json

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def ask(prompt: str, default: str = "") -> str:
    """Prompt the user for text input with an optional default."""
    suffix = f" [{default}]" if default else ""
    answer = input(f"{prompt}{suffix}: ").strip()
    return answer if answer else default


def ask_choice(prompt: str, options: list[str], default: int = 0) -> int:
    """Prompt the user to pick from a numbered list. Returns the chosen index."""
    print(f"\n{prompt}")
    for i, option in enumerate(options):
        marker = " *" if i == default else ""
        print(f"  {i + 1}) {option}{marker}")
    while True:
        raw = input(f"Choice [default {default + 1}]: ").strip()
        if not raw:
            return default
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return int(raw) - 1
        print(f"  Please enter a number between 1 and {len(options)}.")


def ask_color(prompt: str, default: tuple[int, ...]) -> tuple[int, int, int, int]:
    """Prompt the user for an RGBA color as a hex string or comma-separated values."""
    default_hex = "#{:02x}{:02x}{:02x}".format(*default[:3])
    print(f"\n{prompt}")
    print(f"  Enter a hex color (#rrggbb) or r,g,b values (0-255).")
    raw = input(f"  [{default_hex}]: ").strip()
    if not raw:
        return (default[0], default[1], default[2], 255)

    # Try hex
    hex_match = re.match(r"^#?([0-9a-fA-F]{6})$", raw)
    if hex_match:
        h = hex_match.group(1)
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)

    # Try comma-separated
    parts = [p.strip() for p in raw.split(",")]
    if len(parts) >= 3 and all(p.isdigit() for p in parts[:3]):
        r, g, b = int(parts[0]), int(parts[1]), int(parts[2])
        if all(0 <= v <= 255 for v in (r, g, b)):
            return (r, g, b, 255)

    print(f"  Could not parse color, using default {default_hex}.")
    return (default[0], default[1], default[2], 255)


def ask_yes_no(prompt: str, default: bool = True) -> bool:
    """Prompt the user for a yes/no answer."""
    hint = "Y/n" if default else "y/N"
    raw = input(f"{prompt} [{hint}]: ").strip().lower()
    if not raw:
        return default
    return raw in ("y", "yes")


def _darken(color: tuple[int, int, int, int], amount: int = 30) -> tuple[int, int, int, int]:
    """Create a darker shade of a color."""
    return (
        max(0, color[0] - amount),
        max(0, color[1] - amount),
        max(0, color[2] - amount),
        255,
    )


def _lighten(color: tuple[int, int, int, int], amount: int = 30) -> tuple[int, int, int, int]:
    """Create a lighter highlight of a color."""
    return (
        min(255, color[0] + amount),
        min(255, color[1] + amount),
        min(255, color[2] + amount),
        255,
    )


# ---------------------------------------------------------------------------
# Import the generator (sibling module)
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.dirname(__file__))
import generate_character as gen  # noqa: E402


# ---------------------------------------------------------------------------
# Main wizard
# ---------------------------------------------------------------------------

def run_wizard():
    print("=" * 56)
    print("  Character Sprite Builder (v6 — 16x16 Chibi Style)")
    print("  Frame: 16x16px (renders 2x on 32x32 world grid)")
    print("  Animations: walk, jump, crouch, interact")
    print("=" * 56)

    # --- Step 1: Name ---
    print("\n--- Step 1: Character Name ---")
    name = ask("Character name (used in filenames)", default="player")
    name = re.sub(r"[^a-zA-Z0-9_-]", "_", name).lower()

    # --- Step 2: Preset ---
    print("\n--- Step 2: Color Preset ---")
    preset_labels = [f"{i}: {p['name']}" for i, p in enumerate(gen.PRESETS)]
    preset_labels.append("Custom — pick every color yourself")

    choice = ask_choice("Choose a color preset:", preset_labels, default=0)

    if choice == len(gen.PRESETS):
        palette = build_custom_palette()
        preset_tag = "custom"
    else:
        preset_tag = f"preset{choice}"
        palette = dict(gen.PRESETS[choice])

        if ask_yes_no("\nWould you like to customize individual colors?", default=False):
            palette = customize_palette(palette)

    # --- Step 3: Hair Style ---
    print("\n--- Step 3: Hair Style ---")
    hair_labels = list(gen.HAIR_STYLES.keys())
    default_hair_idx = 0
    if choice < len(gen.DEFAULT_HAIR):
        default_hair_name = gen.DEFAULT_HAIR[choice]
        if default_hair_name in hair_labels:
            default_hair_idx = hair_labels.index(default_hair_name)

    hair_choice = ask_choice("Choose a hair style:", hair_labels, default=default_hair_idx)
    hair_style = hair_labels[hair_choice]

    # --- Step 4: Output ---
    print("\n--- Step 4: Output ---")
    output_dir = ask("Output directory", default=gen.OUTPUT_DIR)
    os.makedirs(output_dir, exist_ok=True)

    # --- Summary ---
    print("\n" + "=" * 52)
    print("  Summary")
    print("=" * 52)
    print(f"  Name:       {name}")
    print(f"  Preset:     {preset_tag}")
    print(f"  Hair:       {hair_style}")
    print(f"  Output:     {output_dir}")
    print()

    if not ask_yes_no("Generate sprite?", default=True):
        print("Cancelled.")
        return

    # --- Generate ---
    print("\nGenerating...")

    sheet_img, frames_meta = gen.build_spritesheet(palette, hair_style)

    image_file = f"{name}_{preset_tag}.png"
    atlas_file = f"{name}_{preset_tag}.json"
    preview_file = f"{name}_{preset_tag}_preview.html"

    # Save spritesheet
    sheet_path = os.path.join(output_dir, image_file)
    sheet_img.save(sheet_path)
    print(f"  Spritesheet: {sheet_path}")

    # Save atlas
    atlas = gen.build_atlas(name, image_file, frames_meta, sheet_img.size)
    atlas_path = os.path.join(output_dir, atlas_file)
    with open(atlas_path, "w") as f:
        json.dump(atlas, f, indent=2)
    print(f"  Atlas:       {atlas_path}")

    # Save preview
    preview_path = os.path.join(output_dir, preview_file)
    with open(preview_path, "w") as f:
        f.write(gen.build_preview_html(name, image_file, atlas_file))
    print(f"  Preview:     {preview_path}")

    total = len(gen.ANIMATIONS) * len(gen.DIRECTIONS) * gen.FRAMES_PER_DIR
    print(f"\n  {total} frames generated ({gen.FRAME_W}x{gen.FRAME_H}px each).")
    print(f"  Animations: {', '.join(gen.ANIMATIONS)}")
    print(f"  Done!")


# ---------------------------------------------------------------------------
# Custom palette builder
# ---------------------------------------------------------------------------

COLOR_KEYS = ["skin", "hair", "shirt", "pants", "shoes", "outline", "eye", "mouth_inner", "mouth_line"]

CUSTOM_DEFAULTS = {
    "skin":        (235, 190, 160, 255),
    "hair":        (55, 60, 120, 255),
    "shirt":       (190, 60, 55, 255),
    "pants":       (70, 65, 80, 255),
    "shoes":       (55, 45, 40, 255),
    "outline":     (35, 28, 28, 255),
    "eye":         (28, 28, 35, 255),
    "mouth_inner": (120, 45, 40, 255),
    "mouth_line":  (35, 28, 28, 255),
}


def build_custom_palette() -> dict:
    """Walk the user through picking a color for every body part."""
    print("\nPick a color for each part (hex #rrggbb or r,g,b):")
    palette = {"name": "Custom"}
    for key in COLOR_KEYS:
        palette[key] = ask_color(f"  {key}", CUSTOM_DEFAULTS[key])
    # Auto-generate shade/highlight variants for 16x16 chibi style
    for base_key in ["skin", "hair", "shirt", "pants", "shoes"]:
        palette[f"{base_key}_shade"] = _darken(palette[base_key])
    palette["hair_highlight"] = _lighten(palette["hair"])
    return palette


def customize_palette(palette: dict) -> dict:
    """Let the user selectively override colors in an existing palette."""
    print("\nPress Enter to keep current value, or type a new color.")
    for key in COLOR_KEYS:
        current = palette.get(key, CUSTOM_DEFAULTS[key])
        new_color = ask_color(f"  {key}", current)
        palette[key] = new_color
    # Regenerate shade/highlight variants
    for base_key in ["skin", "hair", "shirt", "pants", "shoes"]:
        palette[f"{base_key}_shade"] = _darken(palette[base_key])
    palette["hair_highlight"] = _lighten(palette["hair"])
    return palette


# ---------------------------------------------------------------------------
# Entry
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        run_wizard()
    except KeyboardInterrupt:
        print("\n\nCancelled.")
        sys.exit(1)
