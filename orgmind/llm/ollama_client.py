import requests
import config
import sys


def generate_response(prompt, retries=1):
    """
    Send prompt to Ollama and return model response.
    Includes retry logic and safer error handling.
    """

    payload = {
        "model": config.MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    for attempt in range(retries + 1):

        try:
            response = requests.post(
                config.OLLAMA_URL,
                json=payload,
                timeout=60
            )

            if response.status_code != 200:
                raise Exception(f"Ollama error: {response.text}")

            data = response.json()

            # Validate response format
            if "response" not in data:
                raise Exception(f"Invalid Ollama response: {data}")

            sys.stdout.flush()

            return data["response"]

        except Exception as e:

            if attempt == retries:
                print(f"[LLM ERROR] {e}")
                return ""

    return ""