import json
import os

# >>>> EDIT THESE <<<<
SOURCE_SQUADS_JSON = "tm_data/premier_league_squads_2024_25_complete.json"
TARGET_MISSING_JSON = "missing_players_market_values.json"

def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def normalize_name(s):
    return " ".join((s or "").strip().lower().split())

def extract_eval_history(player_obj):
    """Return list of {'date': 'YYYY-MM-DD', 'value': int} from the squad JSON player."""
    mv = (player_obj or {}).get("market_valuation") or {}
    # Prefer the explicit history list if present
    hist = mv.get("raw_api_response", {}).get("history")
    if not hist:
        hist = mv.get("complete_market_value_history") or []
    out = []
    for entry in hist:
        mv_obj = (entry or {}).get("marketValue") or {}
        date = mv_obj.get("determined") or mv_obj.get("date")
        val = mv_obj.get("value")
        if isinstance(date, str) and isinstance(val, int):
            out.append({"date": date, "value": val})
    # Deduplicate by date, keep last seen
    dedup = {}
    for p in out:
        dedup[p["date"]] = p["value"]
    return [{"date": d, "value": dedup[d]} for d in sorted(dedup)]

def extract_rows_from_squads(squads_json):
    """Yield simplified rows: {'name', 'short_name', 'evaluation_history'}."""
    teams = (squads_json or {}).get("teams", []) or []
    for team in teams:
        for p in team.get("squad", []) or []:
            info = p.get("player_info", {}) or {}
            name = info.get("name") or info.get("display_name") or info.get("short_name") or ""
            short_name = info.get("short_name") or info.get("name") or info.get("display_name") or ""
            history = extract_eval_history(p)
            yield {
                "name": name,
                "short_name": short_name or name,
                "evaluation_history": history,
            }

def append_to_missing(source_path, target_path):
    # Load inputs
    squads = load_json(source_path, default={})
    existing_list = load_json(target_path, default=[])  # this should be a list
    if not isinstance(existing_list, list):
        raise ValueError(f"Target file must be a JSON list. Got: {type(existing_list)}")

    # Build a set of existing names (normalized) to avoid duplicates
    existing_names = {normalize_name(item.get("name", "")) for item in existing_list}

    added = 0
    for row in extract_rows_from_squads(squads):
        key = normalize_name(row["name"])
        if not key or key in existing_names:
            continue
        existing_list.append(row)
        existing_names.add(key)
        added += 1

    # Save back
    os.makedirs(os.path.dirname(os.path.abspath(target_path)), exist_ok=True)
    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(existing_list, f, indent=2, ensure_ascii=False)

    print(f"✓ Appended {added} players. Total now: {len(existing_list)}")
    print(f"→ {target_path}")

if __name__ == "__main__":
    append_to_missing(SOURCE_SQUADS_JSON, TARGET_MISSING_JSON)
