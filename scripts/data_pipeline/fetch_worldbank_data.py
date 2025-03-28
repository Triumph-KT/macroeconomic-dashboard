"""
Author: Triumph Kia Teh
Date: March 24, 2025
Description:
    Fetch macroeconomic indicators from the World Bank using pandas_datareader,
    then rename columns to something friendlier.
"""

import pandas_datareader.wb as wb
import pandas as pd
import os

# Define indicators
indicators = {
    "gdp_per_capita": "NY.GDP.PCAP.CD",
    "inflation": "FP.CPI.TOTL.ZG",
    "population": "SP.POP.TOTL",
    "gov_exp_pct_gdp": "NE.CON.GOVT.ZS",
    "unemployment_global": "SL.UEM.TOTL.ZS"
}

# Download data for the US from 2010 to 2024
data = wb.download(
    indicator=list(indicators.values()),
    country='US',
    start=2010,
    end=2024
)

# Convert the multi-index to columns
df = data.reset_index()  
# Columns will look like: ['country', 'year', 'NY.GDP.PCAP.CD', 'FP.CPI.TOTL.ZG', 'SP.POP.TOTL']

# Create a date column from 'year'
df['date'] = pd.to_datetime(df['year'], format="%Y")

# Drop the old columns we don't need
df.drop(columns=['country', 'year'], inplace=True)

# Rename each indicator code to our chosen name
df.rename(columns={
    "NY.GDP.PCAP.CD": "gdp_per_capita",
    "FP.CPI.TOTL.ZG": "inflation",
    "SP.POP.TOTL": "population",
    "NE.CON.GOVT.ZS": "gov_exp_pct_gdp",
    "SL.UEM.TOTL.ZS": "unemployment_global"
}, inplace=True)

# Reorder columns nicely
df = df[["date", "gdp_per_capita", "inflation", "population", "gov_exp_pct_gdp", "unemployment_global"]]

# Save to CSV
output_path = "data/raw/worldbank_us_macro.csv"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
df.to_csv(output_path, index=False)

print(f"✅ Saved World Bank macro data to {output_path}")
