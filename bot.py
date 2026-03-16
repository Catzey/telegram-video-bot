import os
import yt_dlp
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    await update.message.reply_text("Downloading... ⏳")

    ydl_opts = {
        'format': 'best',
        'outtmpl': 'video.%(ext)s'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_name = ydl.prepare_filename(info)

        await update.message.reply_video(video=open(file_name, 'rb'))

        os.remove(file_name)

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    print("🚀 Downloader Bot Running")

    app.run_polling()

if __name__ == "__main__":
    main()
