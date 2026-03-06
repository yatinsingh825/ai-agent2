from operations.churn_model import apply_churn
from operations.technical_debt import apply_technical_debt_penalties


def apply_decision(company, decision, event):

    # -----------------------------
    # Event Reputation Effects
    # -----------------------------
    EVENT_REPUTATION_IMPACT = {
        "Positive Press Coverage": 0.5,
        "Viral Social Media Trend": 0.3,
        "Competitor Launch": -0.3,
        "Tech Infrastructure Issue": -0.5
    }

    rep_change = EVENT_REPUTATION_IMPACT.get(event["name"], 0)
    company.reputation += rep_change

    # -----------------------------
    # Apply Market Event Effects
    # -----------------------------
    if "users" in event["impact"]:
        company.users += int(company.users * event["impact"]["users"])

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
        extra_spend += proposed_budget

        base_user_growth = decision.get("user_growth", 0)

        # -----------------------------
        # Growth Multipliers
        # -----------------------------
        quality_multiplier = max(0.5, company.product_quality / 10)
        reputation_multiplier = max(0.5, company.reputation / 10)

        adjusted_user_growth = (
            base_user_growth * quality_multiplier * reputation_multiplier
        )

        # Reputation penalties
        if company.reputation < 5:
            adjusted_user_growth *= 0.6

        if company.reputation < 4:
            adjusted_user_growth *= 0.3

        # Apply growth
        company.users += int(company.users * adjusted_user_growth)

        # SaaS revenue model
        company.revenue = int(company.users * company.arpu)

        # -----------------------------
        # Technical Impact
        # -----------------------------
        if "tech_impact" in decision:

            tech = decision["tech_impact"]
            quality_change = tech.get("product_quality_change", 0)

            # Redirect overflow improvements
            if company.product_quality >= 9.5:

                company.reputation += quality_change * 0.3
                company.technical_debt = max(
                    0,
                    company.technical_debt - 0.05
                )

            else:

                company.product_quality += quality_change

            company.technical_debt += tech.get(
                "technical_debt_change",
                0
            )

    # -----------------------------
    # Infrastructure Scaling
    # -----------------------------
    company.infra_cost = 1000 + (company.users * 0.5)

    # -----------------------------
    # Engineer Hiring Scaling
    # -----------------------------
    required_engineers = max(3, int(company.users / 800))

    if required_engineers > company.engineers:
        company.engineers = required_engineers

    # -----------------------------
    # Apply Technical Debt Model
    # -----------------------------
    severity = apply_technical_debt_penalties(company)

    if severity in ("medium", "critical"):
        print(f"   🔥 Tech debt severity: {severity.upper()}")

    # -----------------------------
    # Apply Churn Model
    # -----------------------------
    users_lost, churn_rate = apply_churn(company)

    if churn_rate > 0.05:
        print(
            f"   ⚠️ High churn: {churn_rate:.1%} "
            f"({users_lost} users lost)"
        )

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

    if company.cash <= 0:
        company.bankrupt = True

    # -----------------------------
    # Reputation Recovery
    # -----------------------------
    if company.product_quality >= 8.0:

        company.reputation = min(
            10,
            company.reputation + 0.15
        )

    elif company.product_quality >= 6.5:

        company.reputation = min(
            10,
            company.reputation + 0.05
        )

    # -----------------------------
    # Metric Bounds
    # -----------------------------
    company.product_quality = max(
        0,
        min(company.product_quality, 10)
    )

    # Reputation floor prevents collapse
    company.reputation = max(
        1.0,
        min(company.reputation, 10)
    )

    company.technical_debt = max(
        0,
        min(company.technical_debt, 10)
    )

    company.users = max(0, company.users)

    # -----------------------------
    # Simulation Step
    # -----------------------------
    company.month += 1
    company.months_since_funding += 1