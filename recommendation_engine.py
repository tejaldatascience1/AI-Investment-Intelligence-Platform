# ==========================================
# AI Investment Intelligence Platform
# File: recommendation_engine.py
# Version: 3.0 (Production Weighted Scoring Engine)
# ==========================================

import logging

# Configure logging for monitoring recommendation calculations
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
    Generates professional investment recommendations (STRONG BUY, BUY, HOLD, SPECULATIVE BUY, SELL)
    using a multi-pillar weighted scoring matrix incorporating financial health, valuation, 
    margin of safety, debt profile, free cash flow, profitability, and liquidity.
    """
    try:
        # 1. Normalize and Extract Base Inputs Safely
        f_score = float(financial_health_score) if financial_health_score is not None and financial_health_score != "Not Available" else 0.0
        v_score = float(valuation_score) if valuation_score is not None and valuation_score != "Not Available" else 0.0
        mos = float(margin_of_safety) if margin_of_safety is not None else -99.0

        # 2. Extract Extended Pillars via kwargs with sensible fallbacks
        d_score = float(kwargs.get("debt_score", 10.0) or 10.0)
        cf_score = float(kwargs.get("cash_flow_score", 10.0) or 10.0)
        p_score = float(kwargs.get("profitability_score", 15.0) or 15.0)
        l_score = float(kwargs.get("liquidity_score", 10.0) or 10.0)

        # 3. Compute Composite Weighted Intelligence Score (0 to 100 Scale)
        # Weights: Financial Health (25%), Valuation (20%), Margin of Safety (20%), 
        # Profitability (15%), Cash Flow (10%), Debt (5%), Liquidity (5%)
        
        # Normalize individual sub-scores or percentages to relative 100-point scales
        norm_f_score = min(max(f_score, 0.0), 100.0)                    # Already out of 100
        norm_v_score = min(max((v_score / 30.0) * 100.0, 0.0), 100.0)   # Max valuation score is 30
        
        # Normalize Margin of Safety (-50% to +50% mapped to 0 to 100)
        norm_mos = min(max(((mos + 50.0) / 100.0) * 100.0, 0.0), 100.0)
        
        norm_p_score = min(max((p_score / 35.0) * 100.0, 0.0), 100.0)   # Max profitability score proxy (~35)
        norm_cf_score = min(max((cf_score / 20.0) * 100.0, 0.0), 100.0) # Max cash flow score proxy (~20)
        norm_d_score = min(max((d_score / 20.0) * 100.0, 0.0), 100.0)   # Max debt score proxy (~20)
        norm_l_score = min(max((l_score / 15.0) * 100.0, 0.0), 100.0)   # Max liquidity score proxy (~15)

        composite_score = (
            (norm_f_score * 0.25) +
            (norm_v_score * 0.20) +
            (norm_mos * 0.20) +
            (norm_p_score * 0.15) +
            (norm_cf_score * 0.10) +
            (norm_d_score * 0.05) +
            (norm_l_score * 0.05)
        )

        # 4. Generate Detailed Analytical Rationale Builders
        strengths = []
        weaknesses = []

        if f_score >= 70.0:
            strengths.append("strong overall balance sheet health")
        elif f_score < 50.0:
            weaknesses.append("subdued financial stability metrics")

        if mos > 15.0:
            strengths.append(f"an attractive margin of safety ({mos:.1f}%)")
        elif mos < 0.0:
            weaknesses.append(f"a negative margin of safety ({mos:.1f}%), indicating current overvaluation relative to intrinsic value")

        if p_score >= 20.0:
            strengths.append("robust corporate profitability")
        elif p_score < 10.0:
            weaknesses.append("weak operating margins or earnings performance")

        if cf_score >= 12.0:
            strengths.append("healthy free cash flow conversion")
        elif cf_score < 5.0:
            weaknesses.append("constrained cash flow generation")

        if d_score >= 12.0:
            strengths.append("conservative leverage and low debt burden")
        elif d_score < 5.0:
            weaknesses.append("elevated financial leverage risk")

        strength_str = ", ".join(strengths) if strengths else "stable core metrics"
        weakness_str = ", ".join(weaknesses) if weaknesses else "minor risk factors"

        # 5. Decision Matrix Based on Composite Score & Core Thresholds
        if composite_score >= 72.0 and mos > 5.0 and d_score >= 8.0:
            return {
                "Recommendation": "🟢 STRONG BUY",
                "Reason": f"High composite investment score ({composite_score:.1f}/100). Backed by {strength_str}, offering an optimal blend of business quality and valuation discount."
            }

        elif composite_score >= 60.0 and mos > -10.0:
            return {
                "Recommendation": "🟢 BUY",
                "Reason": f"Solid fundamental profile (Composite Score: {composite_score:.1f}/100). Supported by {strength_str}, though tempered by slight headwinds from {weakness_str}."
            }

        elif mos > 30.0 and f_score >= 45.0:
            return {
                "Recommendation": "🟡 SPECULATIVE BUY",
                "Reason": f"Deep value opportunity driven by a substantial margin of safety ({mos:.1f}%). However, caution is warranted due to {weakness_str}."
            }

        elif composite_score >= 48.0 and mos > -25.0:
            return {
                "Recommendation": "🟡 HOLD",
                "Reason": f"Balanced risk-reward profile (Composite Score: {composite_score:.1f}/100). The enterprise exhibits {strength_str}, but current pricing does not provide an immediate margin catalyst."
            }

        elif f_score >= 70.0 and mos <= -20.0:
            return {
                "Recommendation": "🟡 HOLD (OVERVALUED)",
                "Reason": f"Stellar underlying business quality and financial health, but the security is currently trading at a premium with {weakness_str}. Better entry points recommended."
            }

        else:
            return {
                "Recommendation": "🔴 SELL",
                "Reason": f"Elevated fundamental vulnerability (Composite Score: {composite_score:.1f}/100). Pressured by {weakness_str}, presenting significant downside exposure."
            }

    except Exception as e:
        logger.error(f"Error generating recommendation: {e}")
        return {
            "Recommendation": "🟡 HOLD",
            "Reason": "Evaluation defaulted to neutral due to insufficient data or calculation variance."
        }
