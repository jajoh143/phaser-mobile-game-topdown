#!/usr/bin/env python3
"""
Interactive character builder — walks the user through creating a sprite
step-by-step via console prompts instead of requiring CLI flags.

Run:
    python create_character.py
"""

import os
import sys
import re

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


# ---------------------------------------------------------------------------
# Import the generator (sibling module)
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.dirname(__file__))
import generate_character as gen  # noqa: E402


# ---------------------------------------------------------------------------
# Main wizard
# ---------------------------------------------------------------------------

def run_wizard():
    print("=" * 52)
    print("  Character Sprite Builder")
    print("=" * 52)

    # --- Step 1: Name ---
    print("\n--- Step 1: Character Name ---")
    name = ask("Character name (used in filenames)", default="player")
    # Sanitize to safe filename chars
    name = re.sub(r"[^a-zA-Z0-9_-]", "_", name).lower()

    # --- Step 2: Palette ---
    print("\n--- Step 2: Color Palette ---")
    palette_keys = list(gen.PALETTES.keys()) + ["custom"]
    palette_labels = []
    for k in palette_keys:
        if k == "custom":
            palette_labels.append("Custom — pick every color yourself")
        else:
            palette_labels.append(f"{k} — {gen.PALETTES[k]['name']}")

    choice = ask_choice("Choose a color palette:", palette_labels, default=0)

    if palette_keys[choice] == "custom":
        palette = build_custom_palette()
        palette_tag = "custom"
    else:
        palette_tag = palette_keys[choice]
        palette = dict(gen.PALETTES[palette_tag])  # shallow copy

        # Offer to tweak individual colors
        if ask_yes_no("\nWould you like to customize individual colors?", default=False):
            palette = customize_palette(palette)

    # --- Step 3: Body proportions ---
    print("\n--- Step 3: Body Proportions ---")
    if ask_yes_no("Would you like to adjust body part sizes?", default=False):
        customize_body_parts()

    # --- Step 4: Output ---
    print("\n--- Step 4: Output ---")
    output_dir = ask("Output directory", default=gen.OUTPUT_DIR)
    os.makedirs(output_dir, exist_ok=True)

    # --- Summary ---
    print("\n" + "=" * 52)
    print("  Summary")
    print("=" * 52)
    print(f"  Name:     {name}")
    print(f"  Palette:  {palette_tag}")
    print(f"  Output:   {output_dir}")
    print()

    if not ask_yes_no("Generate sprite?", default=True):
        print("Cancelled.")
        return

    # --- Generate ---
    print("\nGenerating...")

    sheet_img, frames_meta = gen.build_spritesheet(palette)

    image_file = f"{name}_{palette_tag}.png"
    atlas_file = f"{name}_{palette_tag}.json"
    preview_file = f"{name}_{palette_tag}_preview.html"

    import json

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

    total = len(gen.DIRECTIONS) * gen.FRAMES_PER_DIR
    print(f"\n  {total} frames generated ({gen.FRAME_W}x{gen.FRAME_H}px each). Done!")


# ---------------------------------------------------------------------------
# Custom palette builder
# ---------------------------------------------------------------------------

COLOR_KEYS = ["skin", "hair", "shirt", "pants", "shoes", "outline", "eye"]

# Sensible starting defaults for custom palette
CUSTOM_DEFAULTS = {
    "skin":    (210, 180, 150, 255),
    "hair":    (60, 45, 30, 255),
    "shirt":   (100, 115, 130, 255),
    "pants":   (65, 65, 75, 255),
    "shoes":   (50, 42, 38, 255),
    "outline": (35, 30, 28, 255),
    "eye":     (30, 30, 30, 255),
}


def build_custom_palette() -> dict:
    """Walk the user through picking a color for every body part."""
    print("\nPick a color for each part (hex #rrggbb or r,g,b):")
    palette = {"name": "Custom"}
    for key in COLOR_KEYS:
        palette[key] = ask_color(f"  {key}", CUSTOM_DEFAULTS[key])
    return palette


def customize_palette(palette: dict) -> dict:
    """Let the user selectively override colors in an existing palette."""
    print("\nPress Enter to keep current value, or type a new color.")
    for key in COLOR_KEYS:
        current = palette.get(key, CUSTOM_DEFAULTS[key])
        palette[key] = ask_color(f"  {key}", current)
    return palette


# ---------------------------------------------------------------------------
# Body part customization
# ---------------------------------------------------------------------------

PART_NAMES = ["head", "hair", "torso", "arm_l", "arm_r", "leg_l", "leg_r", "foot_l", "foot_r"]


def customize_body_parts():
    """Let the user tweak body part rects."""
    print("\nCurrent body part dimensions (x, y, width, height):")
    for i, name in enumerate(PART_NAMES):
        rect = gen.BODY_PARTS[name]["rect"]
        print(f"  {i + 1}) {name:8s}  x={rect[0]:2d}  y={rect[1]:2d}  w={rect[2]:2d}  h={rect[3]:2d}")

    print("\nEnter a part number to edit, or press Enter to continue.")
    while True:
        raw = input("Part # (or Enter to finish): ").strip()
        if not raw:
            break
        if raw.isdigit() and 1 <= int(raw) <= len(PART_NAMES):
            idx = int(raw) - 1
            part_name = PART_NAMES[idx]
            rect = gen.BODY_PARTS[part_name]["rect"]
            print(f"\n  Editing {part_name}: current rect = ({rect[0]}, {rect[1]}, {rect[2]}, {rect[3]})")
            print("  Enter new values as: x, y, w, h")
            vals = input(f"  [{rect[0]}, {rect[1]}, {rect[2]}, {rect[3]}]: ").strip()
            if vals:
                parts = [p.strip() for p in vals.split(",")]
                if len(parts) == 4 and all(p.isdigit() for p in parts):
                    new_rect = tuple(int(p) for p in parts)
                    gen.BODY_PARTS[part_name]["rect"] = new_rect
                    print(f"  Updated {part_name} to {new_rect}")
                else:
                    print("  Invalid input, keeping current value.")
        else:
            print(f"  Enter a number between 1 and {len(PART_NAMES)}.")


# ---------------------------------------------------------------------------
# Entry
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        run_wizard()
    except KeyboardInterrupt:
        print("\n\nCancelled.")
        sys.exit(1)
