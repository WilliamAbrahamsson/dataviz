import requests
import csv
import json
import time
import re
from urllib.parse import urljoin
from typing import List, Dict, Any, Optional, Tuple

# -----------------------------
# CONFIG
# -----------------------------
INPUT_CSV = "missing_players.csv"          # uses column "Full Name"
OUTPUT_JSON = "missing_players_market_values.json"  # autosaves every 50
SAVE_EVERY = 50
REQUEST_SLEEP = 0.6

# API endpoints
TM_API_SEARCH = "https://tmapi-alpha.transfermarkt.technology/search"
TM_API_MV = "https://tmapi-alpha.transfermarkt.technology/player/{player_id}/market-value-history"

# For fallback ID lookup (only if API search misses)
SEARCH_URL = "https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche"
BASE_URL = "https://www.transfermarkt.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
}

# -----------------------------
# IO
# -----------------------------
def read_missing_players(csv_path: str) -> List[str]:
    names: List[str] = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if "Full Name" not in reader.fieldnames:
            raise ValueError(f"'Full Name' column not found. Got: {reader.fieldnames}")
        for row in reader:
            n = (row.get("Full Name") or "").strip()
            if n:
                names.append(n)
    return names

def save_progress(items: List[Dict[str, Any]], out_path: str):
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved {len(items)} players → {out_path}")

# -----------------------------
# ID LOOKUP
# -----------------------------
def extract_player_id_from_href(href: str) -> Optional[str]:
    if not href:
        return None
    m = re.search(r"/spieler/(\d+)", href)
    return m.group(1) if m else None

def search_player_id_api(full_name: str) -> Optional[str]:
    """
    Try Transfermarkt API search first (clean + fast).
    We query 'entityType=player' and pick the first exact-ish match.
    """
    try:
        params = {"query": full_name, "entityType": "player"}
        r = requests.get(TM_API_SEARCH, params=params, headers=HEADERS, timeout=15)
        r.raise_for_status()
        data = r.json()
        # Expected shapes seen in practice:
        # { "success": true, "data": { "players": [ { "id": "105470", "name": "...", ... }, ... ] } }
        players = []
        if isinstance(data, dict):
            dd = data.get("data") or {}
            if isinstance(dd, dict):
                players = dd.get("players") or dd.get("results") or []
        if not players:
            return None

        # simple heuristic: first result
        pid = str(players[0].get("id") or players[0].get("playerId") or "").strip()
        return pid or None
    except Exception:
        return None

def search_player_id_fallback(full_name: str) -> Optional[str]:
    """
    Fallback to quick-search webpage if API search didn't return anything.
    """
    try:
        r = requests.get(SEARCH_URL, params={"query": full_name}, headers=HEADERS, timeout=15)
        r.raise_for_status()
        # very light parse to find first link with /spieler/<id>
        matches = re.findall(r'href="([^"]+/spieler/\d+[^"]*)"', r.text)
        if not matches:
            return None
        for href in matches:
            pid = extract_player_id_from_href(href)
            if pid:
                return pid
        return None
    except Exception:
        return None

def get_player_id(full_name: str) -> Optional[str]:
    pid = search_player_id_api(full_name)
    if pid:
        return pid
    return search_player_id_fallback(full_name)

# -----------------------------
# MARKET VALUE (API)
# -----------------------------
def fetch_market_value_history_api(player_id: str) -> List[Dict[str, Any]]:
    """
    Call TM API for market value history and return [{"date": "YYYY-MM-DD", "value": int}, ...]
    """
    try:
        url = TM_API_MV.format(player_id=player_id)
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.raise_for_status()
        data = r.json()

        if not (isinstance(data, dict) and data.get("success") and "data" in data):
            return []

        mv = data["data"]
        history = mv.get("history") or []
        points: List[Dict[str, Any]] = []

        for entry in history:
            # Common shape:
            # {
            #   "marketValue": {"value": 30000000, "currency": "EUR", "determined": "2024-06-15", "compact": {...}},
            #   "age": 29, "clubId": "...", ...
            # }
            mv_obj = entry.get("marketValue") or {}
            val = mv_obj.get("value")
            date = mv_obj.get("determined") or mv_obj.get("date")
            if isinstance(val, int) and isinstance(date, str):
                points.append({"date": date, "value": val})

        # Sort & dedupe by date
        dedup = {}
        for p in points:
            dedup[p["date"]] = p["value"]
        out = [{"date": d, "value": dedup[d]} for d in sorted(dedup)]
        return out
    except Exception as e:
        # If API fails (e.g., rate limit), return empty to keep pipeline going
        return []

# -----------------------------
# MAIN PIPELINE
# -----------------------------
def process(input_csv: str, output_json: str):
    names = read_missing_players(input_csv)
    print(f"Found {len(names)} players in {input_csv}\n")

    results: List[Dict[str, Any]] = []

    for idx, full_name in enumerate(names, 1):
        print(f"[{idx}/{len(names)}] {full_name} → getting player ID...")
        pid = get_player_id(full_name)
        time.sleep(REQUEST_SLEEP)

        if not pid:
            print("   ✗ No player ID found (API+fallback).")
            results.append({
                "name": full_name,
                "short_name": full_name,
                "evaluation_history": []
            })
        else:
            print(f"   ✓ ID {pid} → fetching market value history (API)…")
            history = fetch_market_value_history_api(pid)
            time.sleep(REQUEST_SLEEP)
            print(f"   {'✓' if history else '⚠'} {len(history)} points")

            results.append({
                "name": full_name,        # keep CSV name (simple & consistent)
                "short_name": full_name,  # you can swap to a different source if you prefer
                "evaluation_history": history
            })

        # autosave
        if idx % SAVE_EVERY == 0:
            save_progress(results, output_json)

    save_progress(results, output_json)
    print("\nDone.")

# -----------------------------
# ENTRYPOINT
# -----------------------------
if __name__ == "__main__":
    process(INPUT_CSV, OUTPUT_JSON)
