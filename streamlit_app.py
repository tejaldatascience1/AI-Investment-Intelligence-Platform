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
    layout="wide"
)


# ----------------------------------
# Header
# ----------------------------------

st.title("📈 AI-Powered Investment Intelligence Platform")

st.subheader(
    "Bloomberg Mini Terminal for Retail Investors & Analysts"
)

st.write(
"""
An AI-driven investment research platform that helps users analyze companies
using financial statements, valuation models, risk intelligence and document analysis.
"""
)

st.divider()


# ----------------------------------
# Company Research
# ----------------------------------

st.header("🏢 Company Research")

company_data = get_companies()


countries = sorted(
    company_data["country"].unique()
)

selected_country = st.selectbox(
    "🌎 Select Country",
    countries
)

filtered_country = company_data[
    company_data["country"] == selected_country
]


sectors = sorted(
    filtered_country["sector"].unique()
)

selected_sector = st.selectbox(
    "📊 Select Sector",
    sectors
)

filtered_sector = filtered_country[
    filtered_country["sector"] == selected_sector
]


selected_company = st.selectbox(
    "🏢 Select Company",
    filtered_sector["company_name"]
)

selected_ticker = filtered_sector[
    filtered_sector["company_name"] == selected_company
]["ticker"].values[0]


st.success(
    f"Selected Company : {selected_company} | Ticker : {selected_ticker}"
)


# ----------------------------------
# Analysis Engine
# ----------------------------------

if st.button("🚀 Generate Investment Intelligence"):

    with st.spinner("Analyzing Company..."):

        financial_data = get_company_financials(
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

        valuation = get_valuation_metrics(
            selected_ticker
        )

        valuation_result = calculate_valuation_score(
            valuation
        )

        intrinsic = calculate_intrinsic_value(
            selected_ticker,
            valuation
        )

        recommendation = generate_recommendation(
            financial_health["Financial Health Score"],
            valuation_result["Valuation Score"],
            intrinsic["Margin of Safety"]
        )

    st.success("Analysis Completed Successfully ✅")

    st.divider()

    st.subheader("📊 Financial Health")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Financial Health",
            f"{financial_health['Financial Health Score']}/100"
        )

    with col2:
        st.metric(
            "Profitability",
            financial_health["Profitability Score"]
        )

    with col3:
        st.metric(
            "Liquidity",
            financial_health["Liquidity Score"]
        )

    st.write("### Financial Score Breakdown")

    st.dataframe(
        pd.DataFrame(
            financial_health.items(),
            columns=["Metric", "Score"]
        ),
        use_container_width=True
    )

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
            financial_health["Profitability Score"],
            financial_health["Growth Score"],
            financial_health["Debt Score"],
            financial_health["Liquidity Score"],
            financial_health["Cash Flow Score"]
        ]
    })

    fig = px.bar(
        chart_data,
        x="Category",
        y="Score",
        text="Score",
        title="Financial Score Breakdown"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.divider()

    st.subheader("💰 Valuation Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Current Price",
            f"${valuation['Current Price']}"
        )

        st.metric(
            "P/E Ratio",
            round(valuation["P/E Ratio"], 2)
        )

    with col2:
        st.metric(
            "Book Value Per Share",
            f"${round(valuation['Book Value Per Share'], 2)}"
        )

        st.metric(
            "P/B Ratio",
            round(valuation["P/B Ratio"], 2)
        )

    st.success(
        valuation_result["Overall Valuation"]
    )

    st.write("### Valuation Details")

    st.subheader("📈 Intrinsic Value")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Intrinsic Value",
            f"${round(intrinsic['Intrinsic Value'], 2)}"
        )

    with col2:
        st.metric(
            "Margin of Safety",
            f"{round(intrinsic['Margin of Safety'], 2)} %"
        )

    st.divider()

    # ----------------------------------
    # AI Recommendation
    # ----------------------------------

    st.subheader("🤖 AI Investment Recommendation")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.metric(
            "Recommendation",
            recommendation["Recommendation"]
        )

    with col2:
        st.info(
            recommendation["Reason"]
        )

    st.divider()

# ----------------------------------
# Footer
# ----------------------------------

st.caption(
    "Built using AI + Data Science + Core Finance Concepts"
)