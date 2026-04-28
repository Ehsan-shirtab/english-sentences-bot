import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
RENDER_URL = "https://english-sentences-bot.onrender.com/webhook"

url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
response = requests.post(url, json={"url": RENDER_URL})
print(response.json())
