import re
import json
from agents.base_agent import BaseAgent
from llm.ollama_client import generate_response


def extract_json(text):

    match = re.search(r"\{.*\}", text, re.DOTALL)

    if not match:
        return None

    json_str = match.group(0)
    json_str = re.sub(r"//.*", "", json_str)

    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return None


class FinanceAgent(BaseAgent):

    def __init__(self):
        super().__init__("Finance")

    def evaluate(self, company_state, ceo_decision):

        runway = company_state["runway_months"]
        proposed_budget = ceo_decision.get("budget_change", 0)

        prompt = f"""
You are the Finance Head of a startup.

Company State:
{company_state}

CEO Proposed Decision:
{ceo_decision}

If the proposed budget increase risks bankruptcy within 3 months,
reduce the budget_change value.

Respond strictly in JSON format:
{{
  "approved_budget_change": number,
  "confidence": 0.7,
  "comment": "short explanation"
}}
"""

        response = generate_response(prompt)

        parsed = extract_json(response)

        # -----------------------------
        # Fallback logic if LLM fails
        # -----------------------------
        if parsed is None:

            if runway > 2:
                approved = proposed_budget
            elif runway > 1:
                approved = int(proposed_budget * 0.7)
            else:
                approved = int(proposed_budget * 0.4)

            return {
                "approved_budget_change": approved,
                "confidence": 0.6,
                "comment": "Fallback finance logic applied"
            }

        return parsed