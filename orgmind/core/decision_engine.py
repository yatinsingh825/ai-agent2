def negotiate_decision(company, ceo_decision, finance_decision, cto_decision):

    if not ceo_decision:
        return None

    ceo_budget = ceo_decision.get("budget_change", 0)
    ceo_conf = ceo_decision.get("confidence", 0.5)
    strategy = ceo_decision.get("strategy", "")

    runway = company.runway()

    # ----------------------------------
    # Emergency strategy detection
    # ----------------------------------
    emergency_strategies = (
        "Emergency Cost Reduction",
        "Reputation Crisis Recovery",
        "Survival Pivot"
    )

    is_emergency = strategy in emergency_strategies

    # ----------------------------------
    # Finance influence
    # ----------------------------------
    finance_budget = ceo_budget
    finance_conf = 0.5

    if finance_decision:
        finance_budget = finance_decision.get(
            "approved_budget_change",
            ceo_budget
        )
        finance_conf = finance_decision.get("confidence", 0.5)

    # ----------------------------------
    # CTO influence
    # ----------------------------------
    cto_budget = ceo_budget
    cto_conf = 0.5

    if cto_decision and not is_emergency:
        cto_budget = cto_decision.get(
            "recommended_budget_change",
            ceo_budget
        )
        cto_conf = cto_decision.get("confidence", 0.5)

    # ----------------------------------
    # Weighted negotiation
    # ----------------------------------
    total_conf = ceo_conf + finance_conf + cto_conf

    if total_conf == 0:
        final_budget = ceo_budget
    else:
        final_budget = int(
            (
                ceo_budget * ceo_conf
                + finance_budget * finance_conf
                + cto_budget * cto_conf
            )
            / total_conf
        )

    # ----------------------------------
    # Emergency spending ceiling
    # ----------------------------------
    if is_emergency:
        final_budget = min(final_budget, 500)

    # ----------------------------------
    # Healthy runway spending floor
    # ----------------------------------
    elif runway > 6:
        floor = int(abs(ceo_budget) * 0.3)
        final_budget = max(final_budget, floor)

    # ----------------------------------
    # Final decision object
    # ----------------------------------
    final_decision = ceo_decision.copy()
    final_decision["budget_change"] = final_budget

    if cto_decision and "tech_impact" in cto_decision and not is_emergency:
        final_decision["tech_impact"] = cto_decision["tech_impact"]

    return final_decision