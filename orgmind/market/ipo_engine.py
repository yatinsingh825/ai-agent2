def attempt_ipo(company):

    # Already public
    if company.is_public:
        return None

    # --------------------------------
    # IPO Requirements (Realistic)
    # --------------------------------
    if (
        company.valuation > 1_000_000
        and company.users > 10_000
        and company.reputation > 6
        and company.runway() > 3
    ):

        company.is_public = True

        company.share_price = company.valuation / company.total_shares
        company.market_cap = company.valuation

        return {
            "ipo_price": round(company.share_price, 2),
            "market_cap": company.market_cap
        }

    return None