import requests
import pandas as pd
from bs4 import BeautifulSoup, Comment

def scrape_fbref_tables(url: str):
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

    # 1) Normal tables
    for tbl in soup.select("table"):
        try:
            df = pd.read_html(str(tbl))[0]
            tables[tbl.get("id") or "unnamed"] = df
        except Exception:
            pass

    # 2) Tables inside HTML comments
    for c in soup.find_all(string=lambda text: isinstance(text, Comment)):
        if "<table" in c:
            try:
                df_list = pd.read_html(str(c))
                for i, df in enumerate(df_list):
                    key = f"comment_table_{i+1}"
                    tables[key] = df
            except Exception:
                pass

    return tables


if __name__ == "__main__":
    url = "https://fbref.com/en/comps/9/2024-2025/stats/2024-2025-Premier-League-Stats"
    tables = scrape_fbref_tables(url)

    if not tables:
        print("No tables found.")
    else:
        for name, df in tables.items():
            print("=" * 80)
            print(f"Table: {name} | Shape: {df.shape}")
            print(df.head())  # show first 5 rows
            print()
