import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import subprocess
import datetime
import os

# ===================================================================
# ==========  AUTO REFRESH LOGIC  ===================================
# ===================================================================
def check_auto_refresh():
    """
    Check if we should auto-refresh data from the APIs (ephemerally),
    but ONLY if we've already done at least one manual fetch in the past,
    the time threshold passed, and daily limit not exceeded.
    """
    now = datetime.datetime.now()

    if 'last_fetch_time' not in st.session_state:
        st.session_state['last_fetch_time'] = None
    if 'fetch_count_today' not in st.session_state:
        st.session_state['fetch_count_today'] = 0
    if 'current_day' not in st.session_state:
        st.session_state['current_day'] = now.day

    # Reset daily count if day changed
    if now.day != st.session_state['current_day']:
        st.session_state['fetch_count_today'] = 0
        st.session_state['current_day'] = now.day

    auto_fetch = False
    if st.session_state['last_fetch_time'] is not None:
        hours_since = (now - st.session_state['last_fetch_time']).total_seconds() / 3600
        if hours_since > 4:  # e.g. 4-hour threshold
            if st.session_state['fetch_count_today'] < 3:
                auto_fetch = True

    if auto_fetch:
        st.info("Auto-refreshing data from the APIs (ephemeral) ...")
        do_refresh_all_data()
        st.session_state['last_fetch_time'] = now
        st.session_state['fetch_count_today'] += 1

# ===================================================================
# ==========  HELPER: DO REFRESH  ===================================
# ===================================================================
def do_refresh_all_data():
    """
    Calls your fetch scripts to update local CSV files in data/raw/,
    then clears cache so we re-read them. 
    """
    # Example calls:
    # NOTE: Adjust as needed if your scripts are in a different location or use different names.
    # e.g.: 
    # subprocess.run(["python", "scripts/data_pipeline/fetch_fred_data.py"])
    # subprocess.run(["python", "scripts/data_pipeline/fetch_worldbank_data.py"])
    # subprocess.run(["python", "scripts/data_pipeline/fetch_yahoo_data.py"])
    st.cache_data.clear()

# ===================================================================
# ==========  LOAD CORRELATION CSV  =================================
# ===================================================================
@st.cache_data
def load_correlation_matrices():
    pearson = pd.read_csv("data/processed/pearson_correlation_matrix.csv", index_col=0)
    spearman = pd.read_csv("data/processed/spearman_correlation_matrix.csv", index_col=0)
    return pearson, spearman

# ===================================================================
# ==========  LOAD FRED CSV  ========================================
# ===================================================================
@st.cache_data
def load_fred_csv():
    """
    Reads the CSV files that your fetch_fred_data.py script would generate 
    in data/raw/fred (like fred_cpiaucns.csv, fred_gdp.csv, etc.).
    """
    cpi = pd.read_csv("data/raw/fred/fred_cpiaucns.csv", parse_dates=["date"])
    gdp = pd.read_csv("data/raw/fred/fred_gdp.csv", parse_dates=["date"])
    unrate = pd.read_csv("data/raw/fred/fred_unrate.csv", parse_dates=["date"])
    cli = pd.read_csv("data/raw/fred/fred_usslind.csv", parse_dates=["date"])

    return cpi, gdp, unrate, cli

# ===================================================================
# ==========  LOAD YAHOO CSV  =======================================
# ===================================================================
@st.cache_data
def load_yahoo_csv():
    """
    Merges each yahoo CSV (sp500.csv, gold.csv, etc.) into one DataFrame with columns:
        date, sp500, gold, bond10y, ...
    """
    import glob
    path = "data/raw/yahoo"
    all_files = glob.glob(os.path.join(path, "*.csv"))
    dfs = []

    for f in all_files:
        label = os.path.splitext(os.path.basename(f))[0]  # e.g. sp500, gold, etc.
        df_ = pd.read_csv(f, parse_dates=["date"])
        df_.rename(columns={"adj_close": label}, inplace=True)
        dfs.append(df_)

    merged = None
    for df_ in dfs:
        if merged is None:
            merged = df_
        else:
            merged = pd.merge(merged, df_, on="date", how="outer")

    return merged.dropna()

# ===================================================================
# ==========  LOAD WORLD BANK CSV  ==================================
# ===================================================================
@st.cache_data 
def load_worldbank_csv():
    """
    Your fetch_worldbank_data.py presumably saves 'data/raw/worldbank/worldbank_us_macro.csv'.
    """
    wb = pd.read_csv("data/raw/worldbank/worldbank_us_macro.csv", parse_dates=["date"])
    return wb

