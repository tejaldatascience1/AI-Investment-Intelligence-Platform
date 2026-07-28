# ==========================================
# AI Investment Intelligence Platform
# File: recommendation_engine.py
# Version: 2.1
# Status: Production Robust
# ==========================================


# ----------------------------------
# Investment Recommendation Engine
# ----------------------------------

def generate_recommendation(
    financial_health_score,
    valuation_score,
    margin_of_safety,
    **kwargs
):
    """
    Generates realistic investment recommendations (BUY, HOLD, or SELL)
    by combining multiple fundamental pillars, supporting optional keyword arguments safely.
    """
    
    # Normalize scores and margins safely if they are None or strings
    try:
        f_score = float(financial_health_score) if financial_health_score is not None and financial_health_score != "Not Available" else 0.0
    except Exception:
        f_score = 0.0

    try:
        v_score = float(valuation_score) if valuation_score is not None and valuation_score != "Not Available" else 0.0
    except Exception:
        v_score = 0.0

    try:
        mos = float(margin_of_safety) if margin_of_safety is not None else -999.0
    except Exception:
        mos = -999.0

    # Extract optional keyword arguments securely
        d_score = float(kwargs.get("debt_score", 10.0) or 10.0)
        cf_score = float(kwargs.get("cash_flow_score", 10.0) or 10.0)
        p_score = float(kwargs.get("profitability_score", 15.0) or 15.0)
    except Exception:
        d_score, cf_score, p_score = 10.0, 10.0, 15.0

    # 1. Strong / Conviction BUY
    if (
        f_score >= 70.0
        and v_score >= 20.0
        and mos > 10.0
        and d_score >= 10.0
        and cf_score >= 10.0
        and p_score >= 15.0
    ):
        return {
            "Recommendation": "🟢 STRONG BUY",
            "Reason": "Exceptional financial strength, robust cash flows, solid profitability, and significant margin of safety."
        }

    # 2. Standard BUY
    elif (
        f_score >= 60.0
        and v_score >= 10.0
        and mos > 0.0
        and d_score >= 5.0
    ):
        return {
            "Recommendation": "🟢 BUY",
            "Reason": "Solid fundamentals, positive margin of safety, and acceptable debt levels make this an attractive entry point."
        }

    # 3. Speculative / Margin-based BUY
    elif (
        mos > 25.0
        and p_score >= 10.0
    ):
        return {
            "Recommendation": "🟡 SPECULATIVE BUY",
            "Reason": "Business quality is mixed, but the deep discount and high margin of safety present a potential value opportunity."
        }

    # 4. HOLD / Neutral
    elif (
        f_score >= 50.0
        and v_score >= 10.0
        and mos > -15.0
    ):
        return {
            "Recommendation": "🟡 HOLD",
            "Reason": "Business operations are stable, but current valuation or safety margins do not offer a compelling reason to buy or sell."
        }

    # 5. DEFENSIVE HOLD
    elif (
        f_score >= 75.0
        and mos <= -15.0
    ):
        return {
            "Recommendation": "🟡 HOLD (OVERVALUED)",
            "Reason": "Company has stellar financial health, but the stock is currently expensive with a negative margin of safety."
        }

    # 6. SELL
    else:
        return {
            "Recommendation": "🔴 SELL",
            "Reason": "Weak financial health, poor cash flow generation, high debt profile, or negative margin of safety indicate high downside risk."
        }
