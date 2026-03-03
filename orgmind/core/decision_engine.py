def negotiate_decision(company, ceo_decision, finance_decision, cto_decision):

    if not ceo_decision:
        return None

    ceo_budget = ceo_decision.get("budget_change", 0)
    ceo_conf = ceo_decision.get("confidence", 0.5)

    finance_budget = ceo_budget
    finance_conf = 0.5

    if finance_decision:
        finance_budget = finance_decision.get("approved_budget_change", ceo_budget)
        finance_conf = finance_decision.get("confidence", 0.5)

    cto_budget = ceo_budget
    cto_conf = 0.5

    if cto_decision:
        cto_budget = cto_decision.get("recommended_budget_change", ceo_budget)
        cto_conf = cto_decision.get("confidence", 0.5)

    total_conf = ceo_conf + finance_conf + cto_conf

    if total_conf == 0:
        final_budget = ceo_budget
    else:
        final_budget = int(
            (ceo_budget * ceo_conf +
             finance_budget * finance_conf +
             cto_budget * cto_conf)
            / total_conf
        )

    final_decision = ceo_decision.copy()
    final_decision["budget_change"] = final_budget

    # Attach CTO technical impact
    if cto_decision and "tech_impact" in cto_decision:
        final_decision["tech_impact"] = cto_decision["tech_impact"]

    return final_decision