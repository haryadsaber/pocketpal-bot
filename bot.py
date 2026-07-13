"""
PocketPal — a friendly general-purpose Telegram bot.

Runs in two modes automatically:
  - Locally: long polling (just run `python bot.py`)
  - On Render: webhook mode (detected via RENDER_EXTERNAL_URL)
  - On PythonAnywhere: served via flask_app.py (WSGI)

Required environment variable:
  BOT_TOKEN — your token from @BotFather
"""

import logging
import os
import random
from datetime import datetime, timezone

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Load a .env file sitting next to this script if python-dotenv is installed.
# The explicit path matters on servers (e.g. PythonAnywhere), where the
# process's working directory is not the project folder.
try:
    from pathlib import Path

    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parent / ".env")
except ImportError:
    pass

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
# Quiet down noisy HTTP logs
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger("pocketpal")

BOT_TOKEN = os.environ.get("BOT_TOKEN")
# Render sets RENDER_EXTERNAL_URL automatically; WEBHOOK_URL works for other hosts
WEBHOOK_URL = os.environ.get("WEBHOOK_URL") or os.environ.get("RENDER_EXTERNAL_URL")
PORT = int(os.environ.get("PORT", "10000"))

JOKES = [
    "Why don't scientists trust atoms? Because they make up everything!",
    "I told my computer I needed a break, and now it won't stop sending me KitKat ads.",
    "Why did the scarecrow win an award? He was outstanding in his field.",
    "Parallel lines have so much in common. It's a shame they'll never meet.",
    "Why do programmers prefer dark mode? Because light attracts bugs.",
    "I'm reading a book about anti-gravity. It's impossible to put down!",
    "What do you call a fake noodle? An impasta.",
    "Why did the math book look sad? It had too many problems.",
    "I asked the librarian if the library had books on paranoia. She whispered, 'They're right behind you.'",
    "What do you call cheese that isn't yours? Nacho cheese.",
    "Why couldn't the bicycle stand up by itself? It was two tired.",
    "How does the ocean say hi? It waves.",
]

HELP_TEXT = (
    "🤖 <b>PocketPal — your pocket companion</b>\n\n"
    "Here's what I can do:\n\n"
    "/start — say hello\n"
    "/help — show this message\n"
    "/roll — roll a dice 🎲\n"
    "/flip — flip a coin 🪙\n"
    "/joke — hear a random joke 😄\n"
    "/time — current UTC time 🕐\n"
    "/id — your Telegram ID info 🪪\n\n"
    "Or just send me any message and I'll echo it back!"
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Greet the user."""
    user = update.effective_user
    name = user.first_name if user else "there"
    await update.message.reply_html(
        f"👋 Hey <b>{name}</b>! I'm <b>PocketPal</b>, your friendly pocket companion.\n\n"
        "I can roll dice, flip coins, tell jokes and more.\n"
        "Type /help to see everything I can do!"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show the help message."""
    await update.message.reply_html(HELP_TEXT)


async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Roll a dice using Telegram's native animated dice."""
    await update.message.reply_dice(emoji="🎲")


async def flip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Flip a coin."""
    result = random.choice(["Heads", "Tails"])
    await update.message.reply_text(f"🪙 It's... <b>{result}</b>!", parse_mode="HTML")


async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Tell a random joke."""
    await update.message.reply_text(f"😄 {random.choice(JOKES)}")


async def time_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show the current UTC time."""
    now = datetime.now(timezone.utc)
    await update.message.reply_text(
        f"🕐 Current UTC time:\n{now.strftime('%A, %B %d %Y — %H:%M:%S')} UTC"
    )


async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show the user's and chat's Telegram IDs."""
    user = update.effective_user
    chat = update.effective_chat
    await update.message.reply_html(
        f"🪪 <b>Your info</b>\n\n"
        f"User ID: <code>{user.id}</code>\n"
        f"Name: {user.full_name}\n"
        f"Username: @{user.username if user.username else '(none)'}\n"
        f"Chat ID: <code>{chat.id}</code>"
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo back any regular text message."""
    await update.message.reply_text(f"💬 You said: {update.message.text}")


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle unknown commands."""
    await update.message.reply_text(
        "🤔 I don't know that command. Try /help to see what I can do!"
    )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors so the bot never crashes silently."""
    logger.error("Exception while handling an update:", exc_info=context.error)


def build_application():
    """Create the bot application with all handlers registered."""
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("roll", roll))
    app.add_handler(CommandHandler("flip", flip))
    app.add_handler(CommandHandler("joke", joke))
    app.add_handler(CommandHandler("time", time_command))
    app.add_handler(CommandHandler("id", id_command))
    app.add_handler(MessageHandler(filters.COMMAND, unknown))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    app.add_error_handler(error_handler)
    return app


def main() -> None:
    if not BOT_TOKEN:
        raise SystemExit(
            "ERROR: BOT_TOKEN environment variable is not set.\n"
            "Locally: create a .env file with BOT_TOKEN=your-token\n"
            "On Render: add BOT_TOKEN in the Environment tab."
        )

    app = build_application()

    if WEBHOOK_URL:
        # Webhook mode (Render). Telegram pushes updates to our URL —
        # this also wakes the free instance up when it has spun down.
        base = WEBHOOK_URL.rstrip("/")
        logger.info("Starting in WEBHOOK mode on port %s -> %s", PORT, base)
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=BOT_TOKEN,
            webhook_url=f"{base}/{BOT_TOKEN}",
            drop_pending_updates=True,
        )
    else:
        # Local development: simple polling
        logger.info("Starting in POLLING mode (local development)")
        app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
