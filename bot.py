import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
DOWNLOAD_FOLDER = "downloads"

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)


async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):

    url = update.message.text.strip()

    msg = await update.message.reply_text("🔎 Checking link...")

    ydl_opts = {
        "outtmpl": f"{DOWNLOAD_FOLDER}/%(title)s.%(ext)s",
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": True
    }

    try:
        await msg.edit_text("📥 Downloading video...")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            title = info.get("title", "video")

        await msg.edit_text("📤 Uploading to Telegram...")

        await update.message.reply_video(
            video=open(file_path, "rb"),
            caption=f"✅ {title}"
        )

        os.remove(file_path)

        await msg.delete()

    except Exception as e:
        print(e)
        await msg.edit_text("❌ Failed to download video")


def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, download_video)
    )

    print("🚀 Advanced Video Downloader Bot Started")

    app.run_polling()


if __name__ == "__main__":
    main()
