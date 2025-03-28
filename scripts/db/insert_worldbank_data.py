from scripts.db.db_connect import engine
import pandas as pd
from sqlalchemy import text

# Load the cleaned CSV
df = pd.read_csv("data/processed/worldbank_us_macro.csv", parse_dates=["date"])

# Prepare the data as list of dictionaries (recommended for named binding)
data_dicts = df.to_dict(orient="records")

# SQL insert with named placeholders
insert_sql = text("""
    INSERT INTO macro_indicators (
        date, gdp_per_capita, inflation, population,
        gov_exp_pct_gdp, unemployment_global
    )
    VALUES (
        :date, :gdp_per_capita, :inflation, :population,
        :gov_exp_pct_gdp, :unemployment_global
    )
""")

# Insert all rows using a single transaction
with engine.begin() as conn:
    conn.execute(insert_sql, data_dicts)

print("✅ Inserted World Bank data into macro_indicators table.")
