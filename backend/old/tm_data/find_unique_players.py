import os
import glob
import json
import pandas as pd

def normalize_name(name):
    """Normalize names for comparison (lowercase, strip spaces)."""
    if pd.isna(name):
        return ""
    return str(name).strip().lower()

def load_json_player_names(json_path):
    """Load ALL variants of player names from the JSON file (display_name, name, short_name)."""
    import json
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    names = set()
    for team in data.get("teams", []):
        for player in team.get("squad", []):
            p = player.get("player_info", {}) or {}
            for key in ("display_name", "name", "short_name"):
                val = p.get(key)
                if val:
                    names.add(normalize_name(val))
    return names

def load_all_csv_players(folder_path):
    """Read all CSVs in the folder and combine them into one DataFrame."""
    all_files = glob.glob(os.path.join(folder_path, "*.csv"))
    if not all_files:
        raise FileNotFoundError(f"No CSV files found in {folder_path}")
    dfs = []
    for file in all_files:
        df = pd.read_csv(file)
        df["source_file"] = os.path.basename(file)
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True)

def find_missing_players(csv_folder, json_file, output_file):
    # Fixed column names as requested
    NAME_COL = "Unnamed: 1_level_0 Player"
    GAMES_COL = "Playing Time MP"

    # Load JSON player names
    json_names = load_json_player_names(json_file)
    print(f"Loaded {len(json_names)} player names from JSON file.")

    # Load CSVs
    all_players = load_all_csv_players(csv_folder)
    print(f"Loaded {len(all_players)} rows from CSV files.")

    # Check columns exist
    for col in [NAME_COL, GAMES_COL]:
        if col not in all_players.columns:
            raise ValueError(
                f"Column '{col}' not found in CSVs. "
                f"Available columns include: {list(all_players.columns)[:10]} ..."
            )

    # Normalize + filter
    all_players["norm_name"] = all_players[NAME_COL].apply(normalize_name)
    all_players[GAMES_COL] = pd.to_numeric(all_players[GAMES_COL], errors="coerce").fillna(0)

    # Exclude players with 1 or fewer games
    filtered = all_players[all_players[GAMES_COL] > 1]
    # Keep those NOT in JSON
    missing = filtered[~filtered["norm_name"].isin(json_names)]

    agg = (
        missing
        .groupby("norm_name", as_index=False)
        .agg({
            NAME_COL: "first",                 # keep the first spelling we saw
            GAMES_COL: "max",                  # highest MP
            "source_file": lambda s: ";".join(sorted(set(s)))  # all unique sources
        })
    )

    result = agg[[NAME_COL, GAMES_COL, "source_file"]]
    result.columns = ["Full Name", "Games Played", "Source File"]

    # Save result
    result.to_csv(output_file, index=False)
    print(f"✅ Found {len(result)} unique missing players.")
    print(f"📁 Saved to: {output_file}")

# --------------------------
# Edit these before running
# --------------------------
if __name__ == "__main__":
    csv_folder = "FBref_data"  # e.g., "C:/Users/you/Documents/csvs"
    json_file = "tm_data/premier_league_squads_2024_25_complete.json"
    output_file = "missing_players.csv"

    find_missing_players(csv_folder, json_file, output_file)
