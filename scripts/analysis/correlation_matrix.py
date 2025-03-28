# scripts/analysis/correlation_matrix.py

import pandas as pd
from sqlalchemy import create_engine
from scripts.db.db_connect import engine  # Use your existing DB connection

def load_and_prepare_data():
    # 1. Load data
    yahoo_df = pd.read_sql("SELECT * FROM yahoo_assets", engine, parse_dates=["date"])
    fred_df = pd.read_sql("SELECT * FROM fred_indicators", engine, parse_dates=["date"])
    wb_df = pd.read_sql("SELECT * FROM macro_indicators", engine, parse_dates=["date"])

    # 2. Resample to monthly
    yahoo_pivot = yahoo_df.pivot(index="date", columns="symbol", values="adj_close").resample("M").last()
    fred_pivot = fred_df.pivot(index="date", columns="indicator", values="value").resample("M").last()
    wb_resampled = wb_df.set_index("date").resample("M").ffill()

    # 3. Merge all into one DataFrame
    df_combined = pd.concat([yahoo_pivot, fred_pivot, wb_resampled], axis=1)

    # 4. Drop rows with many missing values
    df_combined = df_combined.dropna(thresh=int(df_combined.shape[1] * 0.6))

    return df_combined

def compute_correlations(df):
    pearson_corr = df.corr(method="pearson")
    spearman_corr = df.corr(method="spearman")
    return pearson_corr, spearman_corr

if __name__ == "__main__":
    df = load_and_prepare_data()
    pearson_corr, spearman_corr = compute_correlations(df)

    # Save for inspection
    pearson_corr.to_csv("data/processed/pearson_correlation_matrix.csv")
    spearman_corr.to_csv("data/processed/spearman_correlation_matrix.csv")
    print("✅ Correlation matrices saved.")
