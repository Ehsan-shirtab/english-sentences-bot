"""
telegram_helper.py - Send messages to Telegram
"""

import os
import requests
import time

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_message(text: str, chat_id: str = None):
    target = chat_id or CHAT_ID
    if not TELEGRAM_TOKEN or not target:
        print("TELEGRAM_TOKEN or CHAT_ID not set")
        return

    # Clean markdown symbols
    clean = (text
        .replace("*", "").replace("_", "").replace("`", "")
        .replace("[", "").replace("]", "").replace("#", "")
    )

    # Split at 3800 chars on paragraph boundaries
    chunks = []
    while len(clean) > 3800:
        split_at = clean.rfind("\n\n", 0, 3800)
        if split_at == -1:
            split_at = clean.rfind("\n", 0, 3800)
        if split_at == -1:
            split_at = 3800
        chunks.append(clean[:split_at].strip())
        clean = clean[split_at:].strip()
    if clean:
        chunks.append(clean)

    for i, chunk in enumerate(chunks):
        if not chunk:
            continue
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": target,
            "text": chunk,
            "disable_web_page_preview": True,
        }
        try:
            r = requests.post(url, json=payload, timeout=15)
            r.raise_for_status()
            if len(chunks) > 1:
                time.sleep(1)
        except Exception as e:
            print(f"Telegram error on chunk {i+1}: {e}")
