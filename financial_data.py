import yfinance as yf


# ----------------------------------
# Fetch Company Financial Data
# ----------------------------------

def get_company_financials(ticker):

    company = yf.Ticker(ticker)


    financial_data = {

        "income_statement": company.financials,

        "balance_sheet": company.balance_sheet,

        "cash_flow": company.cashflow

    }


    return financial_data