# ==========================================
# AI Investment Intelligence Platform
# File: valuation_engine.py
# Version: 1.6
# Status: Stable (Production Fallback)
# ==========================================

import yfinance as yf


# ----------------------------------
# Get Valuation Metrics
# ----------------------------------

def get_valuation_metrics(ticker):

    try:

        stock = yf.Ticker(ticker)

        # Fetch company information
        info = stock.get_info()


        # Price fallback using historical data
        current_price = info.get("currentPrice")

        if current_price is None:

            hist = stock.history(
                period="5d"
            )

            if not hist.empty:
                current_price = float(
                    hist["Close"].iloc[-1]
                )



        valuation = {

            "Current Price": current_price,

            "EPS": info.get(
                "trailingEps",
                0
            ),

            "Book Value Per Share": info.get(
                "bookValue",
                0
            ),

            "P/E Ratio": info.get(
                "trailingPE",
                0
            ),

            "P/B Ratio": info.get(
                "priceToBook",
                0
            ),

            "Free Cash Flow": info.get(
                "freeCashflow",
                0
            ),

            "Shares Outstanding": info.get(
                "sharesOutstanding",
                0
            )

        }


        return valuation



    except Exception as e:


        return {

            "Current Price": 0,

            "EPS": 0,

            "Book Value Per Share": 0,

            "P/E Ratio": 0,

            "P/B Ratio": 0,

            "Free Cash Flow": 0,

            "Shares Outstanding": 0,

            "Error": str(e)

        }




# ----------------------------------
# Valuation Score
# ----------------------------------

def calculate_valuation_score(valuation):

    pe = valuation.get(
        "P/E Ratio"
    )

    pb = valuation.get(
        "P/B Ratio"
    )


    score = 0

    result = {}



    # P/E Analysis

    if pe and pe > 0:

        if pe < 15:

            score += 20

            result["P/E Status"] = (
                "🟢 Undervalued"
            )


        elif pe <= 30:

            score += 10

            result["P/E Status"] = (
                "🟡 Fairly Valued"
            )


        else:

            result["P/E Status"] = (
                "🔴 Overvalued"
            )



    # P/B Analysis

    if pb and pb > 0:

        if pb < 1.5:

            score += 20

            result["P/B Status"] = (
                "🟢 Undervalued"
            )


        elif pb <= 5:

            score += 10

            result["P/B Status"] = (
                "🟡 Fairly Valued"
            )


        else:

            result["P/B Status"] = (
                "🔴 Overvalued"
            )



    # Overall Rating

    if score >= 35:

        overall = (
            "🟢 Attractive Valuation"
        )


    elif score >= 20:

        overall = (
            "🟡 Fair Valuation"
        )


    else:

        overall = (
            "🔴 Expensive Stock"
        )



    result["Valuation Score"] = score

    result["Overall Valuation"] = overall


    return result




# ----------------------------------
# Basic DCF Calculator
# ----------------------------------

def calculate_basic_dcf(valuation):


    free_cash_flow = valuation.get(
        "Free Cash Flow"
    )


    if not free_cash_flow or free_cash_flow <= 0:

        return None



    growth_rate = 0.08

    discount_rate = 0.10


    present_value = 0

    cash_flow = free_cash_flow



    for year in range(1,6):

        cash_flow = cash_flow * (
            1 + growth_rate
        )


        discounted_cash_flow = (
            cash_flow /
            ((1 + discount_rate) ** year)
        )


        present_value += discounted_cash_flow



    return present_value




# ----------------------------------
# Intrinsic Value Per Share
# ----------------------------------

def calculate_intrinsic_value(
    ticker,
    valuation
):


    shares = valuation.get(
        "Shares Outstanding"
    )


    business_value = calculate_basic_dcf(
        valuation
    )



    if (
        business_value is None
        or not shares
        or shares <= 0
    ):

        return {

            "Intrinsic Value": 0,

            "Margin of Safety": 0

        }



    intrinsic_value = (
        business_value /
        shares
    )


    current_price = valuation.get(
        "Current Price"
    )


    if current_price:

        margin = (

            (
                intrinsic_value -
                current_price
            )
            /
            intrinsic_value

        ) * 100


    else:

        margin = 0



    return {


        "Business Value": business_value,

        "Shares Outstanding": shares,

        "Intrinsic Value": intrinsic_value,

        "Margin of Safety": margin

    }




# ----------------------------------
# Terminal Value Calculator
# ----------------------------------

def calculate_terminal_value(
    final_cash_flow
):


    terminal_growth_rate = 0.03

    discount_rate = 0.10



    terminal_value = (

        final_cash_flow *
        (1 + terminal_growth_rate)

    ) / (

        discount_rate -
        terminal_growth_rate

    )


    return terminal_value




# ----------------------------------
# Enterprise Value Calculator
# ----------------------------------

def calculate_enterprise_value(
    valuation
):


    free_cash_flow = valuation.get(
        "Free Cash Flow"
    )


    if not free_cash_flow:

        return None



    growth_rate = 0.08

    discount_rate = 0.10


    present_value = 0

    cash_flow = free_cash_flow



    for year in range(1,6):

        cash_flow = cash_flow * (
            1 + growth_rate
        )


        present_value += (

            cash_flow /
            ((1 + discount_rate) ** year)

        )



    terminal_value = calculate_terminal_value(
        cash_flow
    )


    discounted_terminal_value = (

        terminal_value /
        ((1 + discount_rate) ** 5)

    )


    return (

        present_value +
        discounted_terminal_value

    )




# ----------------------------------
# Professional Intrinsic Value
# ----------------------------------

def calculate_professional_intrinsic_value(
    ticker,
    valuation
):


    shares = valuation.get(
        "Shares Outstanding"
    )


    if not shares:

        return None



    enterprise_value = calculate_enterprise_value(
        valuation
    )


    if enterprise_value is None:

        return None



    intrinsic_value = (

        enterprise_value /
        shares

    )


    return {


        "Enterprise Value": enterprise_value,

        "Shares Outstanding": shares,

        "Intrinsic Value": intrinsic_value

    }
