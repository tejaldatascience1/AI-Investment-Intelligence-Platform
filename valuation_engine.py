# ==========================================
# AI Investment Intelligence Platform
# File: financial_data.py
# Version: 4.3 (Robust Multi-Source Extraction Edition)
# ==========================================

import logging
import requests
import pandas as pd
import yfinance as yf

# Configure logging for monitoring data extraction and debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ----------------------------------
# Helper Extraction Functions
# ----------------------------------

def _normalize_key(key):
    """Normalizes string keys for fuzzy/flexible matching."""
    if not isinstance(key, str):
        return ""
    return "".join(c.lower() for c in key if c.isalnum())


def _extract_from_statements(statements_list, target_keywords):
    """
    Searches a list of DataFrames (annual/quarterly balance sheets or cash flows)
    using flexible keyword matching against index labels.
    """
    if not statements_list:
        return None

    for stmt in statements_list:
        if stmt is None or stmt.empty:
            continue
        
        # Iterate over columns (typically dates) and rows (metrics)
        for idx in stmt.index:
            norm_idx = _normalize_key(str(idx))
            for kw in target_keywords:
                if kw in norm_idx:
                    # Get the most recent column (first column)
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
# Fetch Company Financial Data
# ----------------------------------

def get_company_financials(ticker):
    """
    Dynamically fetches live financial statements (Income Statement, 
    Balance Sheet, Cash Flow Statement) and attributes using yfinance 
    with robust fallback hierarchies, flexible row name matching, 
    and fully pickle-serializable outputs.
    """
    try:
        # Use custom headers to avoid restrictions on cloud deployment environments (Streamlit Cloud)
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36"
        })

        company = yf.Ticker(ticker, session=session)

        # Safely fetch fast_info and convert to a standard dictionary to ensure pickle-serializability for st.cache_data
        fast_info_dict = None
        try:
            fi = company.fast_info
            if fi is not None:
                fast_info_dict = dict(fi) if hasattr(fi, "keys") else {k: fi[k] for k in dir(fi) if not k.startswith("_")}
        except Exception as e:
            logger.warning(f"Could not fetch fast_info for {ticker}: {e}")

        # info dictionary
        info = None
        try:
            info = company.info
        except Exception as e:
            logger.warning(f"Could not fetch info dictionary for {ticker}: {e}")

        income_statement = None
        try:
            inc = company.financials
            if inc is not None and not inc.empty:
                income_statement = inc.copy()
        except Exception as e:
            logger.warning(f"Could not fetch financials for {ticker}: {e}")

        quarterly_financial_statement = None
        try:
            q_inc = company.quarterly_financials
            if q_inc is not None and not q_inc.empty:
                quarterly_financial_statement = q_inc.copy()
        except Exception as e:
            logger.warning(f"Could not fetch quarterly_financials for {ticker}: {e}")

        balance_sheet = None
        try:
            bs = company.balance_sheet
            if bs is not None and not bs.empty:
                balance_sheet = bs.copy()
        except Exception as e:
            logger.warning(f"Could not fetch balance_sheet for {ticker}: {e}")

        quarterly_balance_sheet = None
        try:
            q_bs = company.quarterly_balance_sheet
            if q_bs is not None and not q_bs.empty:
                quarterly_balance_sheet = q_bs.copy()
        except Exception as e:
            logger.warning(f"Could not fetch quarterly_balance_sheet for {ticker}: {e}")

        cash_flow = None
        try:
            cf = company.cashflow
            if cf is not None and not cf.empty:
                cash_flow = cf.copy()
        except Exception as e:
            logger.warning(f"Could not fetch cashflow for {ticker}: {e}")

        quarterly_cash_flow = None
        try:
            q_cf = company.quarterly_cashflow
            if q_cf is not None and not q_cf.empty:
                quarterly_cash_flow = q_cf.copy()
        except Exception as e:
            logger.warning(f"Could not fetch quarterly_cashflow for {ticker}: {e}")

        # ----------------------------------
        # Enhanced Multi-Source Data Extraction & Injection
        # ----------------------------------
        
        # Ensure info is a dict for key insertions if valid
        if info is None:
            info = {}

        # 1. Shares Outstanding Priority Extraction
        shares_out = None
        if fast_info_dict and "shares" in fast_info_dict:
            shares_out = fast_info_dict.get("shares")
        if not shares_out:
            for key in ["sharesOutstanding", "impliedSharesOutstanding", "floatShares"]:
                if info.get(key):
                    shares_out = info.get(key)
                    break
        if shares_out:
            info["sharesOutstanding"] = shares_out

        # 2. Total Cash Priority Extraction (fast_info -> info -> balance sheets)
        total_cash = None
        if fast_info_dict:
            for k in ["currency", "lastPrice", "marketCap"]: # bypass non-cash fields
                pass
            # check common fast_info keys if available
            if "totalCash" in fast_info_dict:
                total_cash = fast_info_dict.get("totalCash")
        
        if total_cash is None and info:
            for key in ["totalCash", "cashAndCashEquivalents", "cashFinancial"]:
                if info.get(key) is not None:
                    total_cash = info.get(key)
                    break

        if total_cash is None:
            cash_keywords = ["cashandcashequivalents", "cashcashequivalentsandshortterminvestments", "cash", "shortterminvestments"]
            total_cash = _extract_from_statements([balance_sheet, quarterly_balance_sheet], cash_keywords)

        if total_cash is not None:
            info["totalCash"] = total_cash

        # 3. Total Debt Priority Extraction (info -> balance sheets)
        total_debt = None
        if info:
            for key in ["totalDebt", "shortLongTermDebtTotal", "longTermDebt"]:
                if info.get(key) is not None:
                    total_debt = info.get(key)
                    break

        if total_debt is None:
            debt_keywords = ["totaldebt", "shortlongtermdebttotal", "longtermdebt", "currentdebt", "totalliabilities"]
            total_debt = _extract_from_statements([balance_sheet, quarterly_balance_sheet], debt_keywords)

        if total_debt is not None:
            info["totalDebt"] = total_debt

        # 4. Free Cash Flow / Operating Cash Flow & CapEx Extraction
        fcf = None
        if info and info.get("freeCashflow"):
            fcf = info.get("freeCashflow")

        if fcf is None:
            fcf_keywords = ["freecashflow"]
            fcf = _extract_from_statements([cash_flow, quarterly_cash_flow], fcf_keywords)

        if fcf is None:
            # Derive FCF = Operating Cash Flow + Capital Expenditures (Capex is typically negative)
            ocf_keywords = ["operatingcashflow", "totalcashfromoperatingactivities", "cashflowfromoperatingactivities"]
            capex_keywords = ["capitalexpenditures", "capitalexpenditure", "purchaseofpropertyplantandequipment", "capex"]
            
            ocf = _extract_from_statements([cash_flow, quarterly_cash_flow], ocf_keywords)
            capex = _extract_from_statements([cash_flow, quarterly_cash_flow], capex_keywords)
            
            if ocf is not None and capex is not None:
                fcf = ocf + capex if capex < 0 else ocf - capex

        if fcf is not None:
            info["freeCashflow"] = fcf

        logger.info(f"Successfully fetched financial statements for {ticker}")

        # Construct clean, fully pickle-serializable dictionary output preserving exact keys and standard attributes
        financial_data = {
            "fast_info": fast_info_dict,
            "info": info,
            "income_statement": income_statement,
            "quarterly_financials": quarterly_financial_statement,
            "balance_sheet": balance_sheet,
            "quarterly_balance_sheet": quarterly_balance_sheet,
            "cash_flow": cash_flow,
            "quarterly_cashflow": quarterly_cash_flow
        }

        return financial_data

    except Exception as e:
        logger.error(f"Critical error fetching company financials for {ticker}: {e}")
        return {
            "fast_info": None,
            "info": None,
            "income_statement": None,
            "quarterly_financials": None,
            "balance_sheet": None,
            "quarterly_balance_sheet": None,
            "cash_flow": None,
            "quarterly_cashflow": None,
            "Error": str(e)
        }
