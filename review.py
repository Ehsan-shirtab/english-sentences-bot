"""
review.py
Flashcard review — sends 10 random sentences from the full collection.
Triggered when user sends 'review' to the bot.
"""

import random
from telegram_helper import send_message
from storage import get_all_sentences, get_total_count


def handle_review(chat_id: str):
    all_sentences = get_all_sentences()
    total = get_total_count()

    if total == 0:
        send_message(
            "No sentences stored yet! Your first batch arrives this evening.",
            chat_id=chat_id
        )
        return

    # Pick 10 random sentences
    sample_size = min(10, total)
    selected = random.sample(all_sentences, sample_size)

    lines = [
        f"Flashcard Review",
        f"Showing {sample_size} random sentences from your {total} total",
        f"{'─' * 30}",
        ""
    ]

    for i, s in enumerate(selected, 1):
        lines.append(f"{i}. {s['sentence']}")
        if s.get("when"):
            lines.append(f"   When: {s['when']}")
        lines.append("")

    lines.append("─" * 30)
    lines.append(f"You have {total} sentences in your collection.")
    lines.append("Send 'review' again for a different random set!")

    message = "\n".join(lines)
    send_message(message, chat_id=chat_id)
