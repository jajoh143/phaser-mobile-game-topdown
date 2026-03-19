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
    }


# ---------------------------------------------------------------------------
# Routes — pages
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    presets = [_preset_info(i, p) for i, p in enumerate(gc.PRESETS)]
    return render_template(
        "index.html",
        presets       = presets,
        hair_styles   = list(gc.HAIR_STYLES.keys()),
        weapons       = list(gw.WEAPON_PIXELS.keys()),
        animations    = gc.ANIMATIONS,
        directions    = gc.DIRECTIONS,
        frames_per_dir= gc.FRAMES_PER_DIR,
        frame_w       = gc.FRAME_W,
        frame_h       = gc.FRAME_H,
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
    palette    = gc.PRESETS[preset_idx]
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
    palette      = gc.PRESETS[preset_idx]
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
        palette    = gc.PRESETS[preset_idx]
        sheet, _   = gc.build_spritesheet(palette, hair)
        filename   = f"char_{preset_idx}_{hair}.png"
    elif kind == "weapon":
        sheet, _   = gw.render_weapon(weapon)
        filename   = f"weapon_{weapon}.png"
    else:
        palette      = gc.PRESETS[preset_idx]
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
    print("  Open → http://localhost:5000\n")
    app.run(debug=False, host="0.0.0.0", port=5000)
