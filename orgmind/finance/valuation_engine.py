def calculate_valuation(company):

    # -----------------------------
    # Core Valuation Components
    # -----------------------------

    revenue_component = company.revenue * 8
    user_component = company.users * 20

    quality_component = company.product_quality * 5000
    reputation_component = company.reputation * 3000

    # -----------------------------
    # Technical Debt Penalty
    # -----------------------------
    debt_penalty = company.technical_debt * 10000

    # -----------------------------
    # Total Valuation
    # -----------------------------
    valuation = (
        revenue_component
        + user_component
        + quality_component
        + reputation_component
        - debt_penalty
    )

    # Prevent unrealistic low valuations
    valuation = max(50_000, int(valuation))

    company.valuation = valuation

    return valuation