def attempt_ipo(company):

    if company.is_public:
        return None

    # IPO requirements
    if (
        company.revenue > 15000
        and company.reputation > 6
        and company.runway() > 2
    ):

        company.is_public = True

        company.share_price = company.valuation / company.total_shares
        company.market_cap = company.valuation

        return {
            "ipo_price": round(company.share_price, 2),
            "market_cap": company.market_cap
        }

    return None