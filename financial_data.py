# ==========================================
# AI Investment Intelligence Platform
# File: financial_data.py
# Version: 3.0 (Production Clean Edition)
# ==========================================

import requests
import pandas as pd
import yfinance as yf


# ----------------------------------
# Fetch Company Financial Data
# ----------------------------------

def get_company_financials(ticker):
    """
    Dynamically fetches live financial statements (Income Statement, 
    Balance Sheet, Cash Flow Statement) using yfinance with robust 
    error handling, session headers, and clean dictionary outputs.
    """
    try:
        # Use custom headers to avoid restrictions on cloud deployment environments
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36"
        })

        company = yf.Ticker(ticker, session=session)

        # Safely fetch financial statements
        income_statement = None
        balance_sheet = None
        cash_flow = None

        try:
            inc = company.financials
            if inc is not None and not inc.empty:
                income_statement = inc
        except Exception:
            pass

        try:
            bs = company.balance_sheet
            if bs is not None and not bs.empty:
                balance_sheet = bs
        except Exception:
            pass

        try:
            cf = company.cashflow
            if cf is not None and not cf.empty:
                cash_flow = cf
        except Exception:
            pass

        # Construct clean dictionary output adhering to production constraints
        financial_data = {
            "income_statement": income_statement,
            "balance_sheet": balance_sheet,
            "cash_flow": cash_flow
        }

        return financial_data

    except Exception as e:
        # Return structured empty/None metrics if fetching completely fails
        return {
            "income_statement": None,
            "balance_sheet": None,
            "cash_flow": None,
            "Error": str(e)
        }
