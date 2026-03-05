def apply_decision(company, decision, event):

    # -----------------------------
    # Apply Market Event Effects
    # -----------------------------
    if "users" in event["impact"]:
        company.users += int(company.users * event["impact"]["users"])

    if "reputation" in event["impact"]:
        company.reputation += event["impact"]["reputation"]

    if "product_quality" in event["impact"]:
        company.product_quality += event["impact"]["product_quality"]
        company.technical_debt += 0.2

    # -----------------------------
    # Temporary Monthly Spend
    # -----------------------------
    extra_spend = 0

    # -----------------------------
    # Apply Decision Effects
    # -----------------------------
    if decision:

        proposed_budget = decision.get("budget_change", 0)

        # Campaign spend
        extra_spend += proposed_budget

        base_user_growth = decision.get("user_growth", 0)

        # -----------------------------
        # Growth Multipliers
        # -----------------------------
        quality_multiplier = max(0.5, company.product_quality / 10)
        reputation_multiplier = max(0.5, company.reputation / 10)

        adjusted_user_growth = base_user_growth * quality_multiplier * reputation_multiplier

        # -----------------------------
        # Reputation Penalty Layer
        # -----------------------------
        if company.reputation < 5:
            adjusted_user_growth *= 0.6

        if company.reputation < 4:
            adjusted_user_growth *= 0.3

        # -----------------------------
        # Apply User Growth
        # -----------------------------
        company.users += int(company.users * adjusted_user_growth)

        # SaaS revenue model
        company.revenue = int(company.users * company.arpu)

        # -----------------------------
        # Technical Impact
        # -----------------------------
        if "tech_impact" in decision:

            tech = decision["tech_impact"]

            company.product_quality += tech.get("product_quality_change", 0)
            company.technical_debt += tech.get("technical_debt_change", 0)

    # -----------------------------
    # Infrastructure Scaling
    # -----------------------------
    company.infra_cost = 1000 + (company.users * 0.5)

    # -----------------------------
    # Technical Debt Infrastructure Penalty
    # -----------------------------
    debt_penalty = company.technical_debt * 500
    company.infra_cost += debt_penalty

    # -----------------------------
    # Engineer Hiring Scaling
    # -----------------------------
    required_engineers = max(3, int(company.users / 800))

    if required_engineers > company.engineers:
        company.engineers = required_engineers

    # -----------------------------
    # Technical Debt Effects
    # -----------------------------
    if company.technical_debt > 0:

        debt_quality_penalty = company.technical_debt * 0.05
        company.product_quality -= debt_quality_penalty

    company.technical_debt = max(0, round(company.technical_debt, 2))

    # -----------------------------
    # Churn Model
    # -----------------------------
    base_churn = 0.02

    if company.product_quality < 5:
        base_churn += 0.03

    if company.reputation < 5:
        base_churn += 0.02

    churned_users = int(company.users * base_churn)
    company.users -= churned_users

    # -----------------------------
    # Recalculate Burn Rate
    # -----------------------------
    company.burn_rate = company.calculate_burn()

    # -----------------------------
    # Financial Flow
    # -----------------------------
    total_burn = company.burn_rate + extra_spend

    company.cash += company.revenue
    company.cash -= total_burn

    # Bankruptcy check
    if company.cash <= 0:
        company.bankrupt = True

    # -----------------------------
    # Reputation Recovery
    # -----------------------------
    if company.product_quality > 7:
        company.reputation += 0.2

    # -----------------------------
    # Metric Bounds
    # -----------------------------
    company.product_quality = max(0, min(company.product_quality, 10))
    company.reputation = max(1, min(company.reputation, 10))
    company.technical_debt = max(0, min(company.technical_debt, 10))

    # -----------------------------
    # Simulation Step
    # -----------------------------
    company.month += 1
    company.months_since_funding += 1