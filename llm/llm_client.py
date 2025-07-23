# llm/llm_client.py

import os
import requests
import json
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("API_KEY")

if not API_KEY:
    raise ValueError("API_KEY not set in .env")

# Gemini 2.5 Pro endpoint
API_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"

def get_answer(prompt: str) -> str:
    """
    Sends a prompt to Gemini 2.5 Pro and returns the model's text response.
    """
    system_instruction = "You are a code expert. Answer the question accurately based on the given code context."

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": f"{system_instruction}\n\n{prompt}"
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(API_URL, headers={"Content-Type": "application/json"}, json=payload)
        response.raise_for_status()

        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()

    except requests.exceptions.RequestException as e:
        return f"❌ Request error: {e}"
    except KeyError:
        return f"❌ Unexpected response: {response.text}"
