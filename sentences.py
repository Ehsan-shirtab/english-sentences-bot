"""
sentences.py
Generates and sends 10 real English sentences every evening.
Sentences are real, natural, intermediate level — mix of casual and professional.
Also stores them for flashcard review.
"""

import json
from datetime import datetime, date
from ai import ask_gemini
from telegram_helper import send_message
from storage import save_batch, get_total_count


# Rotate topic focus daily so sentences stay fresh and varied
DAILY_TOPICS = [
    "starting and ending conversations naturally",
    "expressing opinions and agreeing or disagreeing politely",
    "asking for help or clarification at work",
    "talking about plans, schedules, and future events",
    "apologizing, thanking, and being polite in social situations",
    "expressing feelings and emotions naturally",
    "talking about problems and offering solutions",
    "casual small talk about weather, weekends, and daily life",
    "professional workplace communication and meetings",
    "storytelling, sharing news, and updating someone",
    "phone and video call phrases",
    "shopping, ordering food, and everyday errands",
    "making suggestions and invitations",
    "expressing surprise, excitement, and reactions",
]


def get_todays_topic():
    day = date.today().toordinal()
    return DAILY_TOPICS[day % len(DAILY_TOPICS)]


def parse_sentences(text: str) -> list:
    """Parse the AI response into a clean list of sentence objects."""
    sentences = []
    lines = text.strip().split("\n")

    current = {}
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Detect numbered sentence line like "1. I'll get right on it."
        if line and line[0].isdigit() and ". " in line[:4]:
            if current:
                sentences.append(current)
            parts = line.split(". ", 1)
            if len(parts) == 2:
                current = {"sentence": parts[1].strip(), "when": "", "example": ""}

        elif line.lower().startswith("when:") or line.lower().startswith("use when:"):
            current["when"] = line.split(":", 1)[1].strip()

        elif line.lower().startswith("example:"):
            current["example"] = line.split(":", 1)[1].strip()

    if current:
        sentences.append(current)

    return sentences[:10]


def send_daily_sentences():
    today = datetime.now()
    date_str = today.strftime("%B %d, %Y")
    topic = get_todays_topic()
    total = get_total_count()

    system = """You are an English conversation coach helping an intermediate 
English speaker living in Victoria, Canada improve their natural speaking skills.
You teach real sentences that native speakers actually use every day.
Never use asterisks, underscores, or markdown. Plain text only."""

    prompt = f"""Today's topic: {topic}
Date: {date_str}

Generate exactly 10 real, natural English sentences that an intermediate speaker 
can memorize and use in real daily conversations. 

These sentences should:
- Sound completely natural, like something from a movie or real conversation
- Be useful immediately in everyday life in Canada
- Mix casual and professional situations
- Be intermediate level, not too simple and not too complex
- Cover the topic: {topic}

For each sentence write EXACTLY in this format:

1. [The sentence]
When: [One short phrase describing when to use it]
Example: [A very short example situation, max 10 words]

2. [The sentence]
When: [One short phrase]
Example: [Short situation]

Continue for all 10 sentences.

Plain text only. No special characters."""

    raw = ask_gemini(prompt, system=system, max_tokens=2048)
    sentences = parse_sentences(raw)

    # Build the Telegram message
    lines = [
        f"Evening English - {date_str}",
        f"Topic: {topic.title()}",
        f"Total sentences in your collection: {total + len(sentences)}",
        f"{'─' * 30}",
        ""
    ]

    for i, s in enumerate(sentences, 1):
        lines.append(f"{i}. {s['sentence']}")
        if s.get("when"):
            lines.append(f"   When: {s['when']}")
        if s.get("example"):
            lines.append(f"   Example: {s['example']}")
        lines.append("")

    lines.append("─" * 30)
    lines.append("Send 'review' anytime to practice your full collection!")

    message = "\n".join(lines)

    # Save to storage
    save_batch(date_str, sentences)

    # Send to Telegram
    send_message(message)
