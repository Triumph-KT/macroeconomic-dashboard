"""
Author: Triumph Kia Teh
Date: March 24, 2025
Description:
    Utility module to fetch macroeconomic time-series data from FRED API.
    Handles saving each series as a CSV and producing a combined dataset.
"""

import os
import requests
import pandas as pd
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
FRED_API_KEY = os.getenv("FRED_API_KEY")

def fetch_fred_series(series_id, start_date="2010-01-01", output_path=None):
    """Fetch a single FRED series and save to CSV."""
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "observation_start": start_date
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"❌ Error fetching {series_id}: {response.status_code}")
        return

    data = response.json()
    observations = data.get("observations", [])
    if not observations:
        print(f"⚠️ No data found for series {series_id}")
        return

    df = pd.DataFrame(observations)
    df = df[["date", "value"]].dropna()
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna()

    if output_path is None:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        output_path = os.path.join(base_dir, "data", "raw", f"fred_{series_id.lower()}.csv")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"✅ Saved {series_id} to {output_path}")


def fetch_all_fred_data(series_ids=["CPIAUCNS", "GDP", "UNRATE", "USSLIND"]):
    """Fetch all series and save combined cleaned dataset to data/processed."""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    raw_dir = os.path.join(base_dir, 'data', 'raw')
    processed_dir = os.path.join(base_dir, 'data', 'processed')
    os.makedirs(processed_dir, exist_ok=True)

    all_dfs = []

    for series_id in series_ids:
        fetch_fred_series(series_id)
        path = os.path.join(raw_dir, f"fred_{series_id.lower()}.csv")
        if os.path.exists(path):
            df = pd.read_csv(path, parse_dates=["date"])
            df["indicator"] = series_id
            all_dfs.append(df)

    if all_dfs:
        combined = pd.concat(all_dfs).dropna()
        combined = combined[["date", "indicator", "value"]]
        combined.sort_values(by=["indicator", "date"], inplace=True)

        output_path = os.path.join(processed_dir, "fred_combined.csv")
        combined.to_csv(output_path, index=False)
        print(f"📦 Combined FRED data saved to {output_path}")
        return combined
    else:
        print("⚠️ No FRED data available to combine.")
        return None
