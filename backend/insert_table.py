#!/usr/bin/env python3
import json
import sqlite3
import sys
import re
from pathlib import Path

# --------------------------
# Utilities
# --------------------------

def column_exists(conn, table, col):
    cur = conn.execute(f"PRAGMA table_info({table})")
    return any(r[1] == col for r in cur.fetchall())

def ensure_index(conn, name, sql):
    # Create if missing (SQLite doesn't have CREATE INDEX IF NOT EXISTS on older versions)
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='index' AND name=?", (name,))
    if not cur.fetchone():
        conn.execute(sql)

def ensure_table(conn, name, create_sql):
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,))
    if not cur.fetchone():
        conn.executescript(create_sql)

def to_num_unit(val):
    """Return (value_num, value_text, unit)."""
    if val is None:
        return (None, None, None)
    if isinstance(val, (int, float)):
        return (float(val), str(val), None)
    s = str(val).strip()
    unit = None
    if s.endswith('%'):
        unit = '%'
        s = s[:-1].strip()
    s_clean = s.replace(',', '')
    try:
        return (float(s_clean), str(val), unit)
    except ValueError:
        return (None, str(val), unit)

def norm_key(k):
    if not k:
        return None
    k = k.strip().lower()
    k = re.sub(r'\s+', '_', k)
    k = re.sub(r'[^\w%]+', '_', k)
    k = re.sub(r'_+', '_', k).strip('_')
    return k or None

def split_nation(s):
    # "ie IRL" -> ("ie", "IRL")
    if not s:
        return (None, None)
    parts = str(s).split()
    if len(parts) >= 2:
        return (parts[0], parts[1])
    return (None, parts[0])

