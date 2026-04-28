# English Sentences Bot

Every evening, 10 real natural English sentences delivered to your Telegram.
Send "review" anytime for flashcard practice from your growing collection.

---

## How It Works

Every evening the bot sends you 10 sentences like this:

```
Evening English - April 27, 2026
Topic: Expressing Opinions Politely
Total sentences in your collection: 120

1. I see where you're coming from, but I think...
   When: Politely disagreeing with someone
   Example: In a meeting when you have a different opinion

2. That's a fair point, actually.
   When: Agreeing after someone makes a good argument
   Example: During any discussion or debate
```

Send "review" to your bot anytime and get 10 random sentences from your entire collection to practice like flashcards.

---

## Setup

### Step 1 - Create a NEW Telegram Bot
1. Open Telegram, search @BotFather
2. Send /newbot
3. Give it a name like "My English Bot"
4. Copy the token

### Step 2 - Get your Chat ID
Send any message to your new bot, then visit:
```
https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
```
Find "chat":{"id": 123456789} - that is your Chat ID.
Or message @userinfobot on Telegram.

### Step 3 - Push to GitHub
```bash
cd english-sentences-bot
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/english-sentences-bot.git
git push -u origin main
```

### Step 4 - Deploy on Render
1. Go to render.com, New, Web Service
2. Connect your GitHub repo
3. Add environment variables:
   - TELEGRAM_TOKEN
   - TELEGRAM_CHAT_ID
   - GEMINI_API_KEY (same key as your other bot)
   - BOT_SECRET (any random string)
4. Start Command: gunicorn main:app --bind 0.0.0.0:$PORT
5. Deploy

### Step 5 - Register Telegram Webhook
Paste in browser (replace values):
```
https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook?url=https://english-sentences-bot.onrender.com/webhook
```

### Step 6 - Set up cron-job.org

Add these 2 jobs:

Daily Sentences (9 PM Vancouver = 04:03 UTC next day):
```
https://english-sentences-bot.onrender.com/daily?secret=YOUR_SECRET
```
Schedule: 0 4 * * * (daily at 04:00 UTC)

Keep Alive (every 5 minutes):
```
https://english-sentences-bot.onrender.com/health
```
Schedule: every 5 minutes

---

## Commands

Send these to your bot on Telegram:

| Command | What it does |
|---------|-------------|
| review | 10 random sentences from your collection |
| help | Show all commands |

---

## Your Collection Grows Every Day

Day 1: 10 sentences
Day 7: 70 sentences
Day 30: 300 sentences
Day 100: 1,000 sentences
Day 365: 3,650 sentences

After a few months you will have hundreds of real natural sentences
stored on your phone, searchable in Telegram, reviewable anytime.
