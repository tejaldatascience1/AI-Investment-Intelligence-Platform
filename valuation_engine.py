# ==========================================
# AI Investment Intelligence Platform
# File: valuation_engine.py
# Version: 2.0 Stable Valuation Engine
# ==========================================

import yfinance as yf
import requests


# ----------------------------------
# Get Valuation Metrics
# ----------------------------------

def get_valuation_metrics(ticker):

    try:

        session = requests.Session()

        session.headers.update({
            "User-Agent": "Mozilla/5.0"
        })


        stock = yf.Ticker(
            ticker,
            session=session
        )

        info = stock.info


        current_price = (
            info.get("currentPrice")
            or info.get("regularMarketPrice")
        )


        if current_price is None:

            hist = stock.history(
                period="5d"
            )

            if not hist.empty:
                current_price = float(
                    hist["Close"].iloc[-1]
                )


        valuation = {

            "Current Price":
                current_price,


            "EPS":
                info.get("trailingEps"),


            "Book Value Per Share":
                info.get("bookValue"),


            "P/E Ratio":
                info.get("trailingPE"),


            "P/B Ratio":
                info.get("priceToBook"),


            "Free Cash Flow":
                info.get("freeCashflow"),


            "Operating Cash Flow":
                info.get("operatingCashflow"),


            "Capital Expenditure":
                info.get("capitalExpenditure"),


            "Total Debt":
                info.get("totalDebt"),


            "Total Cash":
                info.get("totalCash"),


            "Shares Outstanding":
                info.get("sharesOutstanding")
        }


        # Fallback FCF calculation

        if valuation["Free Cash Flow"] is None:

            ocf = valuation["Operating Cash Flow"]
            capex = valuation["Capital Expenditure"]


            if ocf and capex:

                valuation["Free Cash Flow"] = (
                    ocf - abs(capex)
                )


        return valuation


    except Exception as e:


        return {

            "Current Price": None,
            "EPS": None,
            "Book Value Per Share": None,
            "P/E Ratio": None,
            "P/B Ratio": None,
            "Free Cash Flow": None,
            "Operating Cash Flow": None,
            "Capital Expenditure": None,
            "Total Debt": None,
            "Total Cash": None,
            "Shares Outstanding": None,
            "Error": str(e)

        }



# ----------------------------------
# Valuation Score
# ----------------------------------

def calculate_valuation_score(valuation):


    pe = valuation.get("P/E Ratio")
    pb = valuation.get("P/B Ratio")


    score = 0

    result = {}



    if pe is not None:

        if pe < 20:

            score += 20
            result["P/E Status"] = "🟢 Reasonable"

        elif pe <= 35:

            score += 10
            result["P/E Status"] = "🟡 Premium Valuation"

        else:

            result["P/E Status"] = "🔴 Expensive"


    else:

        result["P/E Status"] = "⚪ N/A"



    if pb is not None:

        if pb < 3:

            score += 20
            result["P/B Status"] = "🟢 Reasonable"

        elif pb <= 8:

            score += 10
            result["P/B Status"] = "🟡 Premium"

        else:

            result["P/B Status"] = "🔴 Expensive"


    else:

        result["P/B Status"] = "⚪ N/A"



    if score >= 30:

        overall = "🟢 Attractive Valuation"


    elif score >= 15:

        overall = "🟡 Fair Valuation"


    else:

        overall = "🔴 Expensive Stock"



    result["Valuation Score"] = score

    result["Overall Valuation"] = overall


    return result



# ----------------------------------
# DCF Calculator
# ----------------------------------

def calculate_basic_dcf(valuation):


    fcf = valuation.get(
        "Free Cash Flow"
    )


    if fcf is None:

        return None



    growth_rate = 0.08

    discount_rate = 0.10

    terminal_growth = 0.03



    present_value = 0

    cash_flow = fcf



    for year in range(1,6):


        cash_flow *= (
            1 + growth_rate
        )


        present_value += (

            cash_flow /
            ((1 + discount_rate) ** year)

        )



    terminal_value = (

        cash_flow *
        (1 + terminal_growth)

    ) / (

        discount_rate -
        terminal_growth

    )



    terminal_pv = (

        terminal_value /
        ((1 + discount_rate) ** 5)

    )



    enterprise_value = (

        present_value +
        terminal_pv

    )


    return enterprise_value



# ----------------------------------
# Intrinsic Value
# ----------------------------------

def calculate_intrinsic_value(ticker, valuation):


    shares = valuation.get(
        "Shares Outstanding"
    )


    enterprise_value = calculate_basic_dcf(
        valuation
    )



    if enterprise_value is None or not shares:

        return None



    debt = valuation.get(
        "Total Debt"
    ) or 0


    cash = valuation.get(
        "Total Cash"
    ) or 0



    equity_value = (

        enterprise_value
        - debt
        + cash

    )



    intrinsic_value = (

        equity_value /
        shares

    )



    current_price = valuation.get(
        "Current Price"
    )


    margin = None


    if current_price:

        margin = (

            (intrinsic_value -
             current_price)

            /

            intrinsic_value

        ) * 100



    return {


        "Enterprise Value":
            enterprise_value,


        "Equity Value":
            equity_value,


        "Intrinsic Value":
            intrinsic_value,


        "Margin of Safety":
            margin

    }



# ----------------------------------
# Enterprise Value
# ----------------------------------

def calculate_enterprise_value(valuation):

    return calculate_basic_dcf(
        valuation
    )



# Compatibility Function
# Keeps your app.py working

def calculate_professional_intrinsic_value(
        ticker,
        valuation
):

    return calculate_intrinsic_value(
        ticker,
        valuation
    )
