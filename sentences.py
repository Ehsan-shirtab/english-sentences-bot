from datetime import datetime, date
from ai import ask_gemini
from telegram_helper import send_message
from storage import save_batch, get_total_count


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
They want to sound more natural like people in everyday movies and TV shows.

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
Each sentence should be useful in real daily conversations.

Write only the sentences, one per line, nothing else.
No explanations, no labels, no numbers, no extra text.
Just 10 sentences, each on its own line.

Example output:
I have a lot going on right now, can we talk later?
Sorry, I did not quite catch that. Could you say it again?
Could you give me a hand with this?

Plain text only. Just the 10 sentences. Nothing else."""

    raw = ask_gemini(prompt, system=system, max_tokens=2048)

    # Parse sentences
    sentences = []
    for line in raw.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.upper().startswith("SENTENCE:"):
            line = line.split(":", 1)[1].strip()
        # Skip any lines that look like labels or headers
        if len(line) > 10 and not line.endswith(":"):
            sentences.append({"sentence": line, "when": "", "example": ""})

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

    lines.append("")
    lines.append("─" * 30)
    lines.append("Send 'review' anytime to practice your full collection!")

    # Save to storage
    if sentences:
        save_batch(date_str, sentences)

    send_message("\n".join(lines))
