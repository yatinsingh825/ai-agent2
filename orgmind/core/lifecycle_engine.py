class LifecycleEngine:

    @staticmethod
    def process(company):

        if company.bankrupt:
            return

        # --------------------------------
        # Hiring Logic
        # --------------------------------
        revenue_per_engineer = company.revenue / max(1, company.engineers)

        if (
            company.runway_months > 6
            and revenue_per_engineer > 6000
            and company.cash > 80000
        ):

            company.engineers += 1

            engineer_salary = 4000
            company.burn_rate += engineer_salary

            print(f"   👷 Hired engineer #{company.engineers}")

        # --------------------------------
        # Late Stage Efficiency
        # --------------------------------
        if company.engineers > 20:

            efficiency_bonus = 0.02 * (company.engineers / 10)
            company.product_quality = min(
                10,
                company.product_quality + efficiency_bonus
            )

        # --------------------------------
        # IPO Event
        # --------------------------------
        if (
            not company.is_public
            and company.valuation >= 10000000
            and company.users >= 50000
            and company.revenue >= 200000
            and company.reputation >= 7
        ):

            company.is_public = True

            company.share_price = company.valuation / 1000000

            print("\n📈 IPO EVENT: Company is now public!")
            print(f"   Share Price: ${company.share_price:.2f}")
            print(f"   Market Cap: ${company.valuation:,.0f}")