import os
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")

DOWNLOAD_DIR = "downloads"
MAX_SIZE_MB = 45

os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def choose_format(url):

    url = url.lower()

    if "youtube.com" in url or "youtu.be" in url:
        return "bestvideo+bestaudio/best"

    if "instagram.com" in url:
        return "best"

    if "tiktok.com" in url:
        return "best"

    if "facebook.com" in url or "fb.watch" in url:
        return "best"

    return "best"


async def auto_download(update: Update, context: ContextTypes.DEFAULT_TYPE):

    url = update.message.text.strip()

    msg = await update.message.reply_text("⚡ Processing link...")

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
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        title = info.get("title", "Video")

        size_mb = os.path.getsize(file_path) / (1024 * 1024)

        if size_mb > MAX_SIZE_MB:

            os.remove(file_path)

            await msg.edit_text("📦 File too large. Creating download link...")

            with yt_dlp.YoutubeDL({"quiet": True}) as ydl:

                info = ydl.extract_info(url, download=False)

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

    except Exception as e:

        print(e)

        await msg.edit_text("❌ Download failed")


def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, auto_download)
    )

    print("🚀 Smart Downloader Bot Running")

    app.run_polling()


if __name__ == "__main__":
    main()
