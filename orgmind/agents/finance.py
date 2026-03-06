from agents.base_agent import BaseAgent


# ----------------------------------
# 💰 Finance Decision Logic
# ----------------------------------

def finance_decision(company_state, ceo_decision):

    runway = company_state["runway_months"]
    burn_rate = company_state["burn_rate"]
    revenue = company_state["revenue"]

    proposed_budget = ceo_decision.get("budget_change", 0)

    # ----------------------------------
    # Burn Multiple Calculation
    # ----------------------------------

    burn_multiple = burn_rate / max(1, revenue)

    # ----------------------------------
    # Runway-Based Budget Approval
    # ----------------------------------

    if runway > 12:

        approved = proposed_budget
        comment = "Runway healthy, approving full proposal."

    elif runway > 6:

        approved = int(proposed_budget * 0.75)
        comment = "Moderate runway, slightly reducing spend."

    elif runway > 3:

        approved = int(proposed_budget * 0.5)
        comment = "Runway tightening, approving half."

    else:

        approved = int(proposed_budget * 0.25)
        comment = "Runway critical, heavy budget reduction."

    # ----------------------------------
    # Burn Multiple Adjustment
    # ----------------------------------

    if burn_multiple > 3:

        approved = int(approved * 0.5)
        comment += " Burn multiple critical (>3), emergency cost control."

    elif burn_multiple > 2:

        approved = int(approved * 0.75)
        comment += " Burn multiple high (>2), reducing budget."

    elif burn_multiple < 1.2:

        approved = int(approved * 1.1)
        comment += " Burn efficient (<1.2), allowing slightly more investment."

    return {
        "approved_budget_change": approved,
        "confidence": 0.75,
        "burn_multiple": round(burn_multiple, 2),
        "comment": comment
    }


# ----------------------------------
# 🧠 Finance Agent
# ----------------------------------

class FinanceAgent(BaseAgent):

    def __init__(self):
        super().__init__("Finance")

    def evaluate(self, company_state, ceo_decision):
        """
        Finance reviews CEO proposal and adjusts budget.
        """

        decision = finance_decision(company_state, ceo_decision)

        return decision