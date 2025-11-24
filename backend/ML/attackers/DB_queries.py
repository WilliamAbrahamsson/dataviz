import sqlite3
import pandas as pd
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "instance" / "mydatabase.db"

def get_conn(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def labeled_seasons(db_path=DB_PATH,
                    season_table="player_season",
                    valuation_table="player_valuation"):

    conn = sqlite3.connect(db_path)

    df_seasons = pd.read_sql_query(f"SELECT * FROM {season_table}", conn)
    df_vals = pd.read_sql_query(f"SELECT * FROM {valuation_table}", conn, parse_dates=["date"])
    conn.close()


    orig_season_cols = list(df_seasons.columns)

    def season_end(code):
        try:
            start_year = int(str(code)[:4])
            return pd.Timestamp(datetime(start_year + 1, 6, 1))
        except Exception:
            return pd.NaT

    df_seasons = df_seasons.copy()
    df_seasons["season_end_date"] = df_seasons["year_code"].apply(season_end)
    df_seasons = df_seasons[df_seasons["season_end_date"].notna()].copy()

    # drop invalid
    df_vals["date"] = pd.to_datetime(df_vals["date"], errors="coerce")
    df_vals = df_vals.dropna(subset=["date"]).copy()


    df_vals = df_vals[["player_id", "date", "amount"]].copy()


    matched_parts = []

    player_ids = df_seasons["player_id"].dropna().unique()

    for pid in player_ids:
        # per-player 
        s = df_seasons[df_seasons["player_id"] == pid].sort_values("season_end_date")
        v = df_vals[df_vals["player_id"] == pid].sort_values("date")

        if v.empty:
            continue

        m = pd.merge_asof(
            left=s,
            right=v,
            left_on="season_end_date",
            right_on="date",
            direction="forward",
            suffixes=("", "_val")
        )
        matched_parts.append(m)

    result = pd.concat(matched_parts, ignore_index=True, sort=False)

    result = result.rename(columns={"amount": "valuation_amount"})
    result = result.dropna(subset=["valuation_amount"])
    result = result.drop(columns=["season_end_date", "date"], errors="ignore")

    return result[orig_season_cols + ["valuation_amount"]].reset_index(drop=True)
