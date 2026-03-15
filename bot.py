import os
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

TOKEN = os.getenv("BOT_TOKEN")
DOWNLOAD_DIR = "downloads"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)


# Progress hook
def progress_hook(d):
    if d["status"] == "downloading":
        percent = d.get("_percent_str", "").strip()
        print("Downloading:", percent)


async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    context.user_data["url"] = url

    keyboard = [
        [
            InlineKeyboardButton("360p", callback_data="360"),
            InlineKeyboardButton("720p", callback_data="720"),
            InlineKeyboardButton("1080p", callback_data="1080")
        ]
    ]

    await update.message.reply_text(
        "🎬 Choose video quality:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def download_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    quality = query.data
    url = context.user_data.get("url")

    await query.edit_message_text("📥 Downloading...")

    format_map = {
        "360": "bestvideo[height<=360]+bestaudio/best[height<=360]",
        "720": "bestvideo[height<=720]+bestaudio/best[height<=720]",
        "1080": "bestvideo[height<=1080]+bestaudio/best[height<=1080]"
    }

    ydl_opts = {
        "outtmpl": f"{DOWNLOAD_DIR}/%(title)s.%(ext)s",
        "format": format_map.get(quality, "best"),
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": True,
        "progress_hooks": [progress_hook],
        "nocheckcertificate": True,
        "geo_bypass": True
    }

    try:

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        await query.edit_message_text("📤 Uploading...")

        await query.message.reply_video(
            video=open(file_path, "rb"),
            caption=f"✅ {info.get('title','Video')}"
        )

        os.remove(file_path)

        await query.delete_message()

    except Exception as e:
        print(e)
        await query.edit_message_text("❌ Download failed")


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link)
    )

    app.add_handler(
        CallbackQueryHandler(download_handler)
    )

    print("🚀 Universal Downloader Bot Started")

    app.run_polling()


if __name__ == "__main__":
    main()
