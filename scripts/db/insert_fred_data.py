# scripts/db/insert_fred_data.py

import os
import pandas as pd
from sqlalchemy import text
from scripts.db.db_connect import engine

# Map CSV files to indicators
fred_files = {
    "CPI": "data/raw/fred_cpiaucns.csv",
    "GDP": "data/raw/fred_gdp.csv",
    "Unemployment": "data/raw/fred_unrate.csv",
    "CLI": "data/raw/fred_usslind.csv"
}

# Load and insert each indicator
with engine.connect() as conn:
    for indicator, file_path in fred_files.items():
        df = pd.read_csv(file_path, parse_dates=["date"])
        df["indicator"] = indicator  # Add indicator column

        for _, row in df.iterrows():
            conn.execute(
                text("""
                    INSERT INTO fred_indicators (date, indicator, value)
                    VALUES (:date, :indicator, :value)
                """),
                {
                    "date": row["date"],
                    "indicator": row["indicator"],
                    "value": row["value"]
                }
            )

print("✅ Inserted all FRED indicators into fred_indicators table.")
