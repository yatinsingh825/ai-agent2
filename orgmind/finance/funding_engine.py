import random


def close_round(company, round_name, amount, dilution):

    company.cash += amount
    company.valuation += amount
    company.founder_ownership *= (1 - dilution)

    company.last_funding_round = round_name
    company.months_since_funding = 0

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

    if hasattr(company, "last_funding_attempt"):
        if company.month - company.last_funding_attempt < 3:
            return None

    company.last_funding_attempt = company.month

    investor_interest = random.random()

    # ---------------------------------
    # Pre-Seed Bridge Round
    # ---------------------------------
    if company.last_funding_round is None:

        if (
            company.months_since_funding >= 15
            and company.users >= 700
            and company.cash < 80000
        ):

            if investor_interest < 0.7:

                return close_round(
                    company,
                    "Pre-Seed Bridge",
                    60000,
                    0.07
                )

    # ---------------------------------
    # Seed Round
    # ---------------------------------
    if company.last_funding_round is None:

        if (
            company.users >= 1500
            and company.product_quality >= 6
            and company.reputation >= 4
        ):

            if investor_interest < 0.75:

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
            and company.revenue >= 40000
            and company.users >= 3000
            and company.valuation >= 500000
        ):

            if investor_interest < 0.80:

                amount = int(company.valuation * 0.25)

                return close_round(
                    company,
                    "Series A",
                    amount,
                    0.20
                )

    return None