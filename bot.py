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

DOWNLOAD_FOLDER = "downloads"

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)


async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):

    url = update.message.text.strip()

    context.user_data["url"] = url

    keyboard = [
        [
            InlineKeyboardButton("🎬 Download Video", callback_data="video"),
            InlineKeyboardButton("🎵 Download Audio", callback_data="audio")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Choose download type:",
        reply_markup=reply_markup
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    url = context.user_data.get("url")

    await query.edit_message_text("📥 Downloading...")

    if query.data == "video":

        ydl_opts = {
            "outtmpl": f"{DOWNLOAD_FOLDER}/%(title)s.%(ext)s",
            "format": "best[ext=mp4]/best",
            "noplaylist": True,
            "quiet": True
        }

    else:

        ydl_opts = {
            "outtmpl": f"{DOWNLOAD_FOLDER}/%(title)s.%(ext)s",
            "format": "bestaudio/best",
            "quiet": True
        }

    try:

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            title = info.get("title", "media")

        await query.edit_message_text("📤 Uploading...")

        if query.data == "video":

            await query.message.reply_video(
                video=open(file_path, "rb"),
                caption=f"✅ {title}"
            )

        else:

            await query.message.reply_audio(
                audio=open(file_path, "rb"),
                caption=f"🎵 {title}"
            )

        os.remove(file_path)

    except Exception as e:

        print(e)
        await query.edit_message_text("❌ Download failed")


def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link)
    )

    app.add_handler(
        CallbackQueryHandler(button_handler)
    )

    print("🚀 Downloader Bot Started")

    app.run_polling()


if __name__ == "__main__":
    main()
