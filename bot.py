import os
import yt_dlp
import asyncio
import re
import time
import threading

from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters
)

TOKEN = os.getenv("BOT_TOKEN")

DOWNLOAD_DIR = "downloads"
MAX_SIZE_MB = 80

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ------------------- KEEP ALIVE -------------------
app_web = Flask(__name__)

@app_web.route("/")
def home():
    return "Bot is alive ✅"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app_web.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web).start()

# ------------------- ANTI SPAM -------------------
user_last_request = {}

def is_spam(user_id):
    now = time.time()
    if user_id in user_last_request:
        if now - user_last_request[user_id] < 5:
            return True
    user_last_request[user_id] = now
    return False

# ------------------- START -------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome!\n\n"
        "Send video link (YouTube / Instagram / Facebook / TikTok)\n\n"
        "For MP3:\n"
        "Send: mp3 <link>"
    )

# ------------------- FORMAT -------------------
def choose_format(url, is_audio=False):

    url = url.lower()

    if is_audio:
        return "bestaudio"

    if "instagram.com" in url:
        return "best"

    if "facebook.com" in url or "fb.watch" in url:
        return "best"

    if "tiktok.com" in url:
        return "best"

    if "youtube.com" in url or "youtu.be" in url:
        return "best[ext=mp4][height<=720]/best"

    return "best"

# ------------------- DOWNLOAD -------------------
async def auto_download(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if is_spam(user_id):
        await update.message.reply_text("⏳ Wait a few seconds...")
        return

    text = update.message.text
    msg = await update.message.reply_text("🔎 Processing...")

    link_match = re.search(r'https?://\S+', text)

    if not link_match:
        await msg.edit_text("❌ Send a valid link.")
        return

    url = link_match.group(0)
    is_audio = text.lower().startswith("mp3")

    ydl_opts = {
        "format": choose_format(url, is_audio),
        "outtmpl": f"{DOWNLOAD_DIR}/%(title).50s.%(ext)s",
        "restrictfilenames": True,
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": True,
        "nocheckcertificate": True,
        "geo_bypass": True,

        # SPEED + STABILITY
        "socket_timeout": 20,
        "retries": 10,
        "fragment_retries": 10,
        "skip_unavailable_fragments": True,

        # YOUTUBE FIX
        "http_headers": {
            "User-Agent": "Mozilla/5.0"
        },

        "extractor_args": {
            "youtube": {
                "player_client": ["android", "web"]
            },
            "instagram": {
                "api_version": "v1"
            }
        }
    }

    # MP3 option
    if is_audio:
        ydl_opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
        }]

    try:
        await msg.edit_text("📥 Downloading...")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await asyncio.to_thread(ydl.extract_info, url, True)
            file_path = ydl.prepare_filename(info)

        title = info.get("title", "Media")

        size_mb = os.path.getsize(file_path) / (1024 * 1024)

        # Large file → link
        if size_mb > MAX_SIZE_MB:
            os.remove(file_path)

            await msg.edit_text("📦 File too large. Generating link...")

            with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
                info = await asyncio.to_thread(ydl.extract_info, url, False)

            video_url = info.get("url")

            keyboard = [
                [InlineKeyboardButton("⬇️ Download", url=video_url)]
            ]

            await msg.edit_text(
                f"🎬 {title}",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return

        await msg.edit_text("📤 Uploading...")

        with open(file_path, "rb") as f:
            if is_audio:
                await update.message.reply_audio(f, caption=f"🎵 {title}")
            else:
                await update.message.reply_video(f, caption=f"✅ {title}")

        os.remove(file_path)
        await msg.delete()

    except Exception as e:
        print("ERROR:", str(e))
        await msg.edit_text("❌ Failed. Try another link.")

# ------------------- MAIN (FINAL FIX) -------------------
def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    app = ApplicationBuilder().token(TOKEN).build()

    # FIX webhook safely
    loop.run_until_complete(
        app.bot.delete_webhook(drop_pending_updates=True)
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, auto_download)
    )

    print("🚀 FINAL FAST BOT RUNNING")

    app.run_polling()


if __name__ == "__main__":
    main()
