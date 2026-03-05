class LifecycleEngine:

    @staticmethod
    def process(company):

        # Seed funding
        if (
            company.last_funding_round is None
            and company.valuation > 200000
        ):
            company.cash += 200000
            company.last_funding_round = "Seed"
            company.founder_ownership *= 0.85

            print("🚀 Seed Funding Raised: $200k")


        # Series A
        elif (
            company.last_funding_round == "Seed"
            and company.valuation > 800000
        ):
            company.cash += 1000000
            company.last_funding_round = "Series A"
            company.founder_ownership *= 0.8

            print("🚀 Series A Raised: $1M")


        # Series B
        elif (
            company.last_funding_round == "Series A"
            and company.valuation > 3000000
        ):
            company.cash += 5000000
            company.last_funding_round = "Series B"
            company.founder_ownership *= 0.8

            print("🚀 Series B Raised: $5M")


        # IPO
        elif (
            not company.is_public
            and company.valuation > 10000000
            and company.users > 50000
        ):
            company.is_public = True
            company.share_price = company.valuation / 1000000

            print("📈 IPO Event: Company is now public!")