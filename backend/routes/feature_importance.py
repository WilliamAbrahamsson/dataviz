import json
import os
from flask import Blueprint, jsonify

feature_importance_bp = Blueprint(
    "feature_importance",
    __name__,
    url_prefix="/api/feature-importance",
)


def _models_dir() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    # backend/routes -> ../ML/models
    return os.path.normpath(os.path.join(here, "..", "ML", "models"))


def _load_importance(filename: str):
    path = os.path.join(_models_dir(), filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f), path, None
    except FileNotFoundError:
        return None, path, f"{filename} not found"
    except json.JSONDecodeError as exc:
        return None, path, f"Invalid JSON in {filename}: {exc}"


@feature_importance_bp.get("/attackers")
def get_attackers_importance():
    data, path, error = _load_importance("attackers_shap_importance.json")
    if error:
        return jsonify({"error": error, "path": path}), 404
    return jsonify(data), 200


@feature_importance_bp.get("/midfielders")
def get_midfielders_importance():
    data, path, error = _load_importance("midfielder_shap_importance.json")
    if error:
        return jsonify({"error": error, "path": path}), 404
    return jsonify(data), 200


@feature_importance_bp.get("/defenders")
def get_defenders_importance():
    data, path, error = _load_importance("defenders_shap_importance.json")
    if error:
        return jsonify({"error": error, "path": path}), 404
    return jsonify(data), 200
