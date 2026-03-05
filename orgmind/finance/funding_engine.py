def attempt_funding(company):

    # ---------------------------------
    # Do not fund bankrupt companies
    # ---------------------------------
    if company.bankrupt:
        return None

    # ---------------------------------
    # Cooldown Check
    # ---------------------------------
    if company.months_since_funding < 6:
        return None

    # ---------------------------------
    # Seed Round
    # ---------------------------------
    if (
        company.last_funding_round is None
        and company.users > 1200
        and company.product_quality > 6
        and company.revenue > 20000
    ):

        investment = 100000

        # Add cash
        company.cash += investment

        # Increase valuation
        company.valuation += investment * 3

        # Apply dilution
        dilution = 0.10
        company.founder_ownership *= (1 - dilution)

        # Update funding state
        company.last_funding_round = "Seed"
        company.months_since_funding = 0

        return {
            "round": "Seed",
            "raised": investment,
            "valuation": company.valuation,
            "dilution": dilution
        }

    # ---------------------------------
    # Series A
    # ---------------------------------
    if (
        company.last_funding_round == "Seed"
        and company.users > 5000
        and company.revenue > 60000
    ):

        # Protect against invalid valuation
        if company.valuation <= 0:
            return None

        raise_amount = int(company.valuation * 0.25)

        dilution = 0.20

        # Add funding
        company.cash += raise_amount

        # Ownership dilution
        company.founder_ownership *= (1 - dilution)

        # Increase valuation
        company.valuation += raise_amount

        # Update funding state
        company.last_funding_round = "Series A"
        company.months_since_funding = 0

        return {
            "round": "Series A",
            "raised": raise_amount,
            "valuation": company.valuation,
            "dilution": dilution
        }

    return None