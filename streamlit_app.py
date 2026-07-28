# ==========================================
# AI Investment Intelligence Platform
# File: streamlit_app.py
# Version: 3.4 (Production Enhanced Edition)
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
# Custom UI Styling (Fixed Dark Mode Readability & Layout)
# ----------------------------------

st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    /* Metric Card Styling with Bloomberg Terminal Aesthetics */
    .stMetric {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 18px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    /* Force all metric labels and values to be bright, high-contrast, and fully readable */
    [data-testid="stMetricLabel"] {
        color: #8b949e !important;
        font-weight: 600;
        font-size: 0.9rem !important;
    }
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: 700;
        font-size: 1.4rem !important;
    }
    [data-testid="stMetricDelta"] {
        color: #58a6ff !important;
    }
    /* General text adjustments for seamless dark theme readability */
    p, span, div, label {
        color: #c9d1d9;
    }
    .stDataFrame {
        border-radius: 8px;
        border: 1px solid #30363d;
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
    using live financial statements, rigorous valuation models, risk intelligence, and balance sheet diagnostics.
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
                
                # Pass optional metrics via kwargs to match recommendation engine v3.0 specs
                recommendation = generate_recommendation(
                    f_score,
                    v_score,
                    margin_of_safety,
                    debt_score=financial_health.get("Debt Score", 10.0),
                    cash_flow_score=financial_health.get("Cash Flow Score", 10.0),
                    profitability_score=financial_health.get("Profitability Score", 15.0),
                    liquidity_score=financial_health.get("Liquidity Score", 10.0)
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
                f"{fh_score_val}/100" if fh_score_val != 'N/A' else "Not Available"
            )

        with col2:
            st.metric(
                "Profitability",
                f"{prof_score_val_str}/35" if prof_score_val_str != 'N/A' else "Not Available"
            )

        with col3:
            st.metric(
                "Liquidity",
                f"{liq_score_val_str}/15" if liq_score_val_str != 'N/A' else "Not Available"
            )

        st.markdown("### Financial Score Breakdown")

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
            font_color="white",
            title_font=dict(size=18, color="#ffffff"),
            margin=dict(l=20, r=20, t=50, b=20)
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.divider()

        # ----------------------------------
        # Valuation & Balance Sheet Metrics Section
        # ----------------------------------
        st.subheader("💰 Valuation & Balance Sheet Metrics")

        # Safely extract requested additional metrics
        fcf_val = valuation.get('Free Cash Flow') if valuation else None
        cash_val = valuation.get('Total Cash') if valuation else None
        debt_val = valuation.get('Total Debt') if valuation else None
        shares_val = valuation.get('Shares Outstanding') if valuation else None
        
        business_val = intrinsic.get('Business Value') if intrinsic else None
        
        # Approximate dynamic WACC based on capital structure or default standard
        current_price_val = valuation.get('Current Price') if valuation else None
        estimated_wacc = 0.095  # Standard benchmark default proxy matching valuation engine
        if shares_val and current_price_val and debt_val is not None and cash_val is not None:
            equity_cap = shares_val * current_price_val
            total_cap = equity_cap + debt_val
            if total_cap > 0:
                # Dynamic proxy calculation
                equity_weight = equity_cap / total_cap
                debt_weight = debt_val / total_cap
                estimated_wacc = (equity_weight * 0.10) + (debt_weight * 0.05 * 0.79)
                estimated_wacc = max(0.06, min(estimated_wacc, 0.15))

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Current Price",
                f"${current_price_val:,.2f}" if current_price_val is not None else "Not Available"
            )
            st.metric(
                "Free Cash Flow (FCF)",
                f"${fcf_val:,.0f}" if fcf_val is not None else "Not Available"
            )
            st.metric(
                "Enterprise Value",
                f"${business_val:,.0f}" if business_val is not None and business_val > 0 else "Not Available"
            )

        with col2:
            st.metric(
                "P/E Ratio",
                f"{valuation.get('P/E Ratio'):,.2f}" if valuation and valuation.get("P/E Ratio") is not None else "Not Available"
            )
            st.metric(
                "Total Cash",
                f"${cash_val:,.0f}" if cash_val is not None else "Not Available"
            )
            st.metric(
                "Estimated WACC",
                f"{estimated_wacc * 100:.2f}%" if estimated_wacc is not None else "Not Available"
            )

        with col3:
            st.metric(
                "P/B Ratio",
                f"{valuation.get('P/B Ratio'):,.2f}" if valuation and valuation.get("P/B Ratio") is not None else "Not Available"
            )
            st.metric(
                "Total Debt",
                f"${debt_val:,.0f}" if debt_val is not None else "Not Available"
            )
            st.metric(
                "Shares Outstanding",
                f"{shares_val:,.0f}" if shares_val is not None else "Not Available"
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
