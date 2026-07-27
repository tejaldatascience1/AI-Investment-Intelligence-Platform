from financial_data import get_company_financials

from financial_analysis import (
    calculate_profitability,
    calculate_growth_and_debt,
    calculate_liquidity,
    calculate_cash_flow,
    calculate_financial_health_score
)


# ----------------------------------
# Select Company
# ----------------------------------

ticker = "AAPL"


# ----------------------------------
# Fetch Financial Data
# ----------------------------------

financial_data = get_company_financials(
    ticker
)


print("Company:", ticker)



# ----------------------------------
# Profitability Analysis
# ----------------------------------

profitability_metrics = calculate_profitability(
    financial_data
)


print("\nProfitability Analysis")


for metric, value in profitability_metrics.items():

    print(
        metric,
        ":",
        round(value, 2),
        "%"
    )



# ----------------------------------
# Growth & Debt Analysis
# ----------------------------------

growth_debt_metrics = calculate_growth_and_debt(
    financial_data
)


print("\nGrowth & Debt Analysis")


for metric, value in growth_debt_metrics.items():

    print(
        metric,
        ":",
        round(value, 2)
    )



# ----------------------------------
# Liquidity Analysis
# ----------------------------------

liquidity_metrics = calculate_liquidity(
    financial_data
)


print("\nLiquidity Analysis")


for metric, value in liquidity_metrics.items():

    print(
        metric,
        ":",
        round(value, 2)
    )



# ----------------------------------
# Cash Flow Analysis
# ----------------------------------

cash_flow_metrics = calculate_cash_flow(
    financial_data
)


print("\nCash Flow Analysis")


for metric, value in cash_flow_metrics.items():

    print(
        metric,
        ":",
        value
    )



# ----------------------------------
# Financial Health Score
# ----------------------------------

health_score = calculate_financial_health_score(
    profitability_metrics,
    growth_debt_metrics,
    liquidity_metrics,
    cash_flow_metrics
)



print("\nFinancial Health Score")


for metric, value in health_score.items():

    print(
        metric,
        ":",
        value
    )