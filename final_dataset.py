import os
import csv
import json
import unicodedata
from typing import Dict, Any, List, Optional

# --------- EDIT THESE PATHS ----------
EVAL_JSON = "tm_data/complete_tm_evaluation.json"     # your existing {name, short_name, evaluation_history}
CSV_DIR   = "FBref_data"                              # folder containing all stats_*.csv
OUTPUT_JSON = "players_with_season_stats.json"                # new file to write
# -------------------------------------

# Map category -> filename pattern (using season end year, e.g. 2018 => season 2017/18)
CATEGORY_PATTERNS = {
    "offensive": "stats_passing_{year}.csv",   # your "offensive" dataset
    "defensive": "stats_defense_{year}.csv",
    "standard":  "stats_standard_{year}.csv",
}

# Seasons 17/18 .. 24/25 => end years 2018..2025
SEASON_END_YEARS = list(range(2018, 2026))

def season_key(end_year: int) -> str:
    """2018 -> '2017/18'"""
    start = end_year - 1
    return f"{start}/{str(end_year)[-2:]}"

def normalize_name(name: str) -> str:
    """Case/space/diacritics-insensitive + strip non-alphanumeric for robust matching."""
    if not name:
        return ""
    s = unicodedata.normalize("NFKD", str(name).strip().lower())
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    # remove all non-alphanumeric
    s = "".join(ch for ch in s if ch.isalnum())
    return s

def detect_name_col(fieldnames: List[str]) -> Optional[str]:
    """Find the column that contains player names."""
    if not fieldnames:
        return None
    # 1) exact known headers
    preferred = [
        "Unnamed: 1_level_0 Player",  # your earlier header
        "Player",
        "Full Name",
        "Name",
        "Player Name",
    ]
    for p in preferred:
        if p in fieldnames:
            return p
    # 2) heuristic: any column containing 'player' or 'name'
    lower_map = {fn.lower(): fn for fn in fieldnames}
    for key in ["player", "name"]:
        for lf, orig in lower_map.items():
            if key in lf:
                return orig
    return None

def read_csv_index(csv_path: str) -> Dict[str, Dict[str, Any]]:
    """
    Read a CSV into index: norm_name -> {col: value, ...} (excluding the name column if found).
    Returns {} if file missing.
    """
    if not os.path.isfile(csv_path):
        return {}
    index: Dict[str, Dict[str, Any]] = {}
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return {}
        name_col = detect_name_col(reader.fieldnames)
        for row in reader:
            raw_name = (row.get(name_col) if name_col else None) or ""
            norm = normalize_name(raw_name)
            if not norm:
                continue
            # keep full row but drop the name column to avoid duplication
            slim = dict(row)
            if name_col in slim:
                del slim[name_col]
            index[norm] = slim
    return index

def build_stats_index(csv_dir: str) -> Dict[str, Dict[str, Dict[str, Dict[str, Any]]]]:
    """
    Build nested index:
      stats_index[season_key][category][norm_name] = {row_data}
    """
    stats_index: Dict[str, Dict[str, Dict[str, Dict[str, Any]]]] = {}
    for end_year in SEASON_END_YEARS:
        skey = season_key(end_year)
        stats_index.setdefault(skey, {})
        for category, pattern in CATEGORY_PATTERNS.items():
            filename = pattern.format(year=end_year)
            path = os.path.join(csv_dir, filename)
            stats_index[skey][category] = read_csv_index(path)
    return stats_index

def main():
    # Load evaluation list (simple list of players)
    with open(EVAL_JSON, "r", encoding="utf-8") as f:
        eval_players = json.load(f)
    if not isinstance(eval_players, list):
        raise ValueError("Evaluation JSON must be a list of players.")

    # Build per-season per-category indices from CSVs
    print("Indexing CSVs...")
    stats_index = build_stats_index(CSV_DIR)

    # Create output objects
    out_items: List[Dict[str, Any]] = []
    for p in eval_players:
        name = p.get("name", "")
        short_name = p.get("short_name", name)
        eval_hist = p.get("evaluation_history", [])

        norm = normalize_name(name) or normalize_name(short_name)
        # Prepare season stats skeleton
        season_stats: Dict[str, Dict[str, Dict[str, Any]]] = {}
        for end_year in SEASON_END_YEARS:
            skey = season_key(end_year)
            season_stats[skey] = {}
            for category in CATEGORY_PATTERNS.keys():
                row = stats_index.get(skey, {}).get(category, {}).get(norm)
                # If missing, leave as empty dict
                season_stats[skey][category] = row if isinstance(row, dict) else {}

        out_items.append({
            "name": name,
            "short_name": short_name,
            "season_stats": season_stats,
            "evaluation_history": eval_hist,
        })

    # Save
    os.makedirs(os.path.dirname(os.path.abspath(OUTPUT_JSON)) or ".", exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(out_items, f, indent=2, ensure_ascii=False)

    print(f"✓ Wrote {len(out_items)} players to {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
