"""
storage.py
Stores all sentences in a JSON file that persists between runs.
Each entry: { "date": "April 27 2026", "sentences": [...] }
"""

import json
import os

STORAGE_FILE = "sentences_storage.json"


def load_all() -> list:
    """Load all stored sentence sets."""
    if not os.path.exists(STORAGE_FILE):
        return []
    try:
        with open(STORAGE_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []


def save_batch(date_str: str, sentences: list):
    """Save a new batch of sentences."""
    all_data = load_all()

    # Avoid duplicate entries for same date
    all_data = [d for d in all_data if d.get("date") != date_str]

    all_data.append({
        "date": date_str,
        "sentences": sentences
    })

    # Keep last 365 days only
    all_data = all_data[-365:]

    try:
        with open(STORAGE_FILE, "w") as f:
            json.dump(all_data, f, indent=2)
    except Exception as e:
        print(f"Storage save error: {e}")


def get_all_sentences() -> list:
    """Get every single sentence ever stored as a flat list."""
    all_data = load_all()
    flat = []
    for batch in all_data:
        for s in batch.get("sentences", []):
            flat.append(s)
    return flat


def get_total_count() -> int:
    """Total number of sentences stored."""
    return len(get_all_sentences())
