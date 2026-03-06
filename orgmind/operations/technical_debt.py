def calculate_debt_penalty(company) -> dict:
    """
    Returns penalties applied to KPIs based on current technical debt level.
    """
    debt = company.technical_debt

    if debt <= 0.1:
        return {
            "product_quality_penalty": 0.0,
            "reputation_penalty": 0.0,
            "infra_cost_increase": 0.0,
            "severity": "none"
        }
    elif debt <= 0.3:
        return {
            "product_quality_penalty": debt * 0.3,
            "reputation_penalty": 0.05,
            "infra_cost_increase": debt * 100,
            "severity": "low"
        }
    elif debt <= 0.6:
        return {
            "product_quality_penalty": debt * 0.6,
            "reputation_penalty": 0.15,
            "infra_cost_increase": debt * 200,
            "severity": "medium"
        }
    else:
        # Critical debt — triggers outage-level damage
        return {
            "product_quality_penalty": debt * 1.0,
            "reputation_penalty": 0.4,
            "infra_cost_increase": debt * 400,
            "severity": "critical"
        }


def apply_technical_debt_penalties(company):
    """Apply debt penalties to company state. Returns severity."""
    penalties = calculate_debt_penalty(company)

    company.product_quality = max(
        1.0,
        company.product_quality - penalties["product_quality_penalty"]
    )
    company.reputation = max(
        0.5,
        company.reputation - penalties["reputation_penalty"]
    )
    company.infra_cost += penalties["infra_cost_increase"]

    return penalties["severity"]