# ===================================================================
# ==========  FORECAST FUNCTION  ====================================
# ===================================================================
def forecast_linear(df, months=12):
    from sklearn.linear_model import LinearRegression
    df = df.dropna().copy()
    df['timestamp'] = df['date'].map(pd.Timestamp.toordinal)

    X = df['timestamp'].values.reshape(-1, 1)
    y = df['value'].values
    model = LinearRegression().fit(X, y)

    future_dates = pd.date_range(start=df['date'].max(), periods=months+1, freq='M')[1:]
    future_ordinals = future_dates.map(pd.Timestamp.toordinal).values.reshape(-1, 1)
    future_preds = model.predict(future_ordinals)

    forecast_df = pd.DataFrame({'date': future_dates, 'value': future_preds})
    return pd.concat([df[['date','value']], forecast_df])

# ===================================================================
# ==========  SETUP + PAGE START  ===================================
# ===================================================================
st.set_page_config(layout="wide")
st.title("Macroeconomic Indicators Dashboard (No DB, Just CSV & APIs)")

check_auto_refresh()  # Possibly auto-refresh if daily limit/time threshold is met

# ---------- LARGER INTRO TEXT -----------
st.markdown("""
<div style="font-size:25px; line-height:1.7;">
<p>
Welcome to the <strong>Macroeconomic Insights & Portfolio Response Dashboard</strong>, 
a research-backed tool designed to visualize and analyze the interplay between key economic indicators and asset performance. 
Built using real-time data from the Federal Reserve Economic Data (FRED), Yahoo Finance, and the World Bank, 
this dashboard helps retail and institutional users make sense of macroeconomic trends, asset correlations, and historical patterns.
</p>

<p>
Each section of this dashboard contributes to a deeper understanding of how macroeconomic variables such as inflation, GDP growth, 
unemployment, and global indicators affect asset classes like equities, bonds, commodities, and currencies. 
Through correlation analysis, scenario simulations, and forecasting tools, users can explore how economic signals may guide portfolio decisions.
</p>

<p>
Navigate using the sidebar to jump to specific panels. Begin by reviewing the latest economic conditions in the KPIs section, 
explore trends in indicators over time, examine how assets react to macro trends, then dive into the correlation matrix 
to uncover deeper statistical relationships.
</p>
</div>
""", unsafe_allow_html=True)

# ---------- SIDEBAR (About + Refresh) -----------
with st.sidebar.expander("About", expanded=True):
    st.markdown("""
    **Creator**: Triumph Kia Teh  
    **Affiliation**: Dartmouth College
    
    This dashboard is my personal quant research project on macroeconomic trends and asset performance.
    It is for *educational and informational* purposes only.
    """)

st.sidebar.markdown("### Data Controls")
if st.sidebar.button("Refresh All Data"):
    st.info("Manually refreshing all data from FRED, Yahoo, World Bank APIs (updates CSV).")
    do_refresh_all_data()
    st.session_state['last_fetch_time'] = datetime.datetime.now()
    st.session_state['fetch_count_today'] += 1
    st.success("All data refreshed! (Ephemeral in this session)")

# ===================================================================
# LOAD EVERYTHING FROM CSV, NOT DB
# ===================================================================
cpi, gdp, unrate, cli = load_fred_csv()
assets = load_yahoo_csv()
wb_df = load_worldbank_csv()
pearson_corr, spearman_corr = load_correlation_matrices()

