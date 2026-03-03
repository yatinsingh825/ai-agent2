import requests
import json
import config

def generate_response(prompt):
    payload = {
        "model": config.MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(config.OLLAMA_URL, json=payload)

    if response.status_code == 200:
        return response.json()["response"]
    else:
        raise Exception(f"Ollama error: {response.text}")