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
    users = state["users"]

    # ----------------------------------
    # 🚨 Company Distress Detection
    # ----------------------------------

    if reputation < 3:

        return {
            "strategy": "Reputation Crisis Recovery",
            "budget_change": 1000,
            "user_growth": 0.03,
            "revenue_growth": 0.02,
            "confidence": 0.9
        }

    if runway < 1.5:

        return {
            "strategy": "Emergency Cost Reduction",
            "budget_change": -1500,
            "user_growth": 0.02,
            "revenue_growth": 0.02,
            "confidence": 0.95
        }

    if users < 900 and runway < 4:

        return {
            "strategy": "Survival Pivot",
            "budget_change": -800,
            "user_growth": 0.03,
            "revenue_growth": 0.03,
            "confidence": 0.85
        }

    # ----------------------------------
    # Viral Opportunity
    # ----------------------------------

    if event == "Viral Social Media Trend":

        return {
            "strategy": "Growth Push",
            "budget_change": 2500,
            "user_growth": 0.15,
            "revenue_growth": 0.06,
            "confidence": 0.9
        }

    # ----------------------------------
    # Competitor Launch
    # ----------------------------------

    if event == "Competitor Launch":

        if product < 7:

            return {
                "strategy": "Product Improvement Sprint",
                "budget_change": 2000,
                "user_growth": 0.05,
                "revenue_growth": 0.04,
                "confidence": 0.85
            }

        return {
            "strategy": "Defend Market Share",
            "budget_change": 1800,
            "user_growth": 0.07,
            "revenue_growth": 0.05,
            "confidence": 0.8
        }

    # ----------------------------------
    # Positive Press Coverage
    # ----------------------------------

    if event == "Positive Press Coverage":

        return {
            "strategy": "Marketing Expansion",
            "budget_change": 2000,
            "user_growth": 0.10,
            "revenue_growth": 0.05,
            "confidence": 0.85
        }

    # ----------------------------------
    # Infrastructure Issue
    # ----------------------------------

    if event == "Tech Infrastructure Issue":

        return {
            "strategy": "Stability Focus",
            "budget_change": 1200,
            "user_growth": 0.04,
            "revenue_growth": 0.03,
            "confidence": 0.75
        }

    # ----------------------------------
    # Runway Warning Mode
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
            "budget_change": 800,
            "user_growth": 0.05,
            "revenue_growth": 0.04,
            "confidence": 0.7
        }

    # ----------------------------------
    # Aggressive Growth Mode
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

        decision = ceo_decision(company_state, market_event)

        return decision