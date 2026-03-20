#!/usr/bin/env python3
"""
Character Studio — Flask web UI for the sprite generators.

Provides a live-preview web interface for configuring character presets,
hair styles, and weapons, with animated playback and one-click export.

Usage:
    pip install flask
    python app.py
    # open http://localhost:5000
"""

import base64
import io
import json
import os
import sys

from flask import Flask, jsonify, render_template, request, send_file

_DIR = os.path.dirname(os.path.abspath(__file__))
if _DIR not in sys.path:
    sys.path.insert(0, _DIR)

import generate_character as gc
import generate_weapon    as gw
import generate_equipped  as ge

app = Flask(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _img_to_b64(img) -> str:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def _preset_info(idx: int, p: dict) -> dict:
    hair = gc.DEFAULT_HAIR[idx] if idx < len(gc.DEFAULT_HAIR) else "short"
    return {
        "idx":          idx,
        "name":         p["name"],
        "default_hair": hair,
        "skin":   list(p["skin"][:3]),
        "hair":   list(p["hair"][:3]),
        "shirt":  list(p["shirt"][:3]),
        "pants":  list(p["pants"][:3]),
        "shoes":  list(p["shoes"][:3]),
        "eye":    list(p["eye"][:3]),
    }


def _hex_to_rgba(h: str) -> tuple:
    """Convert a 6-char hex string (no #) to an RGBA tuple."""
    h = h.lstrip("#").zfill(6)[:6]
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (r, g, b, 255)


def _derive_shade(rgba: tuple, amount: int = 30) -> tuple:
    """Darken and slightly cool-shift a color for shade derivation."""
    r, g, b, a = rgba
    return (max(0, r - amount), max(0, g - amount - 3), max(0, b - amount + 5), a)


def _derive_highlight(rgba: tuple, amount: int = 25) -> tuple:
    """Lighten a color for highlight derivation."""
    r, g, b, a = rgba
    return (min(255, r + amount), min(255, g + amount), min(255, b + amount), a)


# Color param name → palette keys to override (base + shade derived automatically)
_COLOR_PARAMS = {
    "skin_hex":  ("skin",  "skin_shade"),
    "hair_hex":  ("hair",  "hair_shade",  "hair_highlight"),
    "shirt_hex": ("shirt", "shirt_shade"),
    "pants_hex": ("pants", "pants_shade"),
    "shoes_hex": ("shoes", "shoes_shade"),
    "eye_hex":   ("eye",),
}


def _apply_color_overrides(palette: dict, args) -> dict:
    """Apply optional hex color overrides from request args to a palette copy."""
    pal = dict(palette)
    for param, keys in _COLOR_PARAMS.items():
        val = args.get(param)
        if not val:
            continue
        try:
            rgba = _hex_to_rgba(val)
        except (ValueError, TypeError):
            continue
        base_key = keys[0]
        pal[base_key] = rgba
        if len(keys) >= 2:
            pal[keys[1]] = _derive_shade(rgba)     # *_shade
        if len(keys) >= 3:
            pal[keys[2]] = _derive_highlight(rgba)  # *_highlight (hair only)
    return pal


# ---------------------------------------------------------------------------
# Routes — pages
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    presets = [_preset_info(i, p) for i, p in enumerate(gc.PRESETS)]
    # Build weapon list with category metadata
    weapons_meta = [
        {"name": w, "category": gw.WEAPON_CATEGORIES.get(w, "fantasy")}
        for w in gw.WEAPON_PIXELS.keys()
    ]
    return render_template(
        "index.html",
        presets        = presets,
        hair_styles    = list(gc.HAIR_STYLES.keys()),
        weapons        = list(gw.WEAPON_PIXELS.keys()),
        weapons_meta   = weapons_meta,
        animations     = gc.ANIMATIONS,
        directions     = gc.DIRECTIONS,
        frames_per_dir = gc.FRAMES_PER_DIR,
        frame_w        = gc.FRAME_W,
        frame_h        = gc.FRAME_H,
    )


# ---------------------------------------------------------------------------
# Routes — API (return base64 PNG data)
# ---------------------------------------------------------------------------

@app.route("/api/character")
def api_character():
    preset_idx = int(request.args.get("preset", 0))
    hair       = request.args.get("hair", "short")
    if not (0 <= preset_idx < len(gc.PRESETS)):
        return jsonify({"error": "invalid preset"}), 400
    palette    = _apply_color_overrides(gc.PRESETS[preset_idx], request.args)
    sheet, _   = gc.build_spritesheet(palette, hair)
    return jsonify({"image": _img_to_b64(sheet),
                    "width": sheet.width, "height": sheet.height})


@app.route("/api/weapon")
def api_weapon():
    weapon = request.args.get("weapon", "sword")
    if weapon not in gw.WEAPON_PIXELS:
        return jsonify({"error": "unknown weapon"}), 400
    sheet, _ = gw.render_weapon(weapon)
    return jsonify({"image": _img_to_b64(sheet),
                    "width": sheet.width, "height": sheet.height})


@app.route("/api/equipped")
def api_equipped():
    preset_idx = int(request.args.get("preset", 0))
    hair       = request.args.get("hair", "short")
    weapon     = request.args.get("weapon", "sword")
    if not (0 <= preset_idx < len(gc.PRESETS)):
        return jsonify({"error": "invalid preset"}), 400
    if weapon not in gw.WEAPON_PIXELS:
        return jsonify({"error": "unknown weapon"}), 400
    palette       = _apply_color_overrides(gc.PRESETS[preset_idx], request.args)
    char_sheet, _ = gc.build_spritesheet(palette, hair)
    wpn_sheet,  _ = gw.render_weapon(weapon)
    equipped, _   = ge.composite_equipped(char_sheet, wpn_sheet,
                                          f"char_{preset_idx}", weapon)
    return jsonify({"image": _img_to_b64(equipped),
                    "width": equipped.width, "height": equipped.height})


# ---------------------------------------------------------------------------
# Routes — Export (download PNG to disk)
# ---------------------------------------------------------------------------

@app.route("/api/export")
def api_export():
    kind       = request.args.get("kind", "character")
    preset_idx = int(request.args.get("preset", 0))
    hair       = request.args.get("hair", "short")
    weapon     = request.args.get("weapon", "sword")

    if kind == "character":
        palette    = _apply_color_overrides(gc.PRESETS[preset_idx], request.args)
        sheet, _   = gc.build_spritesheet(palette, hair)
        filename   = f"char_{preset_idx}_{hair}.png"
    elif kind == "weapon":
        sheet, _   = gw.render_weapon(weapon)
        filename   = f"weapon_{weapon}.png"
    else:
        palette       = _apply_color_overrides(gc.PRESETS[preset_idx], request.args)
        char_sheet, _ = gc.build_spritesheet(palette, hair)
        wpn_sheet,  _ = gw.render_weapon(weapon)
        sheet, _      = ge.composite_equipped(char_sheet, wpn_sheet,
                                              f"char_{preset_idx}", weapon)
        filename = f"char_{preset_idx}_{hair}_with_{weapon}.png"

    buf = io.BytesIO()
    sheet.save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png",
                     as_attachment=True, download_name=filename)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("\n  ⚔️  Character Studio")
    print("  Open → http://localhost:8765\n")
    app.run(debug=False, host="0.0.0.0", port=8765)
