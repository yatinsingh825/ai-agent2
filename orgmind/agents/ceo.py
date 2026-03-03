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


class CEOAgent(BaseAgent):

    def __init__(self):
        super().__init__("CEO")

    def propose(self, company_state, market_event):

        prompt = f"""
You are the CEO of a startup.

Company State:
{company_state}

Market Event:
{market_event}

Suggest ONE strategic decision for this month.

Respond strictly in JSON format like this.
IMPORTANT:
- budget_change must be an INTEGER.
- confidence must be a decimal between 0 and 1.
- Do NOT include explanations outside JSON.

{{
  "strategy": "...",
  "budget_change": 5000,
  "user_growth": 0.1,
  "revenue_growth": 0.05,
  "confidence": 0.8
}}
"""

        response = generate_response(prompt)

        parsed = extract_json(response)

        if parsed is None:
            print("⚠ CEO JSON parsing failed. Raw output:")
            print(response)

        return parsed