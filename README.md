# 📊 Macroeconomic Insights & Portfolio Response Dashboard

An interactive, research-driven dashboard that models the impact of macroeconomic indicators on financial asset classes using academic theory, data pipelines, and predictive analytics.

---

## 👥 Contributors

Developed by:

- **Triumph Kia Teh** — Quantitative Modeling & Backend (CS + Math)  
- **Privat Bizabishaka** — Macro Research & Visual Analysis (Economics)

For collaboration or feedback, reach out via [LinkedIn](https://www.linkedin.com/in/triumph-kia-teh/) or GitHub.

---

## 📌 Project Objective

This dashboard simulates how asset classes (equities, bonds, FX, commodities) respond to changes in key macroeconomic indicators (e.g., GDP, inflation, ΔCLI) under various economic scenarios. It integrates:

- Academic research (e.g., Di Bonaventura & Morini, Long et al.)
- Real-time & historical economic data via public APIs
- Predictive models (ARIMA, linear regression)
- Visual tools (Tableau, Power BI, Streamlit)

---

## 🧠 Research Backbone

- **Di Bonaventura & Morini (2024)** – *Macro-Financial Factors and Asset Classes*
- **Macrosynergy (2024)** – *Macroeconomic Trends and Financial Markets*
- **Long et al. (2022)** – *ΔCLI and Global Stock Returns*

📄 See the [Research Digest](./research/Research_Digest.pdf) for full literature integration.

---

## 📅 Project Timeline

Executed in 6 structured phases over 12 weeks:

1. Project Setup, Research Review & Data Collection  
2. Data Cleaning, Structuring & Literature Alignment  
3. Dashboard Development & Scenario Modeling  
4. Correlation Analysis & Research Validation  
5. Deployment & UX Design  
6. Predictive Analytics & Simulation Interface  

---

## 📁 Repository Structure

```
macroeconomic-dashboard/
├── data/              # Raw and cleaned datasets
├── notebooks/         # EDA and modeling notebooks
├── dashboards/        # Streamlit, Tableau, and Power BI interfaces
├── scripts/           # ETL, modeling, visualization scripts
├── research/          # Research digest and academic references
├── deployment/        # Deployment configs and cron automation
├── requirements.txt   # Project dependencies
└── README.md
```

---

## 🚀 Features

- 📈 Macroeconomic indicator panels (CLI, inflation, interest rates)
- 🗺️ Scenario simulations (e.g., 2008, COVID-19, rate hikes)
- 📊 Cross-asset correlation heatmaps with time-lag analysis
- 🧠 Predictive models (ARIMA, ΔCLI-based regressions)
- 💻 Fully deployed dashboards (Streamlit, Tableau Public, Power BI Service)

---

## 📡 Data Sources

- [FRED API](https://fred.stlouisfed.org/)
- [OECD CLI](https://data.oecd.org/leadind/business-confidence-index-cli.htm)
- [Yahoo Finance](https://finance.yahoo.com/)
- [World Bank Indicators](https://data.worldbank.org/)

---

## 🧪 Installation & Usage

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/macroeconomic-dashboard.git
cd macroeconomic-dashboard

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # For Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the Streamlit app
cd dashboards/streamlit_app
streamlit run app.py
```

---

## 📸 Preview

> Add screenshots or a GIF preview here once dashboard visuals are live.

---

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.
