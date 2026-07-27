from report_generator import (
    generate_investment_report
)

company = "Apple Inc."

financial_health_score = 80

valuation_score = 0

recommendation = "🔴 SELL"

report = generate_investment_report(

    company,

    financial_health_score,

    valuation_score,

    recommendation

)

print(report)