def close_round(company, round_name, amount, dilution):

    company.cash += amount
    company.valuation += amount
    company.founder_ownership *= (1 - dilution)

    company.last_funding_round = round_name
    company.months_since_funding = 0

    print(f"   💰 {round_name} funding secured: ${amount:,}")

    return {
        "round": round_name,
        "raised": amount,
        "valuation": company.valuation,
        "dilution": dilution
    }


def attempt_funding(company):

    if company.bankrupt:
        return None

    if company.months_since_funding < 6:
        return None

    # ---------------------------------
    # Pre-Seed Bridge Round
    # ---------------------------------
    if company.last_funding_round is None:

        if (
            company.months_since_funding >= 15
            and company.users >= 700
            and company.cash < 150000
            and company.product_quality >= 5
        ):

            print(
                f"   💡 Bridge round triggered "
                f"(users={company.users}, cash=${company.cash:,.0f})"
            )

            return close_round(
                company,
                "Pre-Seed Bridge",
                75000,
                0.07
            )

    # ---------------------------------
    # Seed Round
    # ---------------------------------
    if company.last_funding_round is None:

        if (
            company.users >= 1300
            and company.product_quality >= 5.5
            and company.reputation >= 3.5
        ):

            return close_round(
                company,
                "Seed",
                100000,
                0.10
            )

    # ---------------------------------
    # Series A
    # ---------------------------------
    if company.last_funding_round in ("Seed", "Pre-Seed Bridge"):

        if (
            company.months_since_funding >= 6
            and company.revenue >= 35000
            and company.users >= 2500
            and company.valuation >= 400000
        ):

            amount = int(company.valuation * 0.25)

            return close_round(
                company,
                "Series A",
                amount,
                0.20
            )

    # ---------------------------------
    # Series B
    # ---------------------------------
    if company.last_funding_round == "Series A":

        if (
            company.months_since_funding >= 6
            and company.revenue >= 100000
            and company.users >= 5000
            and company.is_public is False
            and company.valuation >= 1000000
        ):

            amount = int(company.valuation * 0.30)

            return close_round(
                company,
                "Series B",
                amount,
                0.15
            )

    return None