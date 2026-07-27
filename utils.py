# ----------------------------------
# Number Formatting Utilities
# ----------------------------------

def format_number(value):

    if value is None:
        return "N/A"

    value = float(value)

    abs_value = abs(value)

    if abs_value >= 1_000_000_000_000:
        return f"{value/1_000_000_000_000:.2f}T"

    elif abs_value >= 1_000_000_000:
        return f"{value/1_000_000_000:.2f}B"

    elif abs_value >= 1_000_000:
        return f"{value/1_000_000:.2f}M"

    elif abs_value >= 1_000:
        return f"{value/1_000:.2f}K"

    return f"{value:.2f}"


# ----------------------------------
# Currency Formatting
# ----------------------------------

def format_currency(value, symbol="$"):

    if value is None:
        return "N/A"

    return f"{symbol}{format_number(value)}"


# ----------------------------------
# Percentage Formatting
# ----------------------------------

def format_percentage(value):

    if value is None:
        return "N/A"

    return f"{value:.2f}%"


# ----------------------------------
# Score Rating
# ----------------------------------

def get_health_rating(score):

    if score >= 90:
        return "Excellent"

    elif score >= 75:
        return "Strong"

    elif score >= 60:
        return "Average"

    elif score >= 40:
        return "Weak"

    return "High Risk"


# ----------------------------------
# Risk Badge
# ----------------------------------

def get_risk_badge(score):

    if score >= 90:
        return "🟢 Low Risk"

    elif score >= 75:
        return "🟢 Healthy"

    elif score >= 60:
        return "🟡 Moderate"

    elif score >= 40:
        return "🟠 Caution"

    return "🔴 High Risk"