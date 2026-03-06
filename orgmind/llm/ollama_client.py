import requests
import config
import sys


def generate_response(prompt, retries=1):
    """
    Send prompt to Ollama and return model response.
    Includes retry logic and stdout protection to prevent
    streaming collisions with the simulation loop.
    """

    payload = {
        "model": config.MODEL_NAME,
        "prompt": prompt,
        "stream": False  # CRITICAL: prevents streaming corruption
    }

    for attempt in range(retries + 1):

        try:
            # Flush stdout BEFORE request to avoid mixed prints
            sys.stdout.flush()

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

            result = data["response"]

            # Clean response to avoid weird console artifacts
            if isinstance(result, str):
                result = result.strip()

            # Flush again after processing
            sys.stdout.flush()

            return result

        except Exception as e:

            if attempt == retries:
                sys.stdout.flush()
                print(f"\n[LLM ERROR] {e}")
                return ""

    return ""