import os
import yt_dlp
import asyncio
import re
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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "👋 Welcome!\n\n"
        "Send a video link from:\n"
        "• YouTube\n"
        "• Instagram\n"
        "• Facebook\n"
        "• TikTok\n\n"
        "Example:\n"
        "https://youtube.com/watch?v=xxxx\n\n"
        "I'll download the video for you."
    )


def choose_format(url):

    url = url.lower()

    if "youtube.com" in url or "youtu.be" in url:
        return "bv*+ba/b"

    if "instagram.com" in url:
        return "best"

    if "facebook.com" in url or "fb.watch" in url:
        return "best"

    if "tiktok.com" in url:
        return "best"

    return "best"


async def auto_download(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    msg = await update.message.reply_text("🔎 Processing link...")

    link_match = re.search(r'https?://\S+', text)

    if not link_match:

        await msg.edit_text(
            "❌ I couldn't find a valid video link.\n\n"
            "Send a link from:\n"
            "• YouTube\n"
            "• Instagram\n"
            "• Facebook\n"
            "• TikTok\n\n"
            "Example:\n"
            "https://youtube.com/watch?v=xxxx"
        )
        return

    url = link_match.group(0)

    video_format = choose_format(url)

    ydl_opts = {
        "format": video_format,
        "format_sort": ["res", "ext:mp4:m4a"],
        "outtmpl": f"{DOWNLOAD_DIR}/%(title)s.%(ext)s",
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": True,
        "nocheckcertificate": True,
        "geo_bypass": True,
        "retries": 5,
        "fragment_retries": 5,
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "web"]
            }
        }
    }

    try:

        await msg.edit_text("📥 Downloading...")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = await asyncio.to_thread(
                ydl.extract_info, url, True
            )

            file_path = ydl.prepare_filename(info)

        title = info.get("title", "Video")

        size_mb = os.path.getsize(file_path) / (1024 * 1024)

        if size_mb > MAX_SIZE_MB:

            os.remove(file_path)

            await msg.edit_text(
                "📦 Video too large for Telegram.\nGenerating download link..."
            )

            with yt_dlp.YoutubeDL({"quiet": True}) as ydl:

                info = await asyncio.to_thread(
                    ydl.extract_info, url, False
                )

                video_url = None

                for f in info.get("formats", []):

                    if f.get("url") and f.get("ext") in ["mp4", "m4v"]:
                        video_url = f["url"]
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

    print("🚀 Stable Downloader Bot Running")

    app.run_polling()


if __name__ == "__main__":
    main()
