# ==========================================
# AI Investment Intelligence Platform
# File: valuation_engine.py
# Version: 3.0 (Production Clean Edition)
# ==========================================

import requests
import pandas as&& yf # Wait, keep standard yfinance import clean
import yfinance as yf


# ----------------------------------
# Get Valuation Metrics without Fake Data
# ----------------------------------

def get_valuation_metrics(ticker):
    try:
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })

        stock = yf.Ticker(ticker, session=session)
        
        # Priority 1: fast_info for live pricing and shares
        current_price = None
        shares = None
        
        try:
            fast = stock.fast_info
            current_price = float(fast.last_price) if hasattr(fast, 'last_price') and fast.last_price else None
            shares = int(fast.shares) if hasattr(fast, 'shares') and fast.shares else None
        except Exception:
            pass

        # Priority 2: info dictionary
        info = {}
        try:
            info = stock.info
        except Exception:
            pass

        if not current_price:
            current_price = info.get("currentPrice") or info.get("regularMarketPrice")
            
        if not current_price:
            hist = stock.history(period="5d", session=session)
            if not hist.empty:
                current_price = float(hist["Close"].iloc[-1])

        if not shares:
            shares = info.get("sharesOutstanding")

        eps = info.get("trailingEps")
        book_value = info.get("bookValue")
        pe_ratio = info.get("trailingPE")
        pb_ratio = info.get("priceToBook")

        # Priority 3 & 4: Balance Sheet and Cashflow Statements for precise metrics
        total_debt = info.get("totalDebt")
        total_cash = info.get("totalCash")
        fcf = info.get("freeCashflow")

        try:
            balance_sheet = stock.balance_sheet
            if not balance_sheet.empty:
                if total_debt is None:
                    for debt_key in ["Total Debt", "Long Term Debt", "Total Liabilities Net Minority Interest"]:
                        if debt_key in balance_sheet.index:
                            val = balance_sheet.loc[debt_key].iloc[0]
                            if pd.notna(val):
                                total_debt = float(val)
                                break
                if total_cash is None:
                    for cash_key in ["Cash And Cash Equivalents", "Cash Cash Equivalents And Short Term Investments"]:
                        if cash_key in balance_sheet.index:
                            val = balance_sheet.loc[cash_key].iloc[0]
                            if pd.notna(val):
                                total_cash = float(val)
                                break
        except Exception:
            pass

        try:
            cf = stock.cashflow
            if fcf is None and not cf.empty:
                for fcf_key in ["Free Cash Flow", "FreeCashFlow"]:
                    if fcf_key in cf.index:
                        val = cf.loc[fcf_key].iloc[0]
                        if pd.notna(val):
                            fcf = float(val)
                            break
                if fcf is None and "Operating Cash Flow" in cf.index:
                    ocf = cf.loc["Operating Cash Flow"].iloc[0]
                    capex = 0
                    for capex_key in ["Capital Expenditure", "Capital Expenditures"]:
                        if capex_key in cf.index:
                            c_val = cf.loc[capex_key].iloc[0]
                            if pd.notna(c_val):
                                capex = float(c_val)
                                break
                    if pd.notna(ocf):
                        fcf = float(ocf) - abs(float(capex))
        except Exception:
            pass

        # Compute ratios if missing but foundational data is present
        if pe_ratio is None and current_price and eps and eps != 0:
            pe_ratio = current_price / eps

        if pb_ratio is None and current_price and book_value and book_value != 0:
            pb_ratio = current_price / book_value

        return {
            "Current Price": current_price,
            "EPS": eps,
            "Book Value Per Share": book_value,
            "P/E Ratio": pe_ratio,
            "P/B Ratio": pb_ratio,
            "Free Cash Flow": fcf,
            "Total Debt": total_debt,
            "Total Cash": total_cash,
            "Shares Outstanding": shares
        }

    except Exception as e:
        return {
            "Current Price": None,
            "EPS": None,
            "Book Value Per Share": None,
            "P/E Ratio": None,
            "P/B Ratio": None,
            "Free Cash Flow": None,
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
        if pe < 15:
            score += 20
            result["P/E Status"] = "🟢 Undervalued"
        elif pe <= 30:
            score += 10
            result["P/E Status"] = "🟡 Fairly Valued"
        else:
            result["P/E Status"] = "🔴 Overvalued"
    else:
        result["P/E Status"] = "⚪ Not Available"

    if pb is not None:
        if pb < 1.5:
            score += 20
            result["P/B Status"] = "🟢 Undervalued"
        elif pb <= 5:
            score += 10
            result["P/B Status"] = "🟡 Fairly Valued"
        else:
            result["P/B Status"] = "🔴 Overvalued"
    else:
        result["P/B Status"] = "⚪ Not Available"

    if pe is not None or pb is not None:
        if score >= 35:
            overall = "🟢 Attractive Valuation"
        elif score >= 20:
            overall = "🟡 Fair Valuation"
        else:
            overall = "🔴 Expensive Stock"
    else:
        overall = "⚪ Not Available"

    result["Valuation Score"] = score if (pe is not None or pb is not None) else "Not Available"
    result["Overall Valuation"] = overall

    return result


# ----------------------------------
# Basic DCF Calculator
# ----------------------------------

def calculate_basic_dcf(valuation):
    free_cash_flow = valuation.get("Free Cash Flow")

    if free_cash_flow is None or free_cash_flow <= 0:
        return None

    growth_rate = 0.08
    discount_rate = 0.10

    present_value = 0
    cash_flow = free_cash_flow

    for year in range(1, 6):
        cash_flow = cash_flow * (1 + growth_rate)
        discounted_cash_flow = cash_flow / ((1 + discount_rate) ** year)
        present_value += discounted_cash_flow

    return present_value


# ----------------------------------
# Terminal Value Calculator
# ----------------------------------

def calculate_terminal_value(final_cash_flow):
    if final_cash_flow is None:
        return None
        
    terminal_growth_rate = 0.03
    discount_rate = 0.10

    if discount_rate <= terminal_growth_rate:
        return None

    terminal_value = (
        final_cash_flow * (1 + terminal_growth_rate)
    ) / (
        discount_rate - terminal_growth_rate
    )

    return terminal_value


# ----------------------------------
# Enterprise Value Calculator
# ----------------------------------

def calculate_enterprise_value(valuation):
    free_cash_flow = valuation.get("Free Cash Flow")

    if free_cash_flow is None or free_cash_flow <= 0:
        return None

    growth_rate = 0.08
    discount_rate = 0.10

    present_value = 0
    cash_flow = free_cash_flow

    for year in range(1, 6):
        cash_flow = cash_flow * (1 + growth_rate)
        present_value += cash_flow / ((1 + discount_rate) ** year)

    terminal_value = calculate_terminal_value(cash_flow)
    if terminal_value is None:
        return None
        
    discounted_terminal_value = terminal_value / ((1 + discount_rate) ** 5)

    return present_value + discounted_terminal_value


# ----------------------------------
# Intrinsic Value Per Share
# ----------------------------------

def calculate_intrinsic_value(ticker, valuation):
    shares = valuation.get("Shares Outstanding")
    business_value = calculate_basic_dcf(valuation)

    if business_value is None or not shares or shares <= 0:
        return {
            "Business Value": None,
            "Shares Outstanding": shares,
            "Intrinsic Value": None,
            "Margin of Safety": None
        }

    debt = valuation.get("Total Debt") or 0
    cash = valuation.get("Total Cash") or 0

    equity_ value = business_value - debt + cash
    intrinsic_value = equity_value / shares
    current_price = valuation.get("Current Price")

    margin = None
    if current_price and intrinsic_value > 0:
        margin = ((intrinsic_value - current_price) / intrinsic_value) * 100

    return {
        "Business Value": business_value,
        "Shares Outstanding": shares,
        "Intrinsic Value": intrinsic_value,
        "Margin of Safety": margin
    }


# ----------------------------------
# Professional Intrinsic Value
# ----------------------------------

def calculate_professional_intrinsic_value(ticker, valuation):
    shares = valuation.get("Shares Outstanding")
    enterprise_value = calculate_enterprise_value(valuation)

    if enterprise_value is None or not shares or shares <= 0:
        return {
            "Enterprise Value": None,
            "Shares Outstanding": shares,
            "Intrinsic Value": None
        }

    debt = valuation.get("Total Debt") or 0
    cash = valuation.get("Total Cash") or 0

    equity_value = enterprise_value - debt + cash
    intrinsic_value = equity_value / shares

    return {
        "Enterprise Value": enterprise_value,
        "Shares Outstanding": shares,
        "Intrinsic Value": intrinsic_value
    }
