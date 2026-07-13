"""
PocketPal webhook wrapper for PythonAnywhere (WSGI/Flask).

PythonAnywhere hosts WSGI apps, so instead of bot.py running its own
server, this file receives Telegram's webhook POSTs via Flask and hands
them to the python-telegram-bot Application.

Local development still works the simple way: `python bot.py` (polling).
"""

import asyncio

from flask import Flask, request
from telegram import Update

from bot import BOT_TOKEN, build_application

app = Flask(__name__)

# One event loop + application per worker process
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
application = build_application()
_initialized = False


def _ensure_initialized() -> None:
    """Initialize the PTB application once, on first webhook."""
    global _initialized
    if not _initialized:
        loop.run_until_complete(application.initialize())
        _initialized = True


@app.route("/")
def index():
    return "PocketPal is alive!"


@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    _ensure_initialized()
    update = Update.de_json(request.get_json(force=True), application.bot)
    loop.run_until_complete(application.process_update(update))
    return "ok"
