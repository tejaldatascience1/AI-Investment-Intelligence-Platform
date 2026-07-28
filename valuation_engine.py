# ==========================================
# AI Investment Intelligence Platform
# File: valuation_engine.py
# Version: 3.0 (Production DCF Engine)
# ==========================================

import logging
import yfinance as yf
import pandas as pd

# Configure logging for Streamlit Cloud and local debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ----------------------------------
# Get Valuation Metrics
# ----------------------------------

def get_valuation_metrics(ticker):
    """
    Fetches real-time valuation metrics, market data, cash flows, and balance sheet details using yfinance.
    Returns clean dictionary or None for missing data without synthetic fallbacks.
    """
    try:
        company = yf.Ticker(ticker)
        info = company.info

        # Extract market data safely
        current_price = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose")
        pe_ratio = info.get("trailingPE") or info.get("forwardPE")
        pb_ratio = info.get("priceToBook")
        book_value = info.get("bookValue")
        eps = info.get("trailingEps")
        shares_outstanding = info.get("sharesOutstanding")

        # Fetch Financial Statements for FCF, Cash, and Debt
        cash_flow_stmt = company.cashflow
        balance_sheet = company.balance_sheet

        free_cash_flow = None
        total_cash = None
        total_debt = None

        if cash_flow_stmt is not None and not cash_flow_stmt.empty:
            # Try to fetch latest Free Cash Flow or calculate Operating CF - CapEx
            for col in cash_flow_stmt.columns:
                try:
                    ocf = cash_flow_stmt.loc["Operating Cash Flow", col] if "Operating Cash Flow" in cash_flow_stmt.index else None
                    capex = cash_flow_stmt.loc["Capital Expenditure", col] if "Capital Expenditure" in cash_flow_stmt.index else None
                    if ocf is not None and capex is not None:
                        free_cash_flow = float(ocf) + float(capex) # Capex is typically negative
                        break
                    elif "Free Cash Flow" in cash_flow_stmt.index:
                        free_cash_flow = float(cash_flow_stmt.loc["Free Cash Flow", col])
                        break
                except Exception:
                    continue

        if balance_sheet is not None and not balance_sheet.empty:
            for col in balance_sheet.columns:
                try:
                    if "Cash And Cash Equivalents" in balance_sheet.index:
                        total_cash = float(balance_sheet.loc["Cash And Cash Equivalents", col])
                    elif "Cash Cash Equivalents And Short Term Investments" in balance_sheet.index:
                        total_cash = float(balance_sheet.loc["Cash Cash Equivalents And Short Term Investments", col])

                    if "Total Debt" in balance_sheet.index:
                        total_debt = float(balance_sheet.loc["Total Debt", col])
                    elif "Long Term Debt" in balance_sheet.index:
                        short_debt = balance_sheet.loc["Current Debt", col] if "Current Debt" in balance_sheet.index else 0.0
                        long_debt = balance_sheet.loc["Long Term Debt", col]
                        total_debt = float(long_debt) + float(short_debt if short_debt else 0.0)
                    break
                except Exception:
                    continue

        valuation_metrics = {
            "Current Price": current_price,
            "P/E Ratio": pe_ratio,
            "P/B Ratio": pb_ratio,
            "Book Value Per Share": book_value,
            "EPS": eps,
            "Free Cash Flow": free_cash_flow,
            "Shares Outstanding": shares_outstanding,
            "Total Cash": total_cash,
            "Total Debt": total_debt
        }

        return valuation_metrics

    except Exception as e:
        logger.error(f"Error fetching valuation metrics for {ticker}: {e}")
        return {
            "Current Price": None,
            "P/E Ratio": None,
            "P/B Ratio": None,
            "Book Value Per Share": None,
            "EPS": None,
            "Free Cash Flow": None,
            "Shares Outstanding": None,
            "Total Cash": None,
            "Total Debt": None,
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

        score = 15  
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

        score = max(0, min(score, 30))

        return {
            "Valuation Score": score,
            "Overall Valuation": status
        }

    except Exception as e:
        logger.error(f"Error calculating valuation score: {e}")
        return {
            "Valuation Score": 0,
            "Overall Valuation": "Not Available"
        }


# ----------------------------------
# Helper DCF Functions (Required Signatures)
# ----------------------------------

def calculate_terminal_value(final_fcf, terminal_growth_rate=0.03, wacc=0.10):
    """Calculates terminal value using Gordon Growth Model."""
    try:
        if final_fcf is None or wacc <= terminal_growth_rate:
            return None
        return (final_fcf * (1 + terminal_growth_rate)) / (wacc - terminal_growth_rate)
    except Exception as e:
        logger.error(f"Error calculating terminal value: {e}")
        return None


def calculate_enterprise_value(pv_of_cf, terminal_value, total_cash, total_debt):
    """Calculates enterprise value and adjusts to equity value."""
    try:
        if pv_of_cf is None or terminal_value is None:
            return None
        
        ev = pv_of_cf + terminal_value
        cash = total_cash if total_cash is not None else 0.0
        debt = total_debt if total_debt is not None else 0.0
        
        equity_value = ev + cash - debt
        return equity_value
    except Exception as e:
        logger.error(f"Error calculating enterprise value: {e}")
        return None


def calculate_basic_dcf(valuation_metrics):
    """Basic DCF proxy wrapper method."""
    return calculate_professional_intrinsic_value(valuation_metrics)


def calculate_professional_intrinsic_value(valuation_metrics):
    """
    Executes a professional 2-stage Discounted Cash Flow (DCF) model 
    using real Free Cash Flow, dynamic WACC approximation, and balance sheet adjustments.
    """
    try:
        if not valuation_metrics:
            return None

        fcf = valuation_metrics.get("Free Cash Flow")
        shares = valuation_metrics.get("Shares Outstanding")
        total_cash = valuation_metrics.get("Total Cash")
        total_debt = valuation_metrics.get("Total Debt")
        current_price = valuation_metrics.get("Current Price")

        if fcf is None or fcf <= 0 or shares is None or shares <= 0:
            return None

        # Dynamic WACC Approximation via CAPM proxy & Capital Structure
        cost_of_equity = 0.10 # Baseline market expected return proxy
        risk_free_rate = 0.041
        beta = 1.1
        market_return = 0.09
        cost_of_equity = risk_free_rate + beta * (market_return - risk_free_rate)

        cost_of_debt = 0.05 # Standard corporate debt cost approximation
        tax_rate = 0.21

        cash_val = total_cash if total_cash is not None else 0.0
        debt_val = total_debt if total_debt is not None else 0.0
        total_capital = cash_val + debt_val + (shares * (current_price if current_price else 100))
        
        if total_capital > 0:
            equity_weight = (shares * (current_price if current_price else 100)) / total_capital
            debt_weight = debt_val / total_capital
            wacc = (equity_weight * cost_of_equity) + (debt_weight * cost_of_debt * (1 - tax_rate))
            wacc = max(0.06, min(wacc, 0.15)) # Bound WACC between 6% and 15% for realism
        else:
            wacc = 0.095

        # 2-Stage Growth Projections (Stage 1: 5 years high growth, Stage 2: Terminal)
        growth_rate_stage1 = 0.07
        terminal_growth_rate = 0.025
        projection_years = 5

        pv_of_cf = 0.0
        current_projected_fcf = fcf

        for year in range(1, projection_years + 1):
            current_projected_fcf *= (1 + growth_rate_stage1)
            pv_of_cf += current_projected_fcf / ((1 + wacc) ** year)

        terminal_val = calculate_terminal_value(current_projected_fcf, terminal_growth_rate, wacc)
        if terminal_val is None:
            return None

        pv_terminal_val = terminal_val / ((1 + wacc) ** projection_years)
        equity_value = calculate_enterprise_value(pv_of_cf, pv_terminal_val, total_cash, total_debt)

        if equity_value is None or equity_value <= 0:
            return None

        intrinsic_value_per_share = equity_value / shares
        return intrinsic_value_per_share

    except Exception as e:
        logger.error(f"Error in professional intrinsic value calculation: {e}")
        return None


# ----------------------------------
# Main Intrinsic Value & Margin of Safety
# ----------------------------------

def calculate_intrinsic_value(ticker, valuation_metrics):
    """
    Calculates estimated intrinsic value and margin of safety using the DCF model.
    Returns exact expected output keys required by Streamlit dashboard.
    """
    try:
        if not valuation_metrics:
            return {
                "Business Value": None,
                "Shares Outstanding": None,
                "Intrinsic Value": None,
                "Margin of Safety": None
            }

        current_price = valuation_metrics.get("Current Price")
        shares = valuation_metrics.get("Shares Outstanding")
        
        intrinsic_val = calculate_professional_intrinsic_value(valuation_metrics)

        if intrinsic_val is None or intrinsic_val <= 0:
            return {
                "Business Value": None,
                "Shares Outstanding": shares,
                "Intrinsic Value": None,
                "Margin of Safety": None
            }

        business_value = intrinsic_val * shares if shares is not None else None

        margin_of_safety = None
        if current_price is not None and intrinsic_val is not None and intrinsic_val > 0:
            margin_of_safety = ((intrinsic_val - current_price) / intrinsic_val) * 100

        return {
            "Business Value": business_value,
            "Shares Outstanding": shares,
            "Intrinsic Value": round(intrinsic_val, 2),
            "Margin of Safety": round(margin_of_safety, 2) if margin_of_safety is not None else None
        }

    except Exception as e:
        logger.error(f"Error in calculate_intrinsic_value for {ticker}: {e}")
        return {
            "Business Value": None,
            "Shares Outstanding": None,
            "Intrinsic Value": None,
            "Margin of Safety": None
        }
