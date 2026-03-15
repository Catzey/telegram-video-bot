import os
import yt_dlp
import asyncio
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
MAX_SIZE_MB = 45

os.makedirs(DOWNLOAD_DIR, exist_ok=True)


# Welcome message
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "👋 Welcome!\n\n"
        "Send me a video link from:\n"
        "• YouTube\n"
        "• Instagram\n"
        "• Facebook\n"
        "• TikTok\n\n"
        "I will download the video for you."
    )


# Choose best format depending on platform
def choose_format(url):

    url = url.lower()

    if "youtube.com" in url or "youtu.be" in url:
        return "bestvideo+bestaudio/best"

    if "instagram.com" in url:
        return "best"

    if "facebook.com" in url or "fb.watch" in url:
        return "best"

    if "tiktok.com" in url:
        return "best"

    return "best"


async def auto_download(update: Update, context: ContextTypes.DEFAULT_TYPE):

    url = update.message.text.strip()

    msg = await update.message.reply_text("🔎 Processing link...")

    if "http" not in url:
        await msg.edit_text("❌ Please send a valid video link.")
        return

    video_format = choose_format(url)

    ydl_opts = {
        "format": video_format,
        "outtmpl": f"{DOWNLOAD_DIR}/%(title)s.%(ext)s",
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": True,
        "nocheckcertificate": True,
        "geo_bypass": True,
        "concurrent_fragment_downloads": 5,
        "retries": 3,
        "fragment_retries": 3
    }

    try:

        await msg.edit_text("📥 Downloading...")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await asyncio.to_thread(ydl.extract_info, url, True)
            file_path = ydl.prepare_filename(info)

        title = info.get("title", "Video")

        size_mb = os.path.getsize(file_path) / (1024 * 1024)

        # If file too big → send download link instead
        if size_mb > MAX_SIZE_MB:

            os.remove(file_path)

            await msg.edit_text("📦 File too large. Creating download link...")

            with yt_dlp.YoutubeDL({"quiet": True}) as ydl:

                info = await asyncio.to_thread(
                    ydl.extract_info, url, False
                )

                video_url = None

                for f in info.get("formats", []):
                    if f.get("ext") == "mp4":
                        video_url = f.get("url")
                        break

            keyboard = [
                [InlineKeyboardButton("⬇️ Download Video", url=video_url)]
            ]

            await msg.edit_text(
                f"🎬 {title}",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

            return

        await msg.edit_text("📤 Uploading...")

        await update.message.reply_video(
            video=open(file_path, "rb"),
            caption=f"✅ {title}"
        )

        os.remove(file_path)

        await msg.delete()

        await update.message.reply_text("📎 Send another link anytime!")

    except Exception as e:

        print(e)

        await msg.edit_text(
            "❌ Couldn't download this link.\n"
            "Make sure the video is public and try again."
        )


def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, auto_download)
    )

    print("🚀 Smart Downloader Bot Running")

    app.run_polling()


if __name__ == "__main__":
    main()
