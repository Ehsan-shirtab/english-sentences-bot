"""
ai.py - Google Gemini API wrapper
"""

import os
import time
import requests

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.0-flash-latest:generateContent"
)


def ask_gemini(prompt: str, system: str = None, max_tokens: int = 2048) -> str:
    if not GEMINI_API_KEY:
        return "GEMINI_API_KEY not set."

    full_prompt = f"{system}\n\n{prompt}" if system else prompt

    headers = {"Content-Type": "application/json"}
    body = {
        "contents": [{"parts": [{"text": full_prompt}]}],
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature": 0.9,
        }
    }

    for attempt in range(3):
        try:
            r = requests.post(
                f"{GEMINI_URL}?key={GEMINI_API_KEY}",
                headers=headers,
                json=body,
                timeout=60,
            )
            r.raise_for_status()
            data = r.json()
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()

        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response else 0
            if status == 429:
                wait = 30 * (attempt + 1)
                print(f"Rate limited. Waiting {wait}s...")
                time.sleep(wait)
                continue
            return f"Gemini API error {status}: {e}"

        except Exception as e:
            return f"Gemini API error: {e}"

    return "Gemini API error: Rate limit hit after 3 retries."
