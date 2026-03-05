import re
import json
from agents.base_agent import BaseAgent


def extract_json(text):
    """
    Extract JSON object from LLM output.
    """

    match = re.search(r"\{.*\}", text, re.DOTALL)

    if not match:
        return None

    json_str = match.group(0)

    # Remove inline comments
    json_str = re.sub(r"//.*", "", json_str)

    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return None


# ----------------------------------
# 🧠 Startup Strategy Engine
# ----------------------------------

def ceo_decision(state, event):

    runway = state["runway_months"]
    reputation = state["reputation"]
    product = state["product_quality"]

    # ----------------------------------
    # 1️⃣ Viral Opportunity → Growth Push
    # ----------------------------------
    if event == "Viral Social Media Trend":
        return {
            "strategy": "Growth Push",
            "budget_change": 2000,
            "user_growth": 0.15,
            "revenue_growth": 0.06,
            "confidence": 0.9
        }

    # ----------------------------------
    # 2️⃣ Emergency Survival
    # ----------------------------------
    if runway < 1.5:
        return {
            "strategy": "Emergency Cost Reduction",
            "budget_change": -1500,
            "user_growth": 0.02,
            "revenue_growth": 0.02,
            "confidence": 0.9
        }

    # ----------------------------------
    # 3️⃣ Balanced Strategy
    # ----------------------------------
    if runway < 3:

        if product < 6:
            return {
                "strategy": "Improve Product Quality",
                "budget_change": 1500,
                "user_growth": 0.05,
                "revenue_growth": 0.04,
                "confidence": 0.8
            }

        if reputation < 5:
            return {
                "strategy": "Brand Recovery Marketing",
                "budget_change": 1200,
                "user_growth": 0.06,
                "revenue_growth": 0.04,
                "confidence": 0.75
            }

        return {
            "strategy": "Balanced Strategy",
            "budget_change": 500,
            "user_growth": 0.05,
            "revenue_growth": 0.04,
            "confidence": 0.7
        }

    # ----------------------------------
    # 4️⃣ Aggressive Growth
    # ----------------------------------
    return {
        "strategy": "Aggressive Growth",
        "budget_change": 3000,
        "user_growth": 0.10,
        "revenue_growth": 0.05,
        "confidence": 0.8
    }


class CEOAgent(BaseAgent):

    def __init__(self):
        super().__init__("CEO")

    def propose(self, company_state, market_event):
        """
        Generate CEO strategy decision.
        """

        decision = ceo_decision(company_state, market_event)

        return decision