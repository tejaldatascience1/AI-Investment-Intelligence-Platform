# ==========================================
# AI Investment Intelligence Platform
# File: financial_data.py
# Version: 4.0 (Production Robust Edition)
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
    Balance Sheet, Cash Flow Statement) and fast info attributes using yfinance 
    with robust error handling, session headers, and clean dictionary outputs.
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

        # Safely fetch fast_info and info attributes to guarantee fresh live market metrics
        fast_info = None
        info = None
        income_statement = None
        balance_sheet = None
        cash_flow = None

        try:
            fast_info = company.fast_info
        except Exception as e:
            logger.warning(f"Could not fetch fast_info for {ticker}: {e}")

        try:
            info = company.info
        except Exception as e:
            logger.warning(f"Could not fetch info dictionary for {ticker}: {e}")

        try:
            inc = company.financials
            if inc is not None and not inc.empty:
                income_statement = inc
        except Exception as e:
            logger.warning(f"Could not fetch financials for {ticker}: {e}")

        try:
            bs = company.balance_sheet
            if bs is not None and not bs.empty:
                balance_sheet = bs
        except Exception as e:
            logger.warning(f"Could not fetch balance_sheet for {ticker}: {e}")

        try:
            cf = company.cashflow
            if cf is not None and not cf.empty:
                cash_flow = cf
        except Exception as e:
            logger.warning(f"Could not fetch cashflow for {ticker}: {e}")

        # Construct clean dictionary output adhering to production and format constraints
        financial_data = {
            "fast_info": fast_info,
            "info": info,
            "income_statement": income_statement,
            "balance_sheet": balance_sheet,
            "cash_flow": cash_flow
        }

        return financial_data

    except Exception as e:
        logger.error(f"Critical error fetching company financials for {ticker}: {e}")
        return {
            "fast_info": None,
            "info": None,
            "income_statement": None,
            "balance_sheet": None,
            "cash_flow": None,
            "Error": str(e)
        }
