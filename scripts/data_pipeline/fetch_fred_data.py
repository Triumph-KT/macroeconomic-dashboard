"""
Author: Triumph Kia Teh
Date: March 24, 2025
Description:
    Script to test and execute the FRED data fetching function from utils_fred.py.
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils_fred import fetch_fred_series

# Fetch multiple series
fetch_fred_series("CPIAUCNS")   # Inflation
fetch_fred_series("GDP")        # GDP
fetch_fred_series("UNRATE")     # Unemployment
fetch_fred_series("USSLIND")    # Leading Index (CLI alternative)
