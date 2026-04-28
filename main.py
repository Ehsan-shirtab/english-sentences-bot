"""
English Sentences Bot — main.py
Daily 10 sentences + flashcard review stored in Telegram.
"""

from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from sentences import send_daily_sentences
from review import handle_review
from telegram_helper import send_message

load_dotenv()

app = Flask(__name__)
SECRET = os.getenv("BOT_SECRET", "changeme")


@app.route("/")
def index():
    return "OK", 200


@app.route("/health")
def health():
    return "OK", 200
    
@app.route("/setup")
def setup_webhook():
    import requests
    token = os.getenv("TELEGRAM_TOKEN")
    render_url = "https://english-sentences-bot.onrender.com/webhook"
    r = requests.post(
        f"https://api.telegram.org/bot{token}/setWebhook",
        json={"url": render_url}
    )
    return r.json()

@app.route("/daily")
def daily():
    secret = request.args.get("secret", "")
    if secret != SECRET:
        return "Unauthorized", 401
    try:
        send_daily_sentences()
        return "OK", 200
    except Exception as e:
        print(f"Daily error: {e}")
        return "ERROR", 500


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"ok": True})

    try:
        message = data.get("message", {})
        text = message.get("text", "").strip()
        chat_id = str(message.get("chat", {}).get("id", ""))

        if not text or not chat_id:
            return jsonify({"ok": True})

        if text.lower() in ["/review", "review", "/flashcard", "flashcard"]:
            handle_review(chat_id)
        elif text.lower() in ["/help", "help", "/start", "start"]:
            send_message(
                "English Sentences Bot\n\n"
                "Every evening I send you 10 real English sentences "
                "to memorize and use in daily conversation.\n\n"
                "Commands:\n"
                "review - Get 10 random sentences to practice\n"
                "help - Show this message\n\n"
                "Just send 'review' anytime to practice!",
                chat_id=chat_id
            )
        else:
            send_message(
                "Send 'review' to practice random sentences from your collection!",
                chat_id=chat_id
            )

    except Exception as e:
        print(f"Webhook error: {e}")

    return jsonify({"ok": True})


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
