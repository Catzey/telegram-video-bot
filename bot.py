import os
import yt_dlp
import asyncio
import re
import time

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

# Anti-spam
user_last_request = {}

def is_spam(user_id):
    now = time.time()
    if user_id in user_last_request:
        if now - user_last_request[user_id] < 5:
            return True
    user_last_request[user_id] = now
    return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome!\n\n"
        "Send a video link (YouTube, Instagram, Facebook, TikTok)\n\n"
        "For MP3:\n"
        "Send: mp3 <link>"
    )


def choose_format(url, is_audio=False):
    if is_audio:
        return "bestaudio"

    return "bestvideo[height<=720]+bestaudio/best[height<=720]"


def progress_hook(d):
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', '0%')
        print(f"Downloading {percent}")


async def auto_download(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if is_spam(user_id):
        await update.message.reply_text("⏳ Please wait a few seconds...")
        return

    text = update.message.text
    msg = await update.message.reply_text("🔎 Processing...")

    link_match = re.search(r'https?://\S+', text)

    if not link_match:
        await msg.edit_text("❌ Send a valid video link.")
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
        "socket_timeout": 15,
        "retries": 5,
        "progress_hooks": [progress_hook],
    }

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
                await update.message.reply_audio(audio=f, caption=f"🎵 {title}")
            else:
                await update.message.reply_video(video=f, caption=f"✅ {title}")

        os.remove(file_path)
        await msg.delete()

    except Exception as e:
        print("ERROR:", str(e))
        await msg.edit_text("❌ Failed. Try another link.")


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, auto_download)
    )

    print("🚀 PRO Downloader Bot Running")

    app.run_polling(poll_interval=2)


if __name__ == "__main__":
    main()