# Map JSON "standard" fields -> player_season columns
STANDARD_TO_SEASON = {
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

# --------------------------
# Schema bootstrap/patch
# --------------------------

def ensure_schema(conn):
    conn.execute("PRAGMA foreign_keys=ON")

    # Core tables (created if missing; matches your current design)
    ensure_table(conn, "player", """
    CREATE TABLE IF NOT EXISTS player (
      id INTEGER PRIMARY KEY,
      name TEXT,
      nationality TEXT,
      birth_year INTEGER,
      transfermarkt_player_id INTEGER UNIQUE,
      short_name TEXT
    );
    """)

    ensure_table(conn, "player_season", """
    CREATE TABLE IF NOT EXISTS player_season (
      id INTEGER PRIMARY KEY,
      player_id INTEGER NOT NULL,
      year_code TEXT,
      age REAL,
      position TEXT,
      club TEXT,
      matches_played REAL,
      matches_started REAL,
      minutes_played REAL,
      goals_scored REAL,
      assists_made REAL,
      goals_plus_assists REAL,
      goals_excluding_penalties REAL,
      penalty_goals REAL,
      penalty_attempts REAL,
      yellow_cards REAL,
      red_cards REAL,
      expected_goals REAL,
      non_penalty_expected_goals REAL,
      expected_assists REAL,
      combined_non_penalty_expected_goal_contributions REAL,
      progressive_carries REAL,
      progressive_passes REAL,
      progressive_receptions REAL,
      FOREIGN KEY(player_id) REFERENCES player(id)
    );
    """)

    ensure_table(conn, "player_valuation", """
    CREATE TABLE IF NOT EXISTS player_valuation (
      id INTEGER PRIMARY KEY,
      player_id INTEGER NOT NULL,
      date TEXT,
      amount REAL,
      FOREIGN KEY(player_id) REFERENCES player(id)
    );
    """)

    ensure_table(conn, "stat_category", """
    CREATE TABLE IF NOT EXISTS stat_category (
      id INTEGER PRIMARY KEY,
      code TEXT UNIQUE NOT NULL
    );
    """)

    ensure_table(conn, "player_season_stat", """
    CREATE TABLE IF NOT EXISTS player_season_stat (
      id INTEGER PRIMARY KEY,
      player_season_id INTEGER NOT NULL,
      category_id INTEGER NOT NULL,
      key_raw TEXT NOT NULL,
      key_norm TEXT,
      value_num REAL,
      value_text TEXT,
      unit TEXT,
      UNIQUE (player_season_id, category_id, key_raw),
      FOREIGN KEY(player_season_id) REFERENCES player_season(id),
      FOREIGN KEY(category_id) REFERENCES stat_category(id)
    );
    """)

    # Auto-patch: add missing columns the loader uses
    if not column_exists(conn, "player", "nationality_iso2"):
        conn.execute("ALTER TABLE player ADD COLUMN nationality_iso2 TEXT;")
    if not column_exists(conn, "player", "nationality_fifa"):
        conn.execute("ALTER TABLE player ADD COLUMN nationality_fifa TEXT;")
    if not column_exists(conn, "player_season", "ninety_min_equivalents"):
        conn.execute("ALTER TABLE player_season ADD COLUMN ninety_min_equivalents REAL;")

    # Needed unique indexes for upserts
    ensure_index(conn, "ux_player_season_player_year",
                 "CREATE UNIQUE INDEX ux_player_season_player_year ON player_season(player_id, year_code);")
    ensure_index(conn, "ux_val_player_date",
                 "CREATE UNIQUE INDEX ux_val_player_date ON player_valuation(player_id, date);")

    # Helpful join index
    ensure_index(conn, "ix_player_season_player",
                 "CREATE INDEX ix_player_season_player ON player_season(player_id);")

    # Seed categories
    conn.executemany("INSERT OR IGNORE INTO stat_category(code) VALUES (?)",
                     [('offensive',), ('defensive',), ('standard',)])
    conn.commit()

def get_category_id(conn, code):
    cur = conn.execute("SELECT id FROM stat_category WHERE code=?", (code,))
    row = cur.fetchone()
    if row:
        return row[0]
    conn.execute("INSERT INTO stat_category(code) VALUES (?)", (code,))
    return conn.execute("SELECT last_insert_rowid()").fetchone()[0]

# --------------------------
# Upserts
# --------------------------

def upsert_player(conn, p):
    cur = conn.execute("""
        INSERT INTO player (name, short_name, nationality, birth_year,
                            transfermarkt_player_id, nationality_iso2, nationality_fifa)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(transfermarkt_player_id) DO UPDATE SET
            name=excluded.name,
            short_name=excluded.short_name,
            nationality=excluded.nationality,
            birth_year=excluded.birth_year,
            nationality_iso2=excluded.nationality_iso2,
            nationality_fifa=excluded.nationality_fifa
    """, (
        p.get("name"),
        p.get("short_name"),
        p.get("nationality"),
        p.get("birth_year"),
        p.get("transfermarkt_player_id"),
        p.get("nationality_iso2"),
        p.get("nationality_fifa"),
    ))
    # Resolve id (works whether insert or update)
    if p.get("transfermarkt_player_id") is not None:
        row = conn.execute("SELECT id FROM player WHERE transfermarkt_player_id=?",
                           (p["transfermarkt_player_id"],)).fetchone()
    else:
        row = conn.execute("SELECT id FROM player WHERE name=? AND short_name IS ?", 
                           (p.get("name"), p.get("short_name"))).fetchone()
    return row[0] if row else conn.execute("SELECT last_insert_rowid()").fetchone()[0]

def upsert_player_season(conn, player_id, year_code, meta):
    cols = [
        "age","position","club",
        "matches_played","matches_started","minutes_played",
        "goals_scored","assists_made","goals_plus_assists",
        "goals_excluding_penalties","penalty_goals","penalty_attempts",
        "yellow_cards","red_cards",
        "expected_goals","non_penalty_expected_goals","expected_assists",
        "combined_non_penalty_expected_goal_contributions",
        "progressive_carries","progressive_passes","progressive_receptions",
        "ninety_min_equivalents"
    ]
    placeholders = ",".join("?" for _ in cols)
    assignments = ",".join([f"{c}=excluded.{c}" for c in cols])
    values = [meta.get(c) for c in cols]
    conn.execute(f"""
        INSERT INTO player_season (player_id, year_code, {",".join(cols)})
        VALUES (?, ?, {placeholders})
        ON CONFLICT(player_id, year_code) DO UPDATE SET {assignments}
    """, (player_id, year_code, *values))
    row = conn.execute("SELECT id FROM player_season WHERE player_id=? AND year_code=?",
                       (player_id, year_code)).fetchone()
    return row[0]

def upsert_stat(conn, player_season_id, category_id, key_raw, val):
    vn, vt, unit = to_num_unit(val)
    kn = norm_key(key_raw)
    conn.execute("""
        INSERT INTO player_season_stat
        (player_season_id, category_id, key_raw, key_norm, value_num, value_text, unit)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(player_season_id, category_id, key_raw) DO UPDATE SET
          key_norm=excluded.key_norm,
          value_num=excluded.value_num,
          value_text=excluded.value_text,
          unit=excluded.unit
    """, (player_season_id, category_id, key_raw, kn, vn, vt, unit))

def upsert_valuations(conn, player_id, history):
    for row in history or []:
        date = row.get("date")
        value = row.get("value")
        if not date or value is None:
            continue
        conn.execute("""
            INSERT INTO player_valuation (player_id, date, amount)
            VALUES (?, ?, ?)
            ON CONFLICT(player_id, date) DO UPDATE SET amount=excluded.amount
        """, (player_id, date, float(value)))

# --------------------------
# ETL helpers
# --------------------------

def extract_meta_from_standard(standard):
    meta = {}
    for k, col in STANDARD_TO_SEASON.items():
        if k in standard:
            vn, _, _ = to_num_unit(standard[k])
            meta[col] = vn
    # Position/club/age may live under these "Unnamed" keys
    pos = standard.get("Unnamed: 3_level_0 Pos") or standard.get("Pos")
    club = standard.get("Unnamed: 4_level_0 Squad") or standard.get("Squad")
    age = standard.get("Unnamed: 5_level_0 Age") or standard.get("Age")
    if pos: meta["position"] = pos
    if club: meta["club"] = club
    if age is not None:
        try: meta["age"] = float(str(age).strip())
        except: pass
    return meta

def derive_player_nat_from_blocks(blocks):
    for b in blocks:
        n = b.get("Unnamed: 2_level_0 Nation") or b.get("Nation")
        if n:
            iso2, fifa = split_nation(n)
            return {"nationality": fifa, "nationality_iso2": iso2, "nationality_fifa": fifa}
    return {}

def process_player(conn, pobj):
    # Prepare base player row (transfermarkt_player_id, birth_year may be absent in your JSON — that’s ok)
    base = {
        "name": pobj.get("name"),
        "short_name": pobj.get("short_name"),
        "nationality": pobj.get("nationality"),
        "birth_year": pobj.get("birth_year"),
        "transfermarkt_player_id": pobj.get("transfermarkt_player_id"),
        "nationality_iso2": None,
        "nationality_fifa": None,
    }

    seasons = pobj.get("season_stats") or {}

    if not base.get("birth_year"):
        for _, cat in seasons.items():
            # check all three categories for a "Born" field
            for b in (
                cat.get("standard") or {},
                cat.get("offensive") or {},
                cat.get("defensive") or {},
            ):
                born = b.get("Unnamed: 6_level_0 Born") or b.get("Born")
                if born:
                    try:
                        base["birth_year"] = int(float(str(born).strip()))
                        break
                    except ValueError:
                        pass
            if base.get("birth_year"):
                break

    # Try to derive nationality from first populated season we see
    for _, cat in seasons.items():
        if isinstance(cat, dict):
            derived = derive_player_nat_from_blocks([
                cat.get("standard", {}), cat.get("offensive", {}), cat.get("defensive", {})
            ])
            for k, v in derived.items():
                if v and not base.get(k):
                    base[k] = v
            if base.get("nationality_fifa"):
                break

    player_id = upsert_player(conn, base)

    # Valuations
    upsert_valuations(conn, player_id, pobj.get("evaluation_history"))

    # Category ids
    cat_id = {
        "offensive": get_category_id(conn, "offensive"),
        "defensive": get_category_id(conn, "defensive"),
        "standard": get_category_id(conn, "standard"),
    }

    # Seasons
    for year_code, cat in seasons.items():
        offensive = cat.get("offensive") or {}
        defensive = cat.get("defensive") or {}
        standard  = cat.get("standard")  or {}

        # wide meta from standard (fallbacks handled inside)
        meta = extract_meta_from_standard(standard)
        # fallback position/club/age from other blocks if still missing
        if "position" not in meta:
            meta["position"] = offensive.get("Unnamed: 3_level_0 Pos") or defensive.get("Unnamed: 3_level_0 Pos")
        if "club" not in meta:
            meta["club"] = offensive.get("Unnamed: 4_level_0 Squad") or defensive.get("Unnamed: 4_level_0 Squad")
        if "age" not in meta:
            age = offensive.get("Unnamed: 5_level_0 Age") or defensive.get("Unnamed: 5_level_0 Age")
            if age is not None:
                try: meta["age"] = float(str(age).strip())
                except: pass

        psid = upsert_player_season(conn, player_id, year_code, meta)

        # insert all key/values for each category
        for code, block in (("offensive", offensive), ("defensive", defensive), ("standard", standard)):
            if not block:
                continue
            cid = cat_id[code]
            for k, v in block.items():
                if k.lower() == "matches":
                    continue
                upsert_stat(conn, psid, cid, k, v)

def load_json(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, dict) and "name" in data and "season_stats" in data:
        return [data]
    if isinstance(data, list):
        return data
    raise ValueError("JSON must be a player object or a list of player objects.")

# --------------------------
# Main
# --------------------------

def main():
    json_path = "players_with_season_stats.json"
    db_path = "instance/mydatabase.db"
    players = load_json(json_path)

    conn = sqlite3.connect(db_path)
    try:
        ensure_schema(conn)
        for p in players:
            process_player(conn, p)
        conn.commit()
        print(f"Imported {len(players)} player(s) into {db_path}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
