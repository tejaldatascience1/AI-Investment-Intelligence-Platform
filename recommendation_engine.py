# ==========================================
# AI Investment Intelligence Platform
# File: recommendation_engine.py
# Version: 1.0
# Status: Stable
# ==========================================


# ----------------------------------
# Investment Recommendation Engine
# ----------------------------------

def generate_recommendation(

    financial_health_score,

    valuation_score,

    margin_of_safety

):

    # Strong Company

    if (

        financial_health_score >= 80

        and

        valuation_score >= 20

        and

        margin_of_safety > 0

    ):

        return {

            "Recommendation": "🟢 BUY",

            "Reason":
            "Strong financials with attractive valuation."

        }


    # Average Company

    elif (

        financial_health_score >= 60

        and

        valuation_score >= 10

    ):

        return {

            "Recommendation": "🟡 HOLD",

            "Reason":
            "Business is stable but valuation is not very attractive."

        }


    # Weak / Expensive

    else:

        return {

            "Recommendation": "🔴 SELL",

            "Reason":
            "Stock appears expensive or financial quality is weak."

        }