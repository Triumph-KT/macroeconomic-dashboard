"""
Defines and creates database tables for the macroeconomic dashboard:
- World Bank annual indicators
- FRED monthly indicators
- Yahoo Finance daily asset prices

Run this script once to initialize the database schema.
"""
from sqlalchemy import Table, Column, String, Float, Date, MetaData
from scripts.db.db_connect import engine

metadata = MetaData()

# Table 1: World Bank macro data
macro_indicators = Table(
    "macro_indicators", metadata,
    Column("date", Date, primary_key=True),
    Column("gdp_per_capita", Float),
    Column("inflation", Float),
    Column("population", Float),
    Column("gov_exp_pct_gdp", Float),
    Column("unemployment_global", Float),
)

# Table 2: FRED data (CPI, GDP, Unemployment, CLI)
fred_indicators = Table(
    "fred_indicators", metadata,
    Column("date", Date, primary_key=True),
    Column("indicator", String, primary_key=True),  # CPI, GDP, etc.
    Column("value", Float),
)

# Table 3: Yahoo Finance Asset data 
yahoo_assets = Table(
    "yahoo_assets", metadata,
    Column("date", Date, primary_key=True),
    Column("symbol", String, primary_key=True),
    Column("adj_close", Float),
)

if __name__ == "__main__":
    metadata.create_all(engine)
    print("✅ All tables created successfully.")
