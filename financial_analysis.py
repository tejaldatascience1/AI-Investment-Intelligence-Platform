import pandas as pd


# ----------------------------------
# Helper Function
# ----------------------------------

def get_latest_value(statement, metric):

    try:
        value = statement.loc[metric].iloc[0]

        return value

    except:
        return None



# ----------------------------------
# Profitability Analysis
# ----------------------------------

def calculate_profitability(financial_data):


    income_statement = financial_data["income_statement"]

    balance_sheet = financial_data["balance_sheet"]



    # Income Statement Metrics

    revenue = get_latest_value(
        income_statement,
        "Total Revenue"
    )


    net_income = get_latest_value(
        income_statement,
        "Net Income"
    )



    # Balance Sheet Metrics

    total_assets = get_latest_value(
        balance_sheet,
        "Total Assets"
    )


    total_equity = get_latest_value(
        balance_sheet,
        "Stockholders Equity"
    )



    # Calculations

    metrics = {}



    if revenue and net_income:

        metrics["Net Profit Margin"] = (
            net_income / revenue
        ) * 100



    if total_assets and net_income:

        metrics["ROA"] = (
            net_income / total_assets
        ) * 100



    if total_equity and net_income:

        metrics["ROE"] = (
            net_income / total_equity
        ) * 100



    return metrics
# ----------------------------------
# Growth & Debt Analysis
# ----------------------------------

def calculate_growth_and_debt(financial_data):


    income_statement = financial_data["income_statement"]

    balance_sheet = financial_data["balance_sheet"]


    metrics = {}


    # -------------------------------
    # Revenue Growth
    # -------------------------------

    try:

        revenues = income_statement.loc["Total Revenue"]

        current_revenue = revenues.iloc[0]

        previous_revenue = revenues.iloc[1]


        revenue_growth = (
            (current_revenue - previous_revenue)
            /
            previous_revenue
        ) * 100


        metrics["Revenue Growth"] = revenue_growth


    except:

        metrics["Revenue Growth"] = None



    # -------------------------------
    # Debt to Equity
    # -------------------------------

    try:

        total_debt = balance_sheet.loc[
            "Total Debt"
        ].iloc[0]


        equity = balance_sheet.loc[
            "Stockholders Equity"
        ].iloc[0]


        debt_equity = (
            total_debt / equity
        )


        metrics["Debt to Equity"] = debt_equity


    except:

        metrics["Debt to Equity"] = None



    return metrics
# ----------------------------------
# Liquidity Analysis
# ----------------------------------

def calculate_liquidity(financial_data):


    balance_sheet = financial_data["balance_sheet"]


    metrics = {}


    # -------------------------------
    # Current Ratio
    # -------------------------------

    try:

        current_assets = balance_sheet.loc[
            "Current Assets"
        ].iloc[0]


        current_liabilities = balance_sheet.loc[
            "Current Liabilities"
        ].iloc[0]


        current_ratio = (
            current_assets /
            current_liabilities
        )


        metrics["Current Ratio"] = current_ratio


    except:

        metrics["Current Ratio"] = None



    # -------------------------------
    # Quick Ratio
    # -------------------------------

    try:

        inventory = balance_sheet.loc[
            "Inventory"
        ].iloc[0]


        quick_assets = (
            current_assets - inventory
        )


        quick_ratio = (
            quick_assets /
            current_liabilities
        )


        metrics["Quick Ratio"] = quick_ratio


    except:

        metrics["Quick Ratio"] = None



    return metrics
# ----------------------------------
# Cash Flow Analysis
# ----------------------------------

def calculate_cash_flow(financial_data):


    cash_flow = financial_data["cash_flow"]


    metrics = {}


    # -------------------------------
    # Operating Cash Flow
    # -------------------------------

    try:

        operating_cash_flow = cash_flow.loc[
            "Operating Cash Flow"
        ].iloc[0]


        metrics["Operating Cash Flow"] = operating_cash_flow


    except:

        metrics["Operating Cash Flow"] = None



    # -------------------------------
    # Free Cash Flow
    # -------------------------------

    try:

        capital_expenditure = cash_flow.loc[
            "Capital Expenditure"
        ].iloc[0]


        free_cash_flow = (
            operating_cash_flow - abs(capital_expenditure)
        )


        metrics["Free Cash Flow"] = free_cash_flow


    except:

        metrics["Free Cash Flow"] = None



    return metrics
# ----------------------------------
# Financial Health Score
# ----------------------------------

def calculate_financial_health_score(
    profitability_metrics,
    growth_debt_metrics,
    liquidity_metrics,
    cash_flow_metrics
):

    score = 0


    breakdown = {}



    # -------------------------------
    # Profitability Score (30)
    # -------------------------------

    profitability_score = 0


    if profitability_metrics.get("Net Profit Margin"):

        if profitability_metrics["Net Profit Margin"] > 20:
            profitability_score += 10

        elif profitability_metrics["Net Profit Margin"] > 10:
            profitability_score += 7

        else:
            profitability_score += 4



    if profitability_metrics.get("ROA"):

        if profitability_metrics["ROA"] > 10:
            profitability_score += 10

        elif profitability_metrics["ROA"] > 5:
            profitability_score += 7

        else:
            profitability_score += 4



    if profitability_metrics.get("ROE"):

        if profitability_metrics["ROE"] > 20:
            profitability_score += 10

        elif profitability_metrics["ROE"] > 10:
            profitability_score += 7

        else:
            profitability_score += 4



    breakdown["Profitability Score"] = profitability_score

    score += profitability_score



    # -------------------------------
    # Growth Score (20)
    # -------------------------------

    growth_score = 0


    revenue_growth = growth_debt_metrics.get(
        "Revenue Growth"
    )


    if revenue_growth:

        if revenue_growth > 10:
            growth_score = 20

        elif revenue_growth > 5:
            growth_score = 15

        else:
            growth_score = 8



    breakdown["Growth Score"] = growth_score

    score += growth_score



    # -------------------------------
    # Debt Score (20)
    # -------------------------------

    debt_score = 0


    debt_equity = growth_debt_metrics.get(
        "Debt to Equity"
    )


    if debt_equity:

        if debt_equity < 0.5:
            debt_score = 20

        elif debt_equity < 1.5:
            debt_score = 15

        else:
            debt_score = 8



    breakdown["Debt Score"] = debt_score

    score += debt_score



    # -------------------------------
    # Liquidity Score (15)
    # -------------------------------

    liquidity_score = 0


    current_ratio = liquidity_metrics.get(
        "Current Ratio"
    )


    if current_ratio:

        if current_ratio > 1.5:
            liquidity_score = 15

        elif current_ratio > 1:
            liquidity_score = 10

        else:
            liquidity_score = 5



    breakdown["Liquidity Score"] = liquidity_score

    score += liquidity_score



    # -------------------------------
    # Cash Flow Score (15)
    # -------------------------------

    cash_flow_score = 0


    free_cash_flow = cash_flow_metrics.get(
        "Free Cash Flow"
    )


    if free_cash_flow and free_cash_flow > 0:

        cash_flow_score = 15



    breakdown["Cash Flow Score"] = cash_flow_score

    score += cash_flow_score



    breakdown["Financial Health Score"] = score



    return breakdown