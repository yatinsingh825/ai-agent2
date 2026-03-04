def calculate_valuation(company):

    revenue_component = company.revenue * 6

    user_component = company.users * 50

    reputation_bonus = company.reputation * 5000

    debt_penalty = company.technical_debt * 30000

    runway_bonus = 0
    if company.runway() > 3:
        runway_bonus = 20000

    valuation = (
        revenue_component
        + user_component
        + reputation_bonus
        + runway_bonus
        - debt_penalty
    )

    valuation = max(50000, int(valuation))

    company.valuation = valuation

    return valuation