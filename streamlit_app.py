# ==========================================
# AI Investment Intelligence Platform
# File: streamlit_app.py
# Version: 4.0 (Production Display & Native UI Polish Edition)
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
# Helper Formatting Function
# ----------------------------------

def format_large_number(val, prefix="$", suffix=""):
    """
    Formats large financial numbers using professional notation:
    1,250 -> 1.25K
    2,500,000 -> 2.50M
    3,450,000,000 -> 3.45B
    1,200,000,000,000 -> 1.20T
    Returns "Not Available" if value is None.
    """
    if val is None:
        return "Not Available"
    
    try:
        num = float(val)
    except (TypeError, ValueError):
        return "Not Available"
    
    abs_num = abs(num)
    sign = "-" if num < 0 else ""
    
    if abs_num >= 1_000_000_000_000:
        formatted = f"{abs_num / 1_000_000_000_000:.2f}T"
    elif abs_num >= 1_000_000_000:
        formatted = f"{abs_num / 1_000_000_000:.2f}B"
    elif abs_num >= 1_000_000:
        formatted = f"{abs_num / 1_000_000:.2f}M"
    elif abs_num >= 1_000:
        formatted = f"{abs_num / 1_000:.2f}K"
    else:
        formatted = f"{abs_num:.2f}"
        
    return f"{sign}{prefix}{formatted}{suffix}"

# ----------------------------------
# Cached Data Loaders for Speed Optimization
# ----------------------------------

@st.cache_resource(ttl=3600)
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
                        "Business Value": None,
                        "Shares Outstanding": None,
                        "Intrinsic Value": None,
                        "Margin of Safety": None
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

        fh_score_val = financial_health.get('Financial Health Score', 'N/A') if financial_health else 'N/A'
        prof_score_val_str = financial_health.get('Profitability Score', 'N/A') if financial_health else 'N/A'
        liq_score_val_str = financial_health.get('Liquidity Score', 'N/A') if financial_health else 'N/A'

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Financial Health",
                f"{fh_score_val}/100" if fh_score_val is not None and fh_score_val != 'N/A' else "Not Available"
            )

        with col2:
            st.metric(
                "Profitability",
                f"{prof_score_val_str}/35" if prof_score_val_str is not None and prof_score_val_str != 'N/A' else "Not Available"
            )

        with col3:
            st.metric(
                "Liquidity",
                f"{liq_score_val_str}/15" if liq_score_val_str is not None and liq_score_val_str != 'N/A' else "Not Available"
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
                financial_health.get("Profitability Score", 0) if financial_health else 0,
                financial_health.get("Growth Score", 0) if financial_health else 0,
                financial_health.get("Debt Score", 0) if financial_health else 0,
                financial_health.get("Liquidity Score", 0) if financial_health else 0,
                financial_health.get("Cash Flow Score", 0) if financial_health else 0
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
            margin=dict(l=20, r=20, t=50, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
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
        current_price_val = valuation.get('Current Price') if valuation else None
        eps_val = valuation.get('EPS') if valuation else None
        book_value_val = valuation.get('Book Value Per Share') if valuation else None
        pe_ratio_val = valuation.get('P/E Ratio') if valuation else None
        pb_ratio_val = valuation.get('P/B Ratio') if valuation else None
        fcf_val = valuation.get('Free Cash Flow') if valuation else None
        cash_val = valuation.get('Total Cash') if valuation else None
        debt_val = valuation.get('Total Debt') if valuation else None
        shares_val = valuation.get('Shares Outstanding') if valuation else None
        
        business_val = intrinsic.get('Business Value') if intrinsic else None
        
        # Approximate dynamic WACC based on capital structure or default standard
        estimated_wacc = 0.095  # Standard benchmark default proxy matching valuation engine
        if shares_val and current_price_val and debt_val is not None and cash_val is not None:
            equity_cap = shares_val * current_price_val
            total_cap = equity_cap + debt_val
            if total_cap > 0:
                equity_weight = equity_cap / total_cap
                debt_weight = debt_val / total_cap
                estimated_wacc = (equity_weight * 0.10) + (debt_weight * 0.05 * 0.79)
                estimated_wacc = max(0.06, min(estimated_wacc, 0.15))

        # Only show valuation results if sufficient data exists
        has_sufficient_valuation_data = (current_price_val is not None or fcf_val is not None or pe_ratio_val is not None)

        if has_sufficient_valuation_data:
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Current Price",
                    f"${current_price_val:,.2f}" if current_price_val is not None else "Not Available"
                )
                st.metric(
                    "EPS",
                    f"${eps_val:,.2f}" if eps_val is not None else "Not Available"
                )
                st.metric(
                    "Book Value",
                    f"${book_value_val:,.2f}" if book_value_val is not None else "Not Available"
                )

            with col2:
                st.metric(
                    "P/E",
                    f"{pe_ratio_val:,.2f}" if pe_ratio_val is not None else "Not Available"
                )
                st.metric(
                    "P/B",
                    f"{pb_ratio_val:,.2f}" if pb_ratio_val is not None else "Not Available"
                )
                st.metric(
                    "Free Cash Flow",
                    format_large_number(fcf_val, prefix="$")
                )

            with col3:
                st.metric(
                    "Cash",
                    format_large_number(cash_val, prefix="$")
                )
                st.metric(
                    "Total Debt",
                    format_large_number(debt_val, prefix="$")
                )
                st.metric(
                    "Shares Outstanding",
                    format_large_number(shares_val, prefix="", suffix="")
                )

            st.markdown("### Enterprise & Return Metrics")
            col_e1, col_e2, col_e3 = st.columns(3)

            with col_e1:
                st.metric(
                    "Enterprise Value",
                    format_large_number(business_val, prefix="$")
                )

            with col_e2:
                st.metric(
                    "WACC",
                    f"{estimated_wacc * 100:.2f}%" if estimated_wacc is not None else "Not Available"
                )

            overall_val_status = valuation_result.get("Overall Valuation", "Not Available") if valuation_result else "Not Available"
            st.info(f"**Valuation Standing:** {overall_val_status}")

            st.subheader("📈 Intrinsic Value & Margin of Safety")

            col_iv1, col_iv2 = st.columns(2)

            with col_iv1:
                iv_val = intrinsic.get('Intrinsic Value') if intrinsic else None
                st.metric(
                    "Intrinsic Value",
                    f"${iv_val:,.2f}" if iv_val is not None else "Not Available"
                )

            with col_iv2:
                mos_val = intrinsic.get('Margin of Safety') if intrinsic else None
                st.metric(
                    "Margin of Safety",
                    f"{mos_val:,.2f}%" if mos_val is not None else "Not Available"
                )
        else:
            st.warning("Valuation results are unavailable due to insufficient market or fundamental data.")

        st.divider()

        # ----------------------------------
        # AI Recommendation Section
        # ----------------------------------
        st.subheader("🤖 AI Investment Recommendation")

        rec_title = recommendation.get("Recommendation", "N/A") if recommendation else "N/A"
        rec_reason = recommendation.get("Reason", "No rationale provided.") if recommendation else "No rationale provided."

        col_r1, col_r2 = st.columns([1, 2])

        with col_r1:
            st.metric(
                "Recommendation",
                rec_title if rec_title is not None else "Not Available"
            )

        with col_r2:
            st.info(rec_reason if rec_reason is not None else "Not Available")

        st.divider()

# ----------------------------------
# Footer
# ----------------------------------

st.caption(
    "Built using AI + Data Science + Core Finance Concepts | Bloomberg Mini Terminal Edition"
)
