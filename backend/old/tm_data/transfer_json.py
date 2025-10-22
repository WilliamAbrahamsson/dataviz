# populate_sqlite.py
import sys
import json
import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

# ---------- Helpers ----------
def to_int(v) -> Optional[int]:
    if v is None or v == "":
        return None
    try:
        # Handle strings like "+0.5" or "0.0" by casting to float first
        if isinstance(v, str):
            v = v.strip().replace(",", "")
            if v in {"Matches"}:
                return None
        f = float(v)
        # If it's an integer-like float, return int
        if f.is_integer():
            return int(f)
        return int(round(f))
    except Exception:
        return None

def to_float(v) -> Optional[float]:
    if v is None or v == "":
        return None
    try:
        if isinstance(v, str):
            vs = v.strip().replace(",", "")
            if vs.endswith("%"):
                return float(vs[:-1])
            if vs in {"Matches"}:
                return None
            return float(vs)
        return float(v)
    except Exception:
        return None

def parse_nation(nation_str: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """
    Input examples: 'ie IRL', 'eng ENG', 'ie  IRL' (double spaces), or None.
    Returns (iso2, fifa)
    """
    if not nation_str:
        return (None, None)
    parts = nation_str.strip().split()
    if len(parts) == 2:
        iso2, fifa = parts
        iso2 = iso2.upper()
        fifa = fifa.upper()
        if len(iso2) == 2 and len(fifa) == 3:
            return (iso2, fifa)
    # Fallback: try last 3 as FIFA
    if len(nation_str.strip()) >= 3:
        fifa = nation_str.strip()[-3:].upper()
        return (None, fifa)
    return (None, None)

def pick_first(*vals):
    for v in vals:
        if v is not None:
            return v
    return None

def clean_position(pos: Optional[str]) -> Optional[str]:
    if not pos:
        return None
    return pos.replace(",", "/").strip()

# ---------- Mapping ----------
# Keys from 'standard'
STANDARD_MAP = {
    "Playing Time MP": "matches_played",
    "Playing Time Starts": "matches_started",
    "Playing Time Min": "minutes_played",
    "Playing Time 90s": "ninety_min_equivalents",

    "Performance Gls": "goals_scored",
    "Performance Ast": "assists_made",
    "Performance G+A": "goals_plus_assists",
    "Performance G-PK": "goals_excluding_penalties",
    "Performance PK": "penalty_goals",
    "Performance PKatt": "penalty_attempts",
    "Performance CrdY": "yellow_cards",
    "Performance CrdR": "red_cards",

    "Expected xG": "expected_goals",
    "Expected npxG": "non_penalty_expected_goals",
    "Expected xAG": "expected_assists",
    "Expected npxG+xAG": "combined_non_penalty_expected_goal_contributions",

    "Progression PrgC": "progressive_carries",
    "Progression PrgP": "progressive_passes",
    "Progression PrgR": "progressive_receptions",
}

# Keys from 'offensive' (passing detail, key passes, final third, etc)
OFFENSIVE_MAP = {
    "Total Cmp": "passes_completed",
    "Total Att": "passes_attempted",
    "Total Cmp%": "pass_completion_pct",
    "Total TotDist": "pass_total_distance",
    "Total PrgDist": "pass_progressive_distance",

    "Short Cmp": "short_passes_completed",
    "Short Att": "short_passes_attempted",
    "Short Cmp%": "short_passes_completion_pct",

    "Medium Cmp": "medium_passes_completed",
    "Medium Att": "medium_passes_attempted",
    "Medium Cmp%": "medium_passes_completion_pct",

    "Long Cmp": "long_passes_completed",
    "Long Att": "long_passes_attempted",
    "Long Cmp%": "long_passes_completion_pct",

    # "Unknown" / "Unnamed" keys mapped to real columns:
    "Unnamed: 26_level_0 KP": "key_passes",
    "Unnamed: 27_level_0 1/3": "passes_into_final_third",
    "Unnamed: 28_level_0 PPA": "passes_into_penalty_area",
    "Unnamed: 29_level_0 CrsPA": "crosses_into_pa",
    # Some tables also include PrgP here; prefer STANDARD_MAP if present, but keep as fallback
    "Unnamed: 30_level_0 PrgP": "progressive_passes",
}

# Keys from 'defensive'
DEFENSIVE_MAP = {
    "Tackles Tkl": "tackles",
    "Tackles TklW": "tackles_won",
    "Tackles Def 3rd": "tackles_def_3rd",
    "Tackles Mid 3rd": "tackles_mid_3rd",
    "Tackles Att 3rd": "tackles_att_3rd",

    "Challenges Tkl": "challenges_tackles",
    "Challenges Att": "challenges_attempted",
    "Challenges Tkl%": "challenges_tackle_pct",
    "Challenges Lost": "challenges_lost",

    "Blocks Blocks": "blocks",
    "Blocks Sh": "blocks_shots",
    "Blocks Pass": "blocks_passes",

    # "Unknown" / "Unnamed" keys mapped:
    "Unnamed: 20_level_0 Int": "interceptions",
    "Unnamed: 21_level_0 Tkl+Int": "tackles_plus_interceptions",
    "Unnamed: 22_level_0 Clr": "clearances",
    "Unnamed: 23_level_0 Err": "errors_leading_to_shot",
}

# "Header" fields (show up within each section) that help fill player_season metadata
HEADER_KEYS = {
    "Unnamed: 2_level_0 Nation": "nation",
    "Unnamed: 3_level_0 Pos": "position",
    "Unnamed: 4_level_0 Squad": "club",
    "Unnamed: 5_level_0 Age": "age",
    "Unnamed: 6_level_0 Born": "born_year",
}

def extract_section(section: Dict[str, Any], mapping: Dict[str, str]) -> Dict[str, Any]:
    out = {}
    for raw_key, col in mapping.items():
        v = section.get(raw_key)
        if v is None:
            continue
        # percentages and numeric values → floats
        out[col] = to_float(v)
    return out

def extract_headers(section: Dict[str, Any]) -> Dict[str, Any]:
    out = {}
    for raw_key, col in HEADER_KEYS.items():
        if raw_key in section:
            if col in {"age"}:
                out[col] = to_float(section[raw_key])
            elif col in {"born_year"}:
                out[col] = to_int(section[raw_key])
            else:
                out[col] = section[raw_key]
    return out

def merge_stats(standard: Dict[str, Any], offensive: Dict[str, Any], defensive: Dict[str, Any]) -> Dict[str, Any]:
    data = {}
    data.update(extract_section(standard, STANDARD_MAP))
    # Only fill from offensive if missing (standard takes precedence where both exist)
    off_mapped = extract_section(offensive, OFFENSIVE_MAP)
    for k, v in off_mapped.items():
        if data.get(k) is None:
            data[k] = v
    def_mapped = extract_section(defensive, DEFENSIVE_MAP)
    data.update({k: v for k, v in def_mapped.items() if v is not None})
    # Headers (meta fields possibly needed in player_season row)
    headers = {}
    for sec in (standard, offensive, defensive):
        headers.update({k: v for k, v in extract_headers(sec).items() if v is not None})
    return data, headers

def has_any_stats(mapped: Dict[str, Any]) -> bool:
    # Consider non-meta numeric columns only
    return any(v is not None for v in mapped.values())

# ---------- DB ops ----------
def get_conn(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def get_or_create_player(conn: sqlite3.Connection, name: str, short_name: Optional[str], birth_year: Optional[int],
                         iso2: Optional[str], fifa: Optional[str]) -> int:
    # Try to find existing by (name, birth_year). If birth_year unknown, fall back to name only.
    cur = conn.cursor()
    if birth_year is not None:
        cur.execute(
            "SELECT id FROM player WHERE name = ? AND birth_year = ?",
            (name, birth_year),
        )
        row = cur.fetchone()
        if row:
            pid = row[0]
            # Best-effort update missing nationality/short_name if null
            cur.execute(
                """UPDATE player
                   SET short_name = COALESCE(short_name, ?),
                       nationality_iso2 = COALESCE(nationality_iso2, ?),
                       nationality_fifa = COALESCE(nationality_fifa, ?)
                   WHERE id = ?""",
                (short_name, iso2, fifa, pid),
            )
            conn.commit()
            return pid
    else:
        cur.execute(
            "SELECT id FROM player WHERE name = ? AND birth_year IS NULL",
            (name,),
        )
        row = cur.fetchone()
        if row:
            pid = row[0]
            cur.execute(
                """UPDATE player
                   SET short_name = COALESCE(short_name, ?),
                       nationality_iso2 = COALESCE(nationality_iso2, ?),
                       nationality_fifa = COALESCE(nationality_fifa, ?)
                   WHERE id = ?""",
                (short_name, iso2, fifa, pid),
            )
            conn.commit()
            return pid

    # Insert new
    cur.execute(
        """INSERT INTO player (name, birth_year, transfermarkt_player_id, short_name, nationality_iso2, nationality_fifa)
           VALUES (?, ?, NULL, ?, ?, ?)""",
        (name, birth_year, short_name, iso2, fifa),
    )
    conn.commit()
    return cur.lastrowid

def upsert_player_season(conn: sqlite3.Connection, player_id: int, year_code: str, nation: Optional[str],
                         position: Optional[str], club: Optional[str], age: Optional[float], born_year: Optional[float],
                         stats: Dict[str, Any]) -> None:
    if not has_any_stats(stats):
        return  # skip empty seasons

    # Build column list dynamically
    base_cols = [
        "player_id", "year_code", "nation", "position", "club", "age", "born_year"
    ]
    base_vals = [player_id, year_code, nation, position, club, age, born_year]

    stat_cols = list(stats.keys())
    cols = base_cols + stat_cols
    placeholders = ",".join(["?"] * len(cols))
    vals = base_vals + [stats[k] for k in stat_cols]

    # ON CONFLICT (player_id, year_code) → update
    set_clause = ",".join([f"{c}=excluded.{c}" for c in (["nation","position","club","age","born_year"] + stat_cols)])

    sql = f"""INSERT INTO player_season ({",".join(cols)})
              VALUES ({placeholders})
              ON CONFLICT(player_id, year_code) DO UPDATE SET
              {set_clause};"""
    conn.execute(sql, vals)

def insert_player_valuation(conn: sqlite3.Connection, player_id: int, date_str: str, amount: float):
    # Avoid duplicates by checking existence (player_id, date, amount)
    cur = conn.cursor()
    cur.execute(
        "SELECT 1 FROM player_valuation WHERE player_id = ? AND date = ? AND amount = ?",
        (player_id, date_str, amount),
    )
    if cur.fetchone():
        return
    cur.execute(
        "INSERT INTO player_valuation (player_id, date, amount) VALUES (?,?,?)",
        (player_id, date_str, amount),
    )

# ---------- Main ingest ----------
def main(json_path: Path, db_path: Path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    conn = get_conn(db_path)

    for player in data:
        name = player.get("name")
        short_name = player.get("short_name")

        # Probe seasons to infer birth_year and nationality if not on top-level
        inferred_birth_year: Optional[int] = None
        iso2_code: Optional[str] = None
        fifa_code: Optional[str] = None

        # Walk seasons to find first Nation/Born present
        seasons = player.get("season_stats", {}) or {}
        for season_code, sections in seasons.items():
            std = sections.get("standard", {}) or {}
            off = sections.get("offensive", {}) or {}
            deff = sections.get("defensive", {}) or {}
            headers = {}
            for sec in (std, off, deff):
                headers.update(extract_headers(sec))
            if inferred_birth_year is None and headers.get("born_year") is not None:
                inferred_birth_year = to_int(headers.get("born_year"))
            if iso2_code is None or fifa_code is None:
                header_nation = headers.get("nation")
                iso, fifa = parse_nation(header_nation)
                iso2_code = pick_first(iso2_code, iso)
                fifa_code = pick_first(fifa_code, fifa)
            if inferred_birth_year is not None and (iso2_code or fifa_code):
                break

        player_id = get_or_create_player(conn, name, short_name, inferred_birth_year, iso2_code, fifa_code)

        # Insert seasons
        for season_code, sections in seasons.items():
            std = sections.get("standard", {}) or {}
            off = sections.get("offensive", {}) or {}
            deff = sections.get("defensive", {}) or {}

            mapped_stats, headers = merge_stats(std, off, deff)

            # Season-level meta
            header_nation = headers.get("nation")
            iso2, fifa = parse_nation(header_nation)
            # Store FIFA 3-letter code in player_season.nation (it’s a free TEXT field)
            nation_for_row = fifa or iso2

            position = clean_position(headers.get("position"))
            club = headers.get("club")
            age = headers.get("age")
            born_year = headers.get("born_year")

            upsert_player_season(
                conn,
                player_id=player_id,
                year_code=season_code,
                nation=nation_for_row,
                position=position,
                club=club,
                age=age,
                born_year=born_year,
                stats=mapped_stats,
            )

        # Insert valuations
        for val in player.get("evaluation_history", []) or []:
            date_str = val.get("date")
            amount = to_float(val.get("value"))
            if date_str and amount is not None:
                insert_player_valuation(conn, player_id, date_str, float(amount))

        conn.commit()

    conn.close()

if __name__ == "__main__":

    json_path = Path("backend/old/players_with_season_stats.json")
    db_path = Path("backend/instance/mydatabase.db")
    if not json_path.exists():
        print(f"JSON file not found: {json_path}")
        sys.exit(1)
    if not db_path.exists():
        print(f"SQLite DB not found: {db_path}")
        sys.exit(1)
    main(json_path, db_path)
