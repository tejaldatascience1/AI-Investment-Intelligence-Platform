from valuation_engine import (
    get_valuation_metrics,
    calculate_valuation_score,
    calculate_basic_dcf,
    calculate_intrinsic_value,
    calculate_enterprise_value,
    calculate_professional_intrinsic_value
)

from utils import (
    format_currency,
    format_number
)

ticker = "AAPL"

valuation = get_valuation_metrics(ticker)

score = calculate_valuation_score(valuation)

basic_dcf = calculate_basic_dcf(valuation)

basic_intrinsic = calculate_intrinsic_value(
    ticker,
    valuation
)

enterprise_value = calculate_enterprise_value(
    valuation
)

professional_intrinsic = calculate_professional_intrinsic_value(
    ticker,
    valuation
)

print("Company:", ticker)

print("\nValuation Metrics\n")

print(
    "Current Share Price :",
    format_currency(valuation["Current Price"])
)

print(
    "EPS :",
    format_currency(valuation["EPS"])
)

print(
    "Book Value Per Share :",
    format_currency(
        valuation["Book Value Per Share"]
    )
)

print(
    "P/E Ratio :",
    format_number(
        valuation["P/E Ratio"]
    )
)

print(
    "P/B Ratio :",
    format_number(
        valuation["P/B Ratio"]
    )
)

print("\nValuation Analysis\n")

print("P/E Status :", score["P/E Status"])

print("P/B Status :", score["P/B Status"])

print(
    "Valuation Score :",
    score["Valuation Score"],
    "/40"
)

print(
    "Overall :",
    score["Overall Valuation"]
)

print("\nBasic DCF Analysis\n")

print(
    "Estimated Business Value :",
    format_currency(basic_dcf)
)

print("\nBasic Intrinsic Value\n")

print(
    "Intrinsic Value Per Share :",
    format_currency(
        basic_intrinsic["Intrinsic Value"]
    )
)

print(
    "Margin of Safety :",
    format_number(
        basic_intrinsic["Margin of Safety"]
    ),
    "%"
)

print("\nProfessional DCF Analysis\n")

print(
    "Enterprise Value :",
    format_currency(
        enterprise_value
    )
)

print(
    "Professional Intrinsic Value :",
    format_currency(
        professional_intrinsic["Intrinsic Value"]
    )
)