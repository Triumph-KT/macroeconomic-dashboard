import argparse
import pandas as pd
from scripts.db.db_connect import engine
from sqlalchemy import text
import os

def load_worldbank():
    print("🌍 Loading World Bank data...")
    df = pd.read_csv("data/processed/worldbank_us_macro.csv", parse_dates=["date"])

    with engine.begin() as conn:
        conn.execute(text("DELETE FROM macro_indicators"))
        conn.execute(
            text("""
                INSERT INTO macro_indicators (
                    date, gdp_per_capita, inflation, population,
                    gov_exp_pct_gdp, unemployment_global
                )
                VALUES (:date, :gdp_per_capita, :inflation, :population, :gov_exp_pct_gdp, :unemployment_global)
            """),
            df.to_dict(orient='records')
        )

    print("✅ World Bank data inserted successfully.")

def load_fred():
    print("📦 Loading FRED data...")

    indicators = {
        "CPIAUCNS": "data/raw/fred/fred_cpiaucns.csv",
        "GDP": "data/raw/fred/fred_gdp.csv",
        "UNRATE": "data/raw/fred/fred_unrate.csv",
        "USSLIND": "data/raw/fred/fred_usslind.csv"
    }

    dfs = []
    for series_id, path in indicators.items():
        df = pd.read_csv(path, parse_dates=["date"])
        df["indicator"] = series_id
        df = df[["date", "indicator", "value"]].dropna()
        dfs.append(df)

    combined = pd.concat(dfs)

    with engine.begin() as conn:
        conn.execute(text("DELETE FROM fred_indicators"))
        conn.execute(
            text("""
                INSERT INTO fred_indicators (date, indicator, value)
                VALUES (:date, :indicator, :value)
            """),
            combined.to_dict(orient='records')
        )

    print("✅ FRED data inserted into fred_indicators.")

def load_yahoo():
    print("💹 Loading Yahoo Finance asset data...")

    yahoo_dir = "data/raw/yahoo"
    dfs = []

    for filename in os.listdir(yahoo_dir):
        if filename.endswith(".csv"):
            symbol = filename.replace(".csv", "").lower()
            path = os.path.join(yahoo_dir, filename)

            try:
                df = pd.read_csv(path)
                df.columns = [col.lower() for col in df.columns]

                if "date" not in df.columns or "adj_close" not in df.columns:
                    print(f"⚠️ Skipping {filename} (missing 'date' or 'adj close')")
                    continue

                df["date"] = pd.to_datetime(df["date"], errors="coerce")
                df = df[["date", "adj_close"]].dropna()
                df["symbol"] = symbol.upper()
                dfs.append(df)

            except Exception as e:
                print(f"⚠️ Failed to load {filename}: {e}")

    if not dfs:
        print("❌ No valid Yahoo Finance files found.")
        return

    combined = pd.concat(dfs, ignore_index=True)[["date", "symbol", "adj_close"]]

    with engine.begin() as conn:
        conn.execute(text("DELETE FROM yahoo_assets"))
        conn.execute(
            text("""
                INSERT INTO yahoo_assets (date, symbol, adj_close)
                VALUES (:date, :symbol, :adj_close)
            """),
            combined.to_dict(orient='records')
        )

    print("✅ Inserted Yahoo Finance asset data.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=str, choices=["worldbank", "fred", "yahoo"])
    args = parser.parse_args()

    if args.source == "worldbank":
        load_worldbank()
    elif args.source == "fred":
        load_fred()
    elif args.source == "yahoo":
        load_yahoo()
