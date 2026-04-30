"""
storage.py
Stores all sentences in a JSON file that persists between runs.
Each entry: { "date": "April 29 2026", "sentences": [...] }
"""

import json
import os

STORAGE_FILE = "sentences_storage.json"


def load_all() -> dict:
    if not os.path.exists(STORAGE_FILE):
        return {}
    try:
        with open(STORAGE_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def save_all(data: dict):
    try:
        with open(STORAGE_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Storage save error: {e}")


def save_batch(date_str: str, sentences: list, user_id: str = "global"):
    all_data = load_all()

    if user_id not in all_data:
        all_data[user_id] = []

    # Remove duplicate date entry
    all_data[user_id] = [
        d for d in all_data[user_id] if d.get("date") != date_str
    ]

    all_data[user_id].append({
        "date": date_str,
        "sentences": sentences
    })

    # Keep last 365 days per user
    all_data[user_id] = all_data[user_id][-365:]

    save_all(all_data)


def get_all_sentences(user_id: str = "global") -> list:
    all_data = load_all()
    user_data = all_data.get(user_id, [])
    flat = []
    for batch in user_data:
        for s in batch.get("sentences", []):
            flat.append(s)
    return flat


def get_total_count(user_id: str = "global") -> int:
    return len(get_all_sentences(user_id))


def get_all_user_ids() -> list:
    all_data = load_all()
    return list(all_data.keys())


def register_user(user_id: str):
    all_data = load_all()
    if user_id not in all_data:
        all_data[user_id] = []
        save_all(all_data)
