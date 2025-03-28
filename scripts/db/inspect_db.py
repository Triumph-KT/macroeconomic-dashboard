# scripts/db/inspect_db.py

from scripts.db.db_connect import engine
import pandas as pd

tables = {
    "macro_indicators": "🌍 World Bank Macros",
    "fred_indicators": "📊 FRED Indicators",
    "yahoo_assets": "💹 Yahoo Finance Assets"
}

for table, label in tables.items():
    print(f"\n🔍 Inspecting {label} ({table})...")

    # Row count
    count_query = f"SELECT COUNT(*) FROM {table}"
    count = pd.read_sql(count_query, engine).iloc[0, 0]
    print(f"   ✅ Total rows: {count}")

    # Min and Max dates
    try:
        date_query = f"SELECT MIN(date) as min_date, MAX(date) as max_date FROM {table}"
        dates = pd.read_sql(date_query, engine)
        min_date = dates['min_date'][0]
        max_date = dates['max_date'][0]
        print(f"   📅 Date Range: {min_date} → {max_date}")
    except Exception as e:
        print(f"   ⚠️ Skipped date check (reason: {e})")
