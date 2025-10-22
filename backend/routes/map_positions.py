from flask import Blueprint, jsonify, request
import os
import json

map_bp = Blueprint("map", __name__, url_prefix="/api/map")


def _positions_path() -> str:
    # Locate the frontend map positions JSON relative to this file
    here = os.path.dirname(os.path.abspath(__file__))
    # backend/routes -> ../../frontend/src/components/Map/mapd.json
    path = os.path.join(here, "..", "..", "frontend", "src", "components", "Map", "mapd.json")
    return os.path.normpath(path)


@map_bp.get("/positions")
def get_positions():
    path = _positions_path()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data), 200
    except FileNotFoundError:
        return jsonify({"error": "mapd.json not found", "path": path}), 404


@map_bp.post("/positions")
def update_position():
    payload = request.get_json(silent=True) or {}
    team = payload.get("team")
    top = payload.get("top")
    left = payload.get("left")

    if not team or top is None or left is None:
        return jsonify({"error": "Required fields: team, top, left"}), 400

    path = _positions_path()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return jsonify({"error": "mapd.json not found", "path": path}), 404

    if team not in data:
        return jsonify({"error": f"Unknown team: {team}"}), 404

    # Normalize numeric inputs to percentage strings with one decimal
    try:
        top_num = float(str(top).replace("%", ""))
        left_num = float(str(left).replace("%", ""))
    except ValueError:
        return jsonify({"error": "top/left must be numeric percentages"}), 400

    top_num = max(0.0, min(100.0, top_num))
    left_num = max(0.0, min(100.0, left_num))

    entry = data[team]
    entry["top"] = f"{top_num:.1f}%"
    entry["left"] = f"{left_num:.1f}%"
    data[team] = entry

    # Write back formatted JSON to keep the repo tidy
    tmp_path = path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp_path, path)

    return jsonify({"ok": True, "team": team, "top": entry["top"], "left": entry["left"]}), 200

