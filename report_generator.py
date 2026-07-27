# ==========================================
# AI Investment Intelligence Platform
# File: report_generator.py
# Version: 1.0
# Status: Stable
# ==========================================


# ----------------------------------
# Investment Report Generator
# ----------------------------------

def generate_investment_report(

    company,

    financial_health_score,

    valuation_score,

    recommendation

):

    report = f"""
Investment Analysis Report
==========================

Company : {company}

Financial Health Score : {financial_health_score}/100

Valuation Score : {valuation_score}/40

Final Recommendation : {recommendation}

------------------------------------------

Summary

{company} demonstrates a stable financial position based on
the available financial analysis.

The valuation assessment indicates that investors should
carefully compare the current market price with the
estimated intrinsic value before making an investment
decision.

Overall, the platform recommends:

{recommendation}

------------------------------------------

This report was generated automatically by the
AI Investment Intelligence Platform.
"""

    return report