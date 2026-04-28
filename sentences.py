from datetime import datetime, date
from ai import ask_gemini
from telegram_helper import send_message
from storage import save_batch, get_total_count


DAILY_TOPICS = [
    "starting and ending conversations naturally",
    "expressing opinions and agreeing or disagreeing politely",
    "asking for help or clarification",
    "talking about plans and future events",
    "apologizing and thanking people",
    "expressing feelings and emotions",
    "talking about problems and solutions",
    "casual small talk about daily life",
    "making suggestions and invitations",
    "storytelling and sharing news",
    "phone and video call conversations",
    "shopping and everyday errands",
    "expressing surprise and reactions",
    "talking about the past and memories",
]


def get_todays_topic():
    day = date.today().toordinal()
    return DAILY_TOPICS[day % len(DAILY_TOPICS)]


def send_daily_sentences():
    today = datetime.now()
    date_str = today.strftime("%B %d, %Y")
    topic = get_todays_topic()
    total = get_total_count()

    system = """You are an English conversation coach helping an intermediate 
English speaker living in Victoria, Canada improve their speaking skills.

Your student understands common words and can hold basic conversations.
They want to sound more natural, like people in everyday movies and TV shows.

Rules:
- Use clear natural English at intermediate level
- Not too simple like a textbook, not too advanced like formal writing
- No slang, no idioms that are hard to guess
- No business or academic language
- Sentences real people say in normal daily life
- Think of the English level in shows like Friends or Modern Family
- Plain text only, no special characters"""

    prompt = f"""Today's topic: {topic}
Date: {date_str}

Write exactly 10 natural English sentences for an intermediate speaker.
Each sentence should be useful in real daily life situations.

Use EXACTLY this format for each sentence, nothing else:

SENTENCE: I have a lot going on right now, can we talk later?
WHEN: When you are busy and someone wants to talk
EXAMPLE: A friend calls you during a busy afternoon

SENTENCE: Sorry, I did not quite catch that. Could you say it again?
WHEN: When you did not hear or understand someone
EXAMPLE: In a noisy place or on the phone

Write all 10 sentences in this exact format.
Plain text only. No numbers. No asterisks. No dashes."""

    raw = ask_gemini(prompt, system=system, max_tokens=2048)

    # Parse sentences from response
    sentences = []
    current = {}

    for line in raw.split("\n"):
        line = line.strip()
        if not line:
            continue

        if line.upper().startswith("SENTENCE:"):
            if current.get("sentence"):
                sentences.append(current)
                current = {}
            current["sentence"] = line.split(":", 1)[1].strip()

        elif line.upper().startswith("WHEN:"):
            current["when"] = line.split(":", 1)[1].strip()

        elif line.upper().startswith("EXAMPLE:"):
            current["example"] = line.split(":", 1)[1].strip()

    if current.get("sentence"):
        sentences.append(current)

    sentences = sentences[:10]

    # Build message
    lines = [
        f"Evening English - {date_str}",
        f"Topic: {topic.title()}",
        f"Collection so far: {total + len(sentences)} sentences",
        "─" * 30,
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

    # Save to storage
    if sentences:
        save_batch(date_str, sentences)

    send_message("\n".join(lines))
