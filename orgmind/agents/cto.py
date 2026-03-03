import json
import re
from agents.base_agent import BaseAgent
from llm.ollama_client import generate_response


def extract_json(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        json_str = match.group(0)
        json_str = re.sub(r"//.*", "", json_str)
        return json.loads(json_str)
    return None


class CTOAgent(BaseAgent):

    def __init__(self):
        super().__init__("CTO")

    def evaluate(self, company_state, ceo_decision):

        prompt = f"""
You are the CTO of a startup.

Company State:
{company_state}

CEO Proposal:
{ceo_decision}

Focus on:
- Infrastructure stability
- Product quality
- Technical debt
- Scalability risk

Respond strictly in JSON:

IMPORTANT:
- recommended_budget_change must be INTEGER
- confidence must be between 0 and 1

{{
  "recommended_budget_change": 3000,
  "tech_impact": {{
      "product_quality_change": 0.3,
      "technical_debt_change": -0.1
  }},
  "confidence": 0.8
}}
"""

        response = generate_response(prompt)

        try:
            return extract_json(response)
        except:
            print("⚠ CTO JSON parsing failed.")
            print(response)
            return None