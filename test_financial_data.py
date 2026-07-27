from financial_data import get_company_financials


data = get_company_financials("AAPL")


print("Income Statement")
print(data["income_statement"])


print("\nBalance Sheet")
print(data["balance_sheet"])


print("\nCash Flow")
print(data["cash_flow"])