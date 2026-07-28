# ==========================================
# AI Investment Intelligence Platform
# File: streamlit_app.py
# Version: 3.3 (Fixed & Cleaned)
# ==========================================

import streamlit as st
import pandas as pd
import plotly.express as px

from database import get_companies
from financial_data import get_company_financials
from financial_analysis import (
    calculate_profitability,
    calculate_growth_and_debt,
    calculate_liquidity,
    calculate_cash_flow,
    calculate_financial_health_score
)
from valuation_engine import (
    get_valuation_metrics,
    calculate_valuation_score,
    calculate_intrinsic_value
)
from recommendation_engine import (
    generate_recommendation
)

# ----------------------------------
# Page Configuration
# ----------------------------------

st.set_page_config(
    page_title="AI Investment Intelligence Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------
# Custom UI Styling
# ----------------------------------

st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 15px;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)


# ----------------------------------
# Cached Data Loaders for Speed Optimization
# ----------------------------------

@st.cache_data(ttl=3600)
def cached_get_company_financials(ticker):
    return get_company_financials(ticker)

@st.cache_data(ttl=3600)
def cached_get_valuation_metrics(ticker):
    return get_valuation_metrics(ticker)


# ----------------------------------
# Header Section
# ----------------------------------

st.title("📈 AI-Powered Investment Intelligence Platform")
st.subheader("Bloomberg Mini Terminal for Retail Investors & Analysts")
st.markdown(
    """
    An AI-driven investment research platform that helps users analyze companies
    using financial statements, valuation models, risk intelligence and document analysis.
    """
)

st.divider()


# ----------------------------------
# Company Research Section
# ----------------------------------

st.header("🏢 Company Research")

try:
    company_data = get_companies()
except Exception as e:
    company_data = pd.DataFrame(columns=["country", "sector", "company_name", "ticker"])
    st.error(f"Error loading company directory: {e}")

if not company_data.empty:
    col_c1, col_c2, col_c3 = st.columns(3)

    with col_c1:
        countries = sorted(company_data["country"].unique()) if "country" in company_data.columns else []
        selected_country = st.selectbox("🌎 Select Country", countries) if countries else None

    filtered_country = company_data[company_data["country"] == selected_country] if selected_country else company_data

    with col_c2:
        sectors = sorted(filtered_country["sector"].unique()) if "sector" in filtered_country.columns else []
        selected_sector = st.selectbox("📊 Select Sector", sectors) if sectors else None

    filtered_sector = filtered_country[filtered_country["sector"] == selected_sector] if selected_sector else filtered_country

    with col_c3:
        companies_list = filtered_sector["company_name"].tolist() if "company_name" in filtered_sector.columns else []
        selected_company = st.selectbox("🏢 Select Company", companies_list) if companies_list else None

    if selected_company and not filtered_sector.empty:
        matching_rows = filtered_sector[filtered_sector["company_name"] == selected_company]["ticker"]
        selected_ticker = matching_rows.values[0] if not matching_rows.empty else None
    else:
        selected_ticker = None

    if selected_company and selected_ticker:
        st.success(f"Selected Company : **{selected_company}** | Ticker : **{selected_ticker}**")
else:
    selected_ticker = None
    st.warning("No company records found.")

st.divider()


# ----------------------------------
# Analysis Engine Execution
# ----------------------------------

