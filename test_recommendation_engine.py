from recommendation_engine import (
    generate_recommendation
)


# Sample Values

financial_health_score = 80

valuation_score = 0

margin_of_safety = -922.10


recommendation = generate_recommendation(

    financial_health_score,

    valuation_score,

    margin_of_safety

)


print("\nInvestment Recommendation\n")

print(
    "Recommendation :",
    recommendation["Recommendation"]
)

print(
    "Reason :",
    recommendation["Reason"]
)