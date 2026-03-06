from agents.base_agent import BaseAgent


# ----------------------------------
# 💰 Finance Decision Logic
# ----------------------------------

def finance_decision(company_state, ceo_decision):

    runway = company_state["runway_months"]
    proposed_budget = ceo_decision.get("budget_change", 0)

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

    return {
        "approved_budget_change": approved,
        "confidence": 0.7,
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