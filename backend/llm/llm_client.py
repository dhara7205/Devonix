# llm/llm_client.py
import os
import requests
import json

CONFIG_FILE = os.path.join(os.getcwd(), "qa_service_config.json")

def _load_config():
    if not os.path.exists(CONFIG_FILE):
        raise ValueError("❌ LLM config not set. Please call /qa/config first.")
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    api_key = cfg.get("api_key")
    if not api_key:
        raise ValueError("❌ API key missing in config. Please set via /qa/config.")
    return api_key

def get_answer(prompt: str) -> str:
    """
    Sends a prompt to Gemini 1.5 Flash and returns the model's text response.
    """
    api_key = _load_config()
    api_url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={api_key}"

    system_instruction = "You are a code expert. Answer the question accurately based on the given code context."

    payload = {
        "contents": [
            {"parts": [{"text": f"{system_instruction}\n\n{prompt}"}]}
        ]
    }

    try:
        response = requests.post(api_url, headers={"Content-Type": "application/json"}, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except requests.exceptions.RequestException as e:
        return f"❌ Request error: {e}"
    except KeyError:
        return f"❌ Unexpected response: {response.text}"
