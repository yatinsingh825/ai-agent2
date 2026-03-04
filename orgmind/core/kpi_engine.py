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

        # Budget change becomes temporary campaign spend
        extra_spend += proposed_budget

        base_user_growth = decision.get("user_growth", 0)
        base_revenue_growth = decision.get("revenue_growth", 0)

        quality_multiplier = max(0.5, company.product_quality / 10)
        reputation_multiplier = max(0.5, company.reputation / 10)

        adjusted_user_growth = base_user_growth * quality_multiplier
        adjusted_revenue_growth = base_revenue_growth * reputation_multiplier

        company.users += int(company.users * adjusted_user_growth)
        company.revenue += int(company.revenue * adjusted_revenue_growth)

        # Apply technical impact if exists
        if "tech_impact" in decision:

            tech = decision["tech_impact"]

            company.product_quality += tech.get("product_quality_change", 0)
            company.technical_debt += tech.get("technical_debt_change", 0)

    # -----------------------------
    # Technical Debt Effects
    # -----------------------------
    if company.technical_debt > 0:

        debt_penalty = company.technical_debt * 0.05
        company.product_quality -= debt_penalty

        extra_spend += int(company.technical_debt * 500)

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
    # Financial Flow
    # -----------------------------
    total_burn = company.burn_rate + extra_spend

    company.cash += company.revenue
    company.cash -= total_burn

    # -----------------------------
    # Reputation Bounds
    # -----------------------------
    company.reputation = max(2, min(company.reputation, 10))

    # -----------------------------
    # Simulation Step Progress
    # -----------------------------
    company.month += 1
    company.months_since_funding += 1