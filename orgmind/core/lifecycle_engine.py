class LifecycleEngine:

    @staticmethod
    def process(company):

        if company.bankrupt:
            return

        # --------------------------------
        # Hiring Logic (STRICT CAP FIX)
        # --------------------------------

        revenue_per_engineer = company.revenue / max(1, company.engineers)
        engineer_salary = 4000

        # Hard safety caps
        MAX_ENGINEERS = 15
        MAX_HIRE_PER_MONTH = 2

        if (
            company.runway_months > 8
            and revenue_per_engineer > 8000
            and company.cash > 300000
            and company.engineers < MAX_ENGINEERS
        ):

            potential_hires = int(revenue_per_engineer / 12000)

            # Ensure we never exceed hiring cap
            new_hires = max(1, potential_hires)
            new_hires = min(new_hires, MAX_HIRE_PER_MONTH)

            # Prevent exceeding total engineer cap
            new_hires = min(new_hires, MAX_ENGINEERS - company.engineers)

            if new_hires > 0:

                company.engineers += new_hires
                company.burn_rate += new_hires * engineer_salary

                print(
                    f"   👷 Hired {new_hires} engineer(s) "
                    f"[total engineers: {company.engineers}]"
                )

        # --------------------------------
        # Late Stage Efficiency Boost
        # --------------------------------

        if company.engineers > 10:

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