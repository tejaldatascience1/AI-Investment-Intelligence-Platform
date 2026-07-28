# ==========================================
# AI Investment Intelligence Platform
# File: valuation_engine.py
# Version: 4.1 (Production Robust DCF Engine)
# ==========================================

import logging
import yfinance as yf
import pandas as pd

# Configure logging for Streamlit Cloud and local debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ----------------------------------
# Helper Parsing Functions
# ----------------------------------

def _normalize_key(key):
    """Normalizes string keys for flexible fuzzy matching."""
    if not isinstance(key, str):
        return ""
    return "".join(c.lower() for c in key if c.isalnum())


def _extract_from_statements(statements_list, target_keywords):
    """
    Searches a list of DataFrames (balance sheets or cash flows)
    using flexible keyword matching against index labels.
    """
    if not statements_list:
        return None

    for stmt in statements_list:
        if stmt is None or stmt.empty:
            continue
        
        for idx in stmt.index:
            norm_idx = _normalize_key(str(idx))
            for kw in target_keywords:
                if kw in norm_idx:
                    for col in stmt.columns:
                        val = stmt.loc[idx, col]
                        if pd.notna(val):
                            try:
                                float_val = float(val)
                                if float_val != 0.0:
                                    return float_val
                            except Exception:
                                continue
    return None


# ----------------------------------
# Get Valuation Metrics
# ----------------------------------

def get_valuation_metrics(ticker):
    """
    Fetches real-time valuation metrics, market data, cash flows, and balance sheet details 
    using a prioritized multi-source robust extraction flow.
    Returns clean dictionary or None for missing data without synthetic fallbacks.
    """
    try:
        company = yf.Ticker(ticker)
        
        # Safely fetch info with fallback
        info = {}
        try:
            info = company.info or {}
        except Exception as e:
            logger.warning(f"Could not fetch info dictionary for {ticker}: {e}")

        # Extract market data safely
        current_price = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose")
        pe_ratio = info.get("trailingPE") or info.get("forwardPE")
        pb_ratio = info.get("priceToBook")
        book_value = info.get("bookValue")
        eps = info.get("trailingEps")

        # Robust Shares Outstanding Extraction (fast_info -> info)
        shares_outstanding = None
        try:
            fi = company.fast_info
            if fi is not None:
                if hasattr(fi, "get") and fi.get("shares"):
                    shares_outstanding = fi.get("shares")
                elif hasattr(fi, "shares"):
                    shares_outstanding = fi.shares
        except Exception:
            pass

        if not shares_outstanding:
            for key in ["sharesOutstanding", "impliedSharesOutstanding", "floatShares"]:
                if info.get(key):
                    shares_outstanding = info.get(key)
                    break

        # Fetch Financial Statements
        try:
            cash_flow_stmt = company.cashflow
        except Exception:
            cash_flow_stmt = None

        try:
            balance_sheet = company.balance_sheet
        except Exception:
            balance_sheet = None

        try:
            quarterly_cf = company.quarterly_cashflow
        except Exception:
            quarterly_cf = None

        try:
            quarterly_bs = company.quarterly_balance_sheet
        except Exception:
            quarterly_bs = None

        # Robust Free Cash Flow Extraction
        free_cash_flow = None
        if info and info.get("freeCashflow"):
            free_cash_flow = info.get("freeCashflow")

        if free_cash_flow is None:
            fcf_keywords = ["freecashflow"]
            free_cash_flow = _extract_from_statements([cash_flow_stmt, quarterly_cf], fcf_keywords)

        if free_cash_flow is None:
            ocf_keywords = ["operatingcashflow", "totalcashfromoperatingactivities", "cashflowfromoperatingactivities"]
            capex_keywords = ["capitalexpenditures", "capitalexpenditure", "purchaseofpropertyplantandequipment", "capex"]
            
            ocf = _extract_from_statements([cash_flow_stmt, quarterly_cf], ocf_keywords)
            capex = _extract_from_statements([cash_flow_stmt, quarterly_cf], capex_keywords)
            
            if ocf is not None and capex is not None:
                free_cash_flow = ocf + capex if capex < 0 else ocf - capex

        # Robust Total Cash Extraction
        total_cash = None
        if info:
            for key in ["totalCash", "cashAndCashEquivalents", "cashFinancial"]:
                if info.get(key) is not None:
                    total_cash = info.get(key)
                    break

        if total_cash is None:
            cash_keywords = ["cashandcashequivalents", "cashcashequivalentsandshortterminvestments", "cash", "shortterminvestments"]
            total_cash = _extract_from_statements([balance_sheet, quarterly_bs], cash_keywords)

        # Robust Total Debt Extraction
        total_debt = None
        if info:
            for key in ["totalDebt", "shortLongTermDebtTotal", "longTermDebt"]:
                if info.get(key) is not None:
                    total_debt = info.get(key)
                    break

        if total_debt is None:
            debt_keywords = ["totaldebt", "shortlongtermdebttotal", "longtermdebt", "currentdebt"]
            total_debt = _extract_from_statements([balance_sheet, quarterly_bs], debt_keywords)

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
        risk_free_rate = 0.041
        beta = 1.1
        market_return = 0.09
        cost_of_equity = risk_free_rate + beta * (market_return - risk_free_rate)

        cost_of_debt = 0.05 
        tax_rate = 0.21

        cash_val = total_cash if total_cash is not None else 0.0
        debt_val = total_debt if total_debt is not None else 0.0
        total_capital = cash_val + debt_val + (shares * (current_price if current_price else 100))
        
        if total_capital > 0:
            equity_weight = (shares * (current_price if current_price else 100)) / total_capital
            debt_weight = debt_val / total_capital
            wacc = (equity_weight * cost_of_equity) + (debt_weight * cost_of_debt * (1 - tax_rate))
            wacc = max(0.06, min(wacc, 0.15)) 
        else:
            wacc = 0.095

        # 2-Stage Growth Projections
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
