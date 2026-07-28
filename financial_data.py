# ==========================================
# AI Investment Intelligence Platform
# File: financial_data.py
# Version: 4.2 (Fully Compliant & Pickle-Serializable Edition)
# ==========================================

import logging
import requests
import pandas as pd
import yfinance as yf

# Configure logging for monitoring data extraction and debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ----------------------------------
# Fetch Company Financial Data
# ----------------------------------

def get_company_financials(ticker):
    """
    Dynamically fetches live financial statements (Income Statement, 
    Balance Sheet, Cash Flow Statement) and attributes using yfinance 
    with robust error handling, session headers, and fully pickle-serializable outputs.
    Returns None for unavailable items instead of fake fallback values.
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
                # Safely extract attributes from fast_info
                fast_info_dict = dict(fi) if hasattr(fi, "keys") else {k: fi[k] for k in dir(fi) if not k.startswith("_")}
        except Exception as e:
            logger.warning(f"Could not fetch fast_info for {ticker}: {e}")

        # info is already a standard Python dictionary
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
