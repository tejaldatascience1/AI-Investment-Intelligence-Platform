# ==========================================
# AI Investment Intelligence Platform
# File: valuation_engine.py
# Version: 2.0 (Production Stable)
# ==========================================

import yfinance as yf
import pandas as pd


# ----------------------------------
# Get Valuation Metrics
# ----------------------------------

def get_valuation_metrics(ticker):
    """
    Fetches real-time valuation metrics and market data using yfinance.
    Returns a clean dictionary with fallback options.
    """
    try:
        company = yf.Ticker(ticker)
        info = company.info

        # Extract metrics safely
        current_price = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose")
        pe_ratio = info.get("trailingPE") or info.get("forwardPE")
        pb_ratio = info.get("priceToBook")
        book_value = info.get("bookValue")
        eps = info.get("trailingEps")

        valuation_metrics = {
            "Current Price": current_price,
            "P/E Ratio": pe_ratio,
            "P/B Ratio": pb_ratio,
            "Book Value Per Share": book_value,
            "EPS": eps
        }

        return valuation_metrics

    except Exception as e:
        return {
            "Current Price": None,
            "P/E Ratio": None,
            "P/B Ratio": None,
            "Book Value Per Share": None,
            "EPS": None,
            "Error": str(e)
        }


# ----------------------------------
# Calculate Valuation Score
# ----------------------------------

def calculate_valuation_score(valuation_metrics):
    """
    Evaluates valuation metrics to assign an overall score and standing.
    """
    try:
        if not valuation_metrics:
            return {"Valuation Score": 0, "Overall Valuation": "Not Available"}

        pe = valuation_metrics.get("P/E Ratio")
        pb = valuation_metrics.get("P/B Ratio")

        score = 15  # Default baseline score
        status = "Fairly Valued"

        if pe is not None:
            if pe < 15:
                score += 10
                status = "Undervalued / Attractive"
            elif pe > 30:
                score -= 5
                status = "Expensive / Overvalued"

        if pb is not None:
            if pb < 2:
                score += 5
            elif pb > 5:
                score -= 5

        # Score boundaries normalization (0 to 30)
        score = max(0, min(score, 30))

        return {
            "Valuation Score": score,
            "Overall Valuation": status
        }

    except Exception:
        return {
            "Valuation Score": 0,
            "Overall Valuation": "Not Available"
        }


# ----------------------------------
# Calculate Intrinsic Value & Margin of Safety
# ----------------------------------

def calculate_intrinsic_value(ticker, valuation_metrics):
    """
    Calculates estimated intrinsic value and margin of safety.
    """
    try:
        if not valuation_metrics:
            return {
                "Business Value": 0,
                "Shares Outstanding": 0,
                "Intrinsic Value": 0,
                "Margin of Safety": 0.0
            }

        current_price = valuation_metrics.get("Current Price")
        eps = valuation_metrics.get("EPS")

        # Basic Graham-style or proxy intrinsic value estimation if EPS is available
        if eps is not None and eps > 0:
            # Assuming a conservative growth rate and multiplier (e.g., PE of 15)
            intrinsic_val = eps * 15
        else:
            intrinsic_val = 0.0

        margin_of_safety = 0.0
        if current_price and intrinsic_val and current_price > 0:
            margin_of_safety = ((intrinsic_val - current_price) / intrinsic_val) * 100

        return {
            "Business Value": intrinsic_val * 1000000,  # Proxy scale if needed
            "Shares Outstanding": 0,
            "Intrinsic Value": intrinsic_val,
            "Margin of Safety": round(margin_of_safety, 2)
        }

    except Exception:
        return {
            "Business Value": 0,
            "Shares Outstanding": 0,
            "Intrinsic Value": 0,
            "Margin of Safety": 0.0
        }
