def attempt_ipo(company):

    # --------------------------------
    # Already Public
    # --------------------------------
    if company.is_public:
        return None

    # --------------------------------
    # Minimum Company Age
    # --------------------------------
    if company.month < 18:
        return None

    # --------------------------------
    # IPO Readiness Conditions
    # --------------------------------
    valuation_ok = company.valuation >= 750_000
    users_ok = company.users >= 4000
    revenue_ok = company.revenue >= 80_000
    reputation_ok = company.reputation >= 8.0
    runway_ok = company.runway() > 3

    if (
        valuation_ok
        and users_ok
        and revenue_ok
        and reputation_ok
        and runway_ok
    ):

        company.is_public = True

        company.share_price = company.valuation / company.total_shares
        company.market_cap = company.valuation

        return {
            "ipo_price": round(company.share_price, 2),
            "market_cap": company.market_cap
        }

    return None