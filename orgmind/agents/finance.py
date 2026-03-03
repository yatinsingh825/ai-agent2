import re
import json
from agents.base_agent import BaseAgent
from llm.ollama_client import generate_response


def extract_json(text):
    """
    Extracts first valid JSON object from LLM output.
    Removes inline comments and explanation wrappers.
    """
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None

    json_str = match.group(0)

    # Remove inline comments (// ...)
    json_str = re.sub(r"//.*", "", json_str)

    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return None


class FinanceAgent(BaseAgent):

    def __init__(self):
        super().__init__("Finance")

    def evaluate(self, company_state, ceo_decision):

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

        if parsed is None:
            print("⚠ Finance JSON parsing failed. Raw output:")
            print(response)

        return parsed