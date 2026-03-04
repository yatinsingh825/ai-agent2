def attempt_funding(company):

   
    # ---------------------------------
    # Cooldown Check
    # ---------------------------------
    if company.months_since_funding < 6:
        return None

    if company.valuation <= 0:
        return None

    # ---------------------------------
    # Funding Calculation
    # ---------------------------------
    # Raise 20% of valuation
    raise_amount = int(company.valuation * 0.2)

    # Dilution calculation
    new_shares = raise_amount / company.valuation
    dilution = new_shares

    # ---------------------------------
    # Apply Funding
    # ---------------------------------
    company.cash += raise_amount
    company.founder_ownership *= (1 - dilution)

    company.last_funding_round = "Series A"

    # Reset cooldown after funding
    company.months_since_funding = 0

    return {
        "raised": raise_amount,
        "valuation": company.valuation,
        "dilution": round(dilution, 2),
        "round": company.last_funding_round
    }