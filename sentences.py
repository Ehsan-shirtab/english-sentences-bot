from datetime import datetime, date
from ai import ask_gemini
from telegram_helper import send_message
from storage import save_batch, get_total_count, get_all_user_ids, load_all
import os

TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


DAILY_TOPICS = [
    # Daily Conversations
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
    # Social Situations
    "meeting someone new and introducing yourself",
    "talking at a party or social gathering",
    "giving and receiving compliments",
    "comforting someone who is sad or stressed",
    "celebrating good news with someone",
    "catching up with a friend you have not seen in a while",
    "making and cancelling plans with friends",
    "talking about hobbies and interests",
    "recommending a movie, book, or restaurant",
    "disagreeing with someone without being rude",
    "ending a conversation politely",
    # Everyday Life in Canada
    "talking about the weather in Canada",
    "asking for directions and explaining where to go",
    "taking public transit and asking about buses",
    "talking to a neighbour",
    "at the grocery store or supermarket",
    "at a coffee shop or cafe",
    "at a restaurant ordering food",
    "returning something to a store",
    "at the doctor or pharmacy",
    "talking about Canadian holidays and events",
    # Work and Professional
    "starting and ending a work meeting",
    "asking your boss or coworker for something",
    "giving a simple update on your work",
    "handling a mistake at work professionally",
    "asking for feedback or an opinion",
    "welcoming a new coworker",
    "talking about deadlines and schedules",
    "saying no politely at work",
    # Feelings and Personal
    "talking about being tired or stressed",
    "expressing excitement about something coming up",
    "talking about being worried or nervous",
    "sharing good news about your life",
    "talking about a difficult situation you are in",
    "expressing that you need some time alone",
    "talking about your goals and dreams",
    "expressing that you changed your mind",
    # Practical Situations
    "dealing with a problem at home like repairs",
    "talking on the phone with a service or company",
    "asking someone to repeat or slow down",
    "explaining something you do not know the word for",
    "asking for a recommendation or advice",
    "talking about money and prices politely",
    "making a complaint politely",
    "asking for permission to do something",
    "explaining you are running late",
    "wrapping up a conversation and saying goodbye",
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
    "meeting someone new and introducing yourself",
    "giving and receiving compliments",
    "comforting someone who is sad or stressed",
    "catching up with a friend you have not seen in a while",
    "making and cancelling plans with friends",
    "talking about hobbies and interests",
    "recommending a movie book or restaurant",
    "disagreeing with someone without being rude",
    "talking about the weather in Canada",
    "asking for directions",
    "at a coffee shop or cafe",
    "at a restaurant ordering food",
    "returning something to a store",
    "at the doctor or pharmacy",
    "talking about being tired or stressed",
    "expressing excitement about something",
    "talking about being worried or nervous",
    "sharing good news about your life",
    "expressing that you changed your mind",
    "asking for permission to do something",
    "explaining you are running late",
    "wrapping up a conversation and saying goodbye",
    "talking about your goals and dreams",
    "making a complaint politely",
    "asking for a recommendation or advice",
    "talking about money and prices politely",
]


def get_todays_topic():
    day = date.today().toordinal()
    return DAILY_TOPICS[day % len(DAILY_TOPICS)]


def generate_sentences(topic: str, date_str: str) -> tuple:
    """Generate 10 sentences and return raw response and parsed sentences."""

    system = """You are an English conversation coach helping intermediate
English speakers improve their natural speaking skills.

Rules:
- Use clear natural English at intermediate level
- Not too simple like a textbook, not too advanced
- No slang, no idioms that are hard to guess
- No business or academic language
- Sentences real people say in normal daily life
- Think of the English level in shows like Friends or Modern Family
- Plain text only, no special characters"""

    prompt = f"""Today's topic: {topic}
Date: {date_str}

Write exactly 10 natural English sentences for an intermediate speaker.
Each sentence should be useful in real daily conversations.

Write only the sentences, one per line, nothing else.
No explanations, no labels, no numbers, no extra text.
Just 10 sentences each on its own line.

Plain text only. Just the 10 sentences. Nothing else."""

    raw = ask_gemini(prompt, system=system, max_tokens=2048)

    sentences = []
    for line in raw.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.upper().startswith("SENTENCE:"):
            line = line.split(":", 1)[1].strip()
        if len(line) > 10 and not line.endswith(":"):
            sentences.append({"sentence": line, "when": "", "example": ""})

    return sentences[:10]


def build_message(sentences: list, topic: str, date_str: str, total: int) -> str:
    lines = [
        f"Evening English - {date_str}",
        f"Topic: {topic.title()}",
        f"Collection so far: {total} sentences",
        "─" * 30,
        ""
    ]

    for i, s in enumerate(sentences, 1):
        lines.append(f"{i}. {s['sentence']}")

    lines.append("")
    lines.append("─" * 30)
    lines.append("Send 'review' anytime to practice your full collection!")

    return "\n".join(lines)


def send_daily_sentences():
    """
    Send daily sentences to ALL registered users.
    Called by cron job every evening.
    """
    today = datetime.now()
    date_str = today.strftime("%B %d, %Y")
    topic = get_todays_topic()

    # Generate sentences once — same for everyone today
    sentences = generate_sentences(topic, date_str)

    if not sentences:
        print("No sentences generated — skipping")
        return

    # Get all registered users
    all_user_ids = get_all_user_ids()

    # Always include the owner
    if TELEGRAM_CHAT_ID and TELEGRAM_CHAT_ID not in all_user_ids:
        all_user_ids.append(TELEGRAM_CHAT_ID)

    # If no users yet just send to owner
    if not all_user_ids:
        all_user_ids = [TELEGRAM_CHAT_ID] if TELEGRAM_CHAT_ID else []

    for user_id in all_user_ids:
        try:
            # Save sentences for this user
            save_batch(date_str, sentences, user_id=user_id)
            total = get_total_count(user_id=user_id)

            # Build and send personalized message
            message = build_message(sentences, topic, date_str, total)
            send_message(message, chat_id=user_id)

        except Exception as e:
            print(f"Error sending to user {user_id}: {e}")

