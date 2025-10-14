import os
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup, Comment

URL = "https://fbref.com/en/comps/9/2017-2018/passing/2017-2018-Premier-League-Stats"
OUTDIR = "fbref_csv"
YEAR = "2018"

def sanitize(name: str) -> str:
    name = name.strip().lower()
    name = re.sub(r"\s+", "_", name)
    name = re.sub(r"[^a-z0-9._-]", "", name)
    return name or "table"

def flatten_columns(df: pd.DataFrame) -> pd.DataFrame:
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [
            " ".join([str(x) for x in tup if str(x) != "nan"]).strip()
            for tup in df.columns.values
        ]
    return df

def add_from_html(html_chunk: str, tables: dict):
    chunk = BeautifulSoup(html_chunk, "lxml")
    for tbl in chunk.select("table"):
        key = tbl.get("id") or (tbl.find("caption").get_text(strip=True) if tbl.find("caption") else None)
        if not key:
            key = f"table_{len(tables)+1}"
        try:
            df = pd.read_html(str(tbl))[0]
            df = df.dropna(how="all").dropna(axis=1, how="all")
            df = flatten_columns(df)
            k = sanitize(key)
            i = 2
            while k in tables:  # avoid overwriting
                k = f"{sanitize(key)}_{i}"
                i += 1
            tables[k] = df
        except Exception:
            pass

def scrape_fbref_tables(url: str) -> dict:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")

    tables = {}
    # visible tables
    add_from_html(str(soup), tables)
    # hidden tables inside comments
    for c in soup.find_all(string=lambda t: isinstance(t, Comment)):
        if "<table" in c:
            add_from_html(str(c), tables)
    return tables

if __name__ == "__main__":
    print(f"Fetching: {URL}")
    os.makedirs(OUTDIR, exist_ok=True)
    tables = scrape_fbref_tables(URL)

    if not tables:
        print("No tables found.")
    else:
        for name, df in tables.items():
            fname = f"{name}_{YEAR}.csv"
            path = os.path.join(OUTDIR, fname)
            df.to_csv(path, index=False)
            print(f"Saved: {path}")
        print(f"\nDone. Saved {len(tables)} tables into {OUTDIR}/")