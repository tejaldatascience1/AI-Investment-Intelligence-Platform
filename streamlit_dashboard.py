# ==========================================
# AI Investment Intelligence Platform
# File: streamlit_dashboard.py
# Version: 1.0
# Status: Stable
# ==========================================

import streamlit as st

from database import get_companies

from financial_data import get_financial_data

from financial_analysis import (
    calculate_profitability,
    calculate_growth_and_debt,
    calculate_liquidity,
    calculate_cash_flow,
    calculate_financial_health_score
)

# ----------------------------------
# Page Configuration
# ----------------------------------

st.set_page_config(

    page_title="AI Investment Intelligence Platform",

    page_icon="📈",

    layout="wide"

)

# ----------------------------------
# Header
# ----------------------------------

st.title("📈 AI Investment Intelligence Platform")

st.subheader(
    "Bloomberg Mini Terminal for Retail Investors & Analysts"
)

st.write(
    """
    Analyze public companies using financial statements,
    valuation models and AI-powered investment insights.
    """
)

st.divider()

# ----------------------------------
# Company Selection
# ----------------------------------

company_data = get_companies()

countries = sorted(
    company_data["country"].unique()
)

selected_country = st.selectbox(
    "🌍 Select Country",
    countries
)

filtered_country = company_data[
    company_data["country"] == selected_country
]

sectors = sorted(
    filtered_country["sector"].unique()
)

selected_sector = st.selectbox(
    "🏢 Select Sector",
    sectors
)

filtered_sector = filtered_country[
    filtered_country["sector"] == selected_sector
]

selected_company = st.selectbox(
    "📈 Select Company",
    filtered_sector["company_name"]
)

selected_ticker = filtered_sector[
    filtered_sector["company_name"] == selected_company
]["ticker"].values[0]

st.success(
    f"Selected Company : {selected_company} ({selected_ticker})"
)

st.divider()

# ----------------------------------
# Analysis Button
# ----------------------------------

if st.button("🚀 Generate Investment Intelligence"):

    with st.spinner("Analyzing company financials..."):

        financial_data = get_financial_data(
            selected_ticker
        )

        profitability = calculate_profitability(
            financial_data
        )

        growth = calculate_growth_and_debt(
            financial_data
        )

        liquidity = calculate_liquidity(
            financial_data
        )

        cashflow = calculate_cash_flow(
            financial_data
        )

        financial_health = calculate_financial_health_score(

            profitability,

            growth,

            liquidity,

            cashflow

        )

    st.success("Financial Analysis Completed")

    st.subheader("📊 Financial Health")

    st.metric(

        "Financial Health Score",

        f"{financial_health['Financial Health Score']} /100"

    )

    st.write("### Score Breakdown")

    st.write(
        financial_health
    )

st.divider()

st.caption(
    "Built using AI + Data Science + Core Finance"
)