if st.button("🚀 Generate Investment Intelligence", type="primary", use_container_width=True):
    if not selected_ticker:
        st.error("Please select a valid company/ticker before generating intelligence.")
    else:
        with st.spinner("Fetching financial statements and executing valuation engine..."):
            try:
                # Use cached data fetchers to maximize loading speed
                financial_data = cached_get_company_financials(selected_ticker)

                profitability = calculate_profitability(financial_data)
                growth = calculate_growth_and_debt(financial_data)
                liquidity = calculate_liquidity(financial_data)
                cashflow = calculate_cash_flow(financial_data)

                financial_health = calculate_financial_health_score(
                    profitability,
                    growth,
                    liquidity,
                    cashflow
                )

                valuation = cached_get_valuation_metrics(selected_ticker)
                valuation_result = calculate_valuation_score(valuation)
                intrinsic = calculate_intrinsic_value(selected_ticker, valuation)

                # Safety Check for Intrinsic Value & Margin of Safety
                if intrinsic is not None:
                    margin_of_safety = intrinsic.get("Margin of Safety")
                    if margin_of_safety is None:
                        margin_of_safety = 0.0
                else:
                    intrinsic = {
                        "Business Value": 0,
                        "Shares Outstanding": 0,
                        "Intrinsic Value": 0,
                        "Margin of Safety": 0.0
                    }
                    margin_of_safety = 0.0

                f_score = financial_health.get("Financial Health Score", 0) if financial_health else 0
                v_score = valuation_result.get("Valuation Score", 0) if valuation_result else 0
                
                # Removed extra keyword arguments to match the standard function signature perfectly
                recommendation = generate_recommendation(
                    f_score,
                    v_score,
                    margin_of_safety
                )

                st.success("Analysis Completed Successfully ✅")
            except Exception as ex:
                st.error(f"An error occurred during analysis: {ex}")
                st.stop()

        st.divider()

        # ----------------------------------
        # Financial Health Section
        # ----------------------------------
        st.subheader("📊 Financial Health Overview")

        fh_score_val = financial_health.get('Financial Health Score', 'N/A')
        prof_score_val_str = financial_health.get('Profitability Score', 'N/A')
        liq_score_val_str = financial_health.get('Liquidity Score', 'N/A')

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Financial Health",
                f"{fh_score_val}/100" if fh_score_val != 'N/A' else "N/A"
            )

        with col2:
            st.metric(
                "Profitability",
                prof_score_val_str if prof_score_val_str != 'N/A' else "N/A"
            )

        with col3:
            st.metric(
                "Liquidity",
                liq_score_val_str if liq_score_val_str != 'N/A' else "N/A"
            )

        st.write("### Financial Score Breakdown")

        if financial_health:
            fh_df = pd.DataFrame(list(financial_health.items()), columns=["Metric", "Score"])
            st.dataframe(fh_df, use_container_width=True, hide_index=True)

        st.subheader("📊 Financial Score Visualization")

        chart_data = pd.DataFrame({
            "Category": [
                "Profitability",
                "Growth",
                "Debt",
                "Liquidity",
                "Cash Flow"
            ],
            "Score": [
                financial_health.get("Profitability Score", 0),
                financial_health.get("Growth Score", 0),
                financial_health.get("Debt Score", 0),
                financial_health.get("Liquidity Score", 0),
                financial_health.get("Cash Flow Score", 0)
            ]
        })

        fig = px.bar(
            chart_data,
            x="Category",
            y="Score",
            text="Score",
            title="Financial Score Breakdown Matrix",
            color="Score",
            color_continuous_scale="Viridis"
        )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="white"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.divider()

        # ----------------------------------
        # Valuation Analysis Section
        # ----------------------------------
        st.subheader("💰 Valuation Analysis")

        col1, col2 = st.columns(2)

        with col1:
            current_price = valuation.get('Current Price') if valuation else None
            st.metric(
                "Current Price",
                f"${current_price:,.2f}" if current_price is not None else "Not Available"
            )

            pe_ratio = valuation.get("P/E Ratio") if valuation else None
            st.metric(
                "P/E Ratio",
                f"{pe_ratio:,.2f}" if pe_ratio is not None else "Not Available"
            )

        with col2:
            book_value = valuation.get('Book Value Per Share') if valuation else None
            st.metric(
                "Book Value Per Share",
                f"${book_value:,.2f}" if book_value is not None else "Not Available"
            )

            pb_ratio = valuation.get("P/B Ratio") if valuation else None
            st.metric(
                "P/B Ratio",
                f"{pb_ratio:,.2f}" if pb_ratio is not None else "Not Available"
            )

        overall_val_status = valuation_result.get("Overall Valuation", "Not Available") if valuation_result else "Not Available"
        st.info(f"**Valuation Standing:** {overall_val_status}")

        st.subheader("📈 Intrinsic Value & Margin of Safety")

        col1, col2 = st.columns(2)

        with col1:
            iv_val = intrinsic.get('Intrinsic Value') if intrinsic else None
            st.metric(
                "Intrinsic Value",
                f"${iv_val:,.2f}" if iv_val is not None and iv_val > 0 else "Not Available"
            )

        with col2:
            mos_val = intrinsic.get('Margin of Safety') if intrinsic else None
            st.metric(
                "Margin of Safety",
                f"{mos_val:,.2f} %" if mos_val is not None else "Not Available"
            )

        st.divider()

        # ----------------------------------
        # AI Recommendation Section
        # ----------------------------------
        st.subheader("🤖 AI Investment Recommendation")

        rec_title = recommendation.get("Recommendation", "N/A") if recommendation else "N/A"
        rec_reason = recommendation.get("Reason", "No rationale provided.") if recommendation else "No rationale provided."

        col1, col2 = st.columns([1, 2])

        with col1:
            st.metric(
                "Recommendation",
                rec_title
            )

        with col2:
            st.info(rec_reason)

        st.divider()

# ----------------------------------
# Footer
# ----------------------------------

st.caption(
    "Built using AI + Data Science + Core Finance Concepts | Bloomberg Mini Terminal Edition"
)