# ===================================================================
# ========== SECTION: Key Performance Indicators ====================
# ===================================================================
st.header("🔢 Key Performance Indicators (FRED)")
st.markdown("""
<div style="font-size:25px; line-height:1.6;">
Latest FRED macroeconomic indicator values (CPI, GDP, Unemployment Rate, CLI). 
These values offer a snapshot of the U.S. economy's recent state across inflation, output, labor, 
and forward-looking indices.
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
col1.metric("CPI (Level)", f"{cpi['value'].iloc[-1]:,.2f}")
col2.metric("GDP", f"{gdp['value'].iloc[-1]:,.2f}")
col3.metric("Unemployment Rate", f"{unrate['value'].iloc[-1]:.2f}%")
col4.metric("Leading Index (CLI)", f"{cli['value'].iloc[-1]:,.2f}")
st.divider()

st.markdown("""
<div style="font-size:16px;">
<p>
These indicators align with recent academic literature that underscores macro signals' power in shaping 
asset returns. For instance, <em>Long et al. (2022)</em> highlight how changes in leading indicators (like the CLI) 
can predict equity returns across multiple countries, potentially reflecting market underreaction to macro data. 
Similarly, <em>Macrosynergy (2024)</em> show that broad measures of inflation, GDP, and risk aversion often drive multi-asset 
performance over medium horizons.
</p>
</div>
""", unsafe_allow_html=True)

# ===================================================================
# ========== FRED Macro Indicator Trends ============================
# ===================================================================
st.header("📈 FRED Macro Indicator Trends")
st.markdown("""
<div style="font-size:25px; line-height:1.6;">
Explore historical trends in key U.S. economic indicators and forecast their future trajectories. 
These charts help users spot turning points, inflationary pressures, growth rebounds, and labor shifts.
</div>
""", unsafe_allow_html=True)

indicator = st.selectbox("Select a FRED indicator:", ["CPI", "GDP", "Unemployment", "CLI"])

def get_chart_data(indicator):
    if indicator == "CPI":
        return cpi.copy(), "Consumer Price Index", "Index Level"
    elif indicator == "GDP":
        return gdp.copy(), "Gross Domestic Product", "Billions of Dollars"
    elif indicator == "Unemployment":
        return unrate.copy(), "Unemployment Rate", "Percent"
    else:
        return cli.copy(), "Leading Index", "Index Level"

df, label, unit = get_chart_data(indicator)

st.sidebar.header("⚙️ Filter & Forecast (FRED)")
start_date = st.sidebar.date_input("Start Date", df['date'].min().date())
end_date = st.sidebar.date_input("End Date", df['date'].max().date())
smooth = st.sidebar.checkbox("Apply smoothing (7-day rolling)", value=False)
forecast_toggle = st.sidebar.checkbox("Include FRED forecast (12 months)", value=False)

if st.sidebar.button("🔄 Refresh FRED Data"):
    st.info("Fetching updated FRED data from scripts/data_pipeline/fetch_fred_data.py ...")
    # e.g. subprocess.run(["python","scripts/data_pipeline/fetch_fred_data.py"])
    st.cache_data.clear()
    st.session_state['last_fetch_time'] = datetime.datetime.now()
    st.session_state['fetch_count_today'] += 1
    st.success("FRED data updated!")

df = df[(df['date'] >= pd.to_datetime(start_date)) & (df['date'] <= pd.to_datetime(end_date))]
if smooth:
    df['value'] = df['value'].rolling(window=7).mean()
if forecast_toggle:
    df = forecast_linear(df)

chart_fred = alt.Chart(df).mark_line().encode(
    x="date:T",
    y=alt.Y("value:Q", title=unit),
    tooltip=["date:T","value:Q"]
).properties(width=800, height=350, title=f"{label} Over Time").interactive()

st.altair_chart(chart_fred, use_container_width=True)

st.markdown(f"""
<div style="font-size:16px;">
<p>
By examining <strong>{label}</strong> over time, you can see how macro shifts unfold. 
Research by <em>Macrosynergy (2024)</em> indicates these fundamental trends often have 
<b>longer-term</b> impacts on bonds, equities, and other asset classes. Meanwhile, 
<em>Di Bonaventura & Morini (2024)</em> emphasize the importance of a factor's <em>initial level</em> 
(“Is inflation already high before it rises further?”) in determining whether 
it significantly hurts or helps risk assets. 
</p>
<p>
Try enabling the forecast toggle or adjusting your date range to see if 
these patterns align with the “state-dependent” insights from the academic research.
</p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ===================================================================
# ==========  Yahoo Finance Asset Correlation =======================
# ===================================================================
st.header("💹 Yahoo Finance Asset Correlation")
st.markdown("""
<div style="font-size:25px; line-height:1.6;">
This section evaluates how selected financial assets (e.g., equities, gold, oil) have historically correlated 
with macroeconomic indicators. The analysis aids investment decisions and policy modeling.
</div>
""", unsafe_allow_html=True)

asset_option = st.selectbox("Compare with an asset:", assets.columns.drop("date"))
df_merged = pd.merge(df, assets, on="date", how="inner")
correlation = df_merged["value"].corr(df_merged[asset_option])
st.write(f"📌 Correlation with **{asset_option.upper()}**: **{correlation:.2f}**")

overlay = df_merged.melt(
    id_vars="date",
    value_vars=["value", asset_option],
    var_name="Series",
    value_name="Level"
)
chart_asset = alt.Chart(overlay).mark_line().encode(
    x="date:T",
    y="Level:Q",
    color="Series:N",
    tooltip=["date:T","Series:N","Level:Q"]
).properties(width=800, height=300, title=f"{label} vs {asset_option.upper()}")

st.altair_chart(chart_asset, use_container_width=True)

st.markdown("""
<div style="font-size:16px;">
<p>
These comparative charts echo insights from <em>Macrosynergy (2024)</em>, who show that 
asset performance is strongly tied to macro cycles (like rising GDP or high inflation). 
Depending on whether inflation is climbing from a low or high base (see <em>Di Bonaventura & Morini, 2024</em>), 
assets like gold or Treasuries might behave differently. 
Similarly, <em>Long et al. (2022)</em> suggest that leading indicators (CLI) 
may foretell equity movements, especially if investors underreact to macro signals.
</p>
<p>
A positive correlation might indicate both lines move together (e.g., 
strong inflation and robust commodity prices), while a negative correlation 
can signal a hedging effect (e.g., high unemployment vs. equity returns).
</p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ===================================================================
# ==========  World Bank Macroeconomic Indicators ====================
# ===================================================================
st.header("🌍 World Bank Macroeconomic Indicators")
st.markdown("""
<div style="font-size:25px; line-height:1.6;">
This panel provides long-term macroeconomic statistics from the World Bank — offering global perspectives 
on development, population, and fiscal behavior.
</div>
""", unsafe_allow_html=True)

wb_metric = st.selectbox("Select a World Bank metric:", wb_df.columns.drop("date"))
latest_val = wb_df[wb_metric].dropna().iloc[-1]
st.metric(f"Latest {wb_metric.replace('_',' ').title()}", f"{latest_val:,.2f}")

chart_wb = alt.Chart(wb_df).mark_line().encode(
    x="date:T",
    y=alt.Y(wb_metric, title=wb_metric.replace("_"," ").title()),
    tooltip=["date:T", wb_metric]
).properties(width=800, height=350, title=f"{wb_metric.replace('_',' ').title()} Over Time")

st.altair_chart(chart_wb, use_container_width=True)

st.markdown("""
<div style="font-size:16px;">
<p>
Viewing <strong>global data</strong> helps place U.S. macro trends in context. 
<em>Macrosynergy (2024)</em> emphasizes that cross-border factors, like external balances or 
comparative growth rates, can move commodities, FX, and even local equities. 
Studies (e.g., <em>Long et al., 2022</em>) also show that leading indicators 
in major economies may influence global stock returns. 
</p>
<p>
Try analyzing how these World Bank metrics evolve alongside FRED data in the 
Correlation Matrix to see if domestic trends mirror global shifts.
</p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ===================================================================
# ==========  Correlation Matrix Explorer ============================
# ===================================================================
st.header("🧠 Correlation Matrix Explorer")
st.markdown("""
<div style="font-size:25px; line-height:1.6;">
This matrix provides a bird’s-eye view of how all macro indicators and asset classes interact. 
Patterns here can validate existing hypotheses or reveal new research questions.
</div>
""", unsafe_allow_html=True)

corr_type = st.radio("Correlation type:", ["Pearson","Spearman"], horizontal=True)
corr_matrix = pearson_corr if corr_type=="Pearson" else spearman_corr

selected_vars = st.multiselect("Select variables to compare:", corr_matrix.columns.tolist(),
                               default=corr_matrix.columns.tolist())
if selected_vars:
    filtered = corr_matrix.loc[selected_vars, selected_vars].reset_index().melt(id_vars="index")
    filtered.columns = ["Variable 1","Variable 2","Correlation"]
    mat_chart = alt.Chart(filtered).mark_rect().encode(
        x="Variable 1:O",
        y="Variable 2:O",
        color=alt.Color("Correlation:Q", scale=alt.Scale(scheme="redblue")),
        tooltip=["Variable 1","Variable 2","Correlation"]
    ).properties(width=600, height=600, title=f"{corr_type} Correlation Matrix")

    st.altair_chart(mat_chart, use_container_width=True)
else:
    st.info("Select at least one variable to display the matrix.")

st.markdown("""
<div style="font-size:16px;">
<p>
Correlation alone can't capture <em>how</em> or <em>why</em> macro variables drive performance, but it hints at possible relationships. 
For deeper insight, <em>Di Bonaventura & Morini (2024)</em> suggest that the <strong>initial level</strong> of a macro factor 
(e.g., high inflation before it rises further) can drastically alter correlations and returns. Meanwhile, 
<em>Long et al. (2022)</em> highlight how leading indicators might preempt changes in risk assets, 
and <em>Macrosynergy (2024)</em> show that these macro trends often play out over months. 
So be aware that rising inflation from 2% to 3% may have a different impact than rising inflation from 6% to 7%, 
even if the correlation at face value looks the same.
</p>
</div>
""", unsafe_allow_html=True)

# ===================================================================
# ==========  FINAL SUMMARY  ========================================
# ===================================================================
st.markdown("""
<div style="font-size:25px; line-height:1.7; margin-top:30px;">
<hr/>
<h3>📘 Summary: Why This Dashboard Matters</h3>
<p>
This dashboard isn’t just a data dump—it’s a research tool. Each component is designed to empower users to:
</p>
<ul>
<li><strong>Understand</strong> the direction and momentum of the U.S. economy through time-series visualizations.</li>
<li><strong>Explore</strong> how macroeconomic signals relate to financial markets using historical and statistical techniques.</li>
<li><strong>Simulate</strong> simple trend projections through forecasting.</li>
<li><strong>Connect</strong> global development indicators to domestic fiscal and investment conditions.</li>
</ul>
<p>
Together, these panels form a coherent analytical journey—from observing raw macro trends (FRED), comparing them 
with real asset behavior (Yahoo), situating them globally (World Bank), and linking them all statistically 
(correlation matrix).
</p>
<p>
<strong>Whether you’re an investor, researcher, policymaker, or student</strong>, 
this tool serves as a launchpad for insight, forecasting, and hypothesis generation. Our approach 
builds on findings from three key sources:
</p>
<ul>
<li><em>Long et al. (2022)</em> – Emphasize leading indicators’ power in cross-sectional equity returns, highlighting market underreaction.</li>
<li><em>Macrosynergy (2024)</em> – Reveal how macroeconomic trends (inflation, growth, etc.) shape multi-asset returns over medium horizons.</li>
<li><em>Di Bonaventura & Morini (2024)</em> – Demonstrate that both a factor’s direction (rising/falling) and its initial state (low/medium/high) 
can profoundly influence asset-class responses.</li>
</ul>
<hr/>
</div>
""", unsafe_allow_html=True)

# ===============================
# About & Disclaimer (Bottom)
# ===============================
st.markdown("---")
st.markdown("""
<div style="font-size:18px; line-height:1.6;">
<h2>About & Disclaimer</h2>
<p><strong>Creator:</strong> Triumph Kia Teh, Junior at Dartmouth College.<br>
This dashboard is my personal quant research project on macroeconomic trends and asset performance.</p>

<p><strong>Disclaimer:</strong> The information presented here is for <em>educational and informational purposes only</em>. 
It is not intended as financial advice or a recommendation to buy or sell any securities. 
Please conduct your own due diligence or consult a licensed professional before making any investment decisions.</p>
</div>
""", unsafe_allow_html=True)

# ===============================
# References
# ===============================
st.markdown("### References")
st.markdown("""
**Long et al. (2022).** 
*Macroeconomics Matter: Leading Economic Indicators and the Cross-Section of Global Stock Returns.*  
Journal of Financial Markets, 61, 100736. [https://doi.org/10.1016/j.finmar.2022.100736](https://doi.org/10.1016/j.finmar.2022.100736)

**Macrosynergy (2024).** 
*Macroeconomic Trends and Financial Markets: Theory and Evidence.*  
Available at: [https://macrosynergy.com/research/...](https://macrosynergy.com/research/macroeconomic-trends-and-financial-markets-theory-and-evidence/)

**Di Bonaventura & Morini (2024).**  
*How Do Macro-Financial Factors Influence Asset Classes' Performance? An Empirical Analysis.*  
Preprint (Version 1) available at [https://doi.org/10.21203/rs.3.rs-5431562/v1](https://doi.org/10.21203/rs.3.rs-5431562/v1)
""")
