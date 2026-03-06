def calculate_churn_rate(company) -> float:
    """
    Returns monthly churn rate as a decimal (e.g. 0.03 = 3% churn).
    Tied to reputation, product quality, and technical debt.
    """
    base_churn = 0.02  # 2% baseline monthly churn

    # Reputation impact: bad rep = high churn, good rep = retention
    # reputation scale 0-10, neutral at 5
    reputation_factor = (5.0 - company.reputation) * 0.008

    # Product quality impact: below 6 causes churn, above 8 retains
    quality_factor = (6.0 - company.product_quality) * 0.005

    # Technical debt causes outages and frustration
    debt_factor = company.technical_debt * 0.03

    total_churn = base_churn + reputation_factor + quality_factor + debt_factor

    # Hard bounds: minimum 0.5% churn, maximum 12% churn per month
    return max(0.005, min(0.12, total_churn))


def apply_churn(company):
    """Apply monthly churn and return number of users lost."""
    churn_rate = calculate_churn_rate(company)
    users_lost = int(company.users * churn_rate)
    company.users = max(0, company.users - users_lost)
    return users_lost, churn_rate