# scripts/data_pipeline/fetch_yahoo_data.py

import yfinance as yf
import pandas as pd
import os

# Define the assets to fetch
ASSETS = {
    "sp500": "^GSPC",         # S&P 500 Index
    "bond10y": "^TNX",        # 10-Year Treasury Note Yield
    "gold": "GC=F",           # Gold Futures
    "oil": "CL=F",            # Crude Oil WTI Futures
    "eurusd": "EURUSD=X",     # EUR/USD Exchange Rate
    "reit_etf": "VNQ"         # Real Estate ETF (Vanguard)
}

# Output directory
output_dir = os.path.join("data", "raw", "yahoo")
os.makedirs(output_dir, exist_ok=True)

for label, symbol in ASSETS.items():
    print(f"⏳ Fetching {label.upper()} ({symbol})...")
    df = yf.download(symbol, start="2010-01-01", progress=False)

    if df.empty:
        print(f"⚠️ No data returned for {symbol}")
        continue

    df = df.reset_index()[["Date", "Close"]]
    df.columns = ["date", "adj_close"]

    output_path = os.path.join(output_dir, f"{label}.csv")
    df.to_csv(output_path, index=False)
    print(f"✅ Saved {label.upper()} to {output_path}")
