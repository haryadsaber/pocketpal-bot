# 🤖 PocketPal — Telegram Bot

A friendly general-purpose Telegram bot built with Python and [python-telegram-bot](https://python-telegram-bot.org/).

## Features

| Command | What it does |
|---------|--------------|
| /start  | Welcome message |
| /help   | List all commands |
| /roll   | Roll an animated dice 🎲 |
| /flip   | Flip a coin 🪙 |
| /joke   | Random joke 😄 |
| /time   | Current UTC time 🕐 |
| /id     | Your Telegram user & chat ID 🪪 |
| (any text) | Echoes it back 💬 |

## Files

- `bot.py` — the whole bot (polling locally, webhook on Render — auto-detected)
- `requirements.txt` — Python dependencies
- `render.yaml` — Render deploy configuration
- `.env.example` — template for your local token file

## Run locally (Windows)

```
py -m pip install -r requirements.txt
copy .env.example .env
```

Edit `.env` and paste your real token from @BotFather, then:

```
py bot.py
```

## Deploy free on PythonAnywhere (no credit card, ever)

1. Sign up free at [pythonanywhere.com](https://www.pythonanywhere.com) (Beginner plan). Your username becomes your bot's URL: `https://USERNAME.pythonanywhere.com`
2. Open a **Bash console** and run:
   ```
   git clone https://github.com/haryadsaber/pocketpal-bot.git
   cd pocketpal-bot
   pip install --user -r requirements.txt
   echo "BOT_TOKEN=your-token-here" > .env
   ```
3. Go to **Web** tab → **Add a new web app** → Manual configuration → Python 3.10
4. Set **Source code** to `/home/USERNAME/pocketpal-bot`, then edit the **WSGI configuration file** so it ends with:
   ```python
   import sys
   sys.path.insert(0, "/home/USERNAME/pocketpal-bot")
   from flask_app import app as application
   ```
5. Click **Reload**, then register the webhook (one-time, from the Bash console):
   ```
   python3 -c "import requests; print(requests.post('https://api.telegram.org/bot<TOKEN>/setWebhook', data={'url': 'https://USERNAME.pythonanywhere.com/<TOKEN>'}).json())"
   ```
6. Message your bot — done! Free apps just need the **"Run until 3 months from today"** button clicked when PythonAnywhere emails you (every 3 months).

## Alternative: deploy on Render

1. **Put the code on GitHub**
   - Create a free account at github.com → New repository (e.g. `pocketpal-bot`, public)
   - Upload all files from this folder (drag & drop works — no git needed).
     Note: `.gitignore` and `.env.example` are hidden files; `.env` (your real token) must NEVER be uploaded.

2. **Create the Render service**
   - Sign up free at render.com (GitHub login is easiest, no card required)
   - Click **New + → Web Service** → connect your repo
   - Render reads `render.yaml` automatically; otherwise set:
     - Build command: `pip install -r requirements.txt`
     - Start command: `python bot.py`
     - Instance type: **Free**
   - Under **Environment**, add: `BOT_TOKEN` = your token from @BotFather

3. **Deploy** — when logs show `Starting in WEBHOOK mode`, message your bot on Telegram. Done!

### Free tier notes

- Render free services sleep after 15 min without traffic. Because this bot uses **webhooks**, Telegram's message wakes it up automatically — the first reply after a long idle just takes ~30–60 s.
- Want instant replies 24/7? Create a free monitor at [uptimerobot.com](https://uptimerobot.com) pinging `https://YOUR-APP.onrender.com` every 5 minutes to keep it awake (750 free hours/month is enough for one always-on service).

## Customize

- Rename the bot: message @BotFather → `/setname`
- Change the picture: @BotFather → `/setuserpic`
- Register the command menu: @BotFather → `/setcommands` and paste:

```
start - Say hello
help - Show all commands
roll - Roll a dice
flip - Flip a coin
joke - Hear a random joke
time - Current UTC time
id - Show your Telegram ID
```
