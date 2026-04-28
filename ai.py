import os
import time
import requests

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.5-flash:generateContent"
)


def ask_gemini(prompt: str, system: str = None, max_tokens: int = 2048) -> str:
    if not GEMINI_API_KEY:
        return "GEMINI_API_KEY not set."

    # Keep it simple — combine system and prompt into one
    if system:
        full_prompt = system + "\n\n" + prompt
    else:
        full_prompt = prompt

    # Remove any special characters that might break the request
    full_prompt = full_prompt.encode("utf-8", errors="ignore").decode("utf-8")

    headers = {"Content-Type": "application/json"}
    body = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": full_prompt}]
            }
        ],
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
            elif status == 400:
                # Print full error for debugging
                try:
                    print(f"400 error details: {r.text}")
                    return f"Gemini 400 error: {r.text[:200]}"
                except:
                    return f"Gemini API error 400: {e}"
            return f"Gemini API error {status}: {e}"

        except Exception as e:
            return f"Gemini API error: {e}"

    return "Gemini API error: Rate limit hit after 3 retries."
