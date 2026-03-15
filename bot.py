import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
DOWNLOAD_DIR = "downloads"
MAX_SIZE_MB = 45  # keep below Telegram limits for safety

os.makedirs(DOWNLOAD_DIR, exist_ok=True)


async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    status = await update.message.reply_text("🔎 Checking link...")

    ydl_opts = {
        "outtmpl": f"{DOWNLOAD_DIR}/%(title)s.%(ext)s",
        "format": "best",
        "noplaylist": True,
        "quiet": True,
        "merge_output_format": "mp4",
        "nocheckcertificate": True,
        "geo_bypass": True
    }

    try:
        await status.edit_text("📥 Downloading...")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        size_mb = os.path.getsize(file_path) / (1024 * 1024)

        if size_mb > MAX_SIZE_MB:
            os.remove(file_path)
            await status.edit_text(
                f"⚠️ Video too large ({size_mb:.1f}MB).\nTry a shorter video."
            )
            return

        await status.edit_text("📤 Uploading...")

        await update.message.reply_video(
            video=open(file_path, "rb"),
            caption=f"✅ {info.get('title','Video')}"
        )

        os.remove(file_path)

        await status.delete()

    except Exception as e:
        print(e)
        await status.edit_text("❌ Download failed")


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, download_video)
    )

    print("🚀 Ultimate Downloader Bot Running")

    app.run_polling()


if __name__ == "__main__":
    main()
