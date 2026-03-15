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


async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    context.user_data["url"] = url

    keyboard = [
        [
            InlineKeyboardButton("🎬 Video 360p", callback_data="360"),
            InlineKeyboardButton("🎬 Video 720p", callback_data="720"),
        ],
        [
            InlineKeyboardButton("🎬 Video 1080p", callback_data="1080"),
        ],
        [
            InlineKeyboardButton("🎵 Audio (MP3)", callback_data="audio")
        ],
        [
            InlineKeyboardButton("🔗 Direct Download Link", callback_data="link")
        ]
    ]

    await update.message.reply_text(
        "Choose download option:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    url = context.user_data.get("url")

    await query.edit_message_text("🔎 Processing...")

    option = query.data

    if option == "link":

        ydl_opts = {
            "quiet": True
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:

                info = ydl.extract_info(url, download=False)

                formats = info.get("formats", [])

                video_url = None

                for f in formats:
                    if f.get("ext") == "mp4":
                        video_url = f.get("url")
                        break

            keyboard = [
                [InlineKeyboardButton("⬇️ Download", url=video_url)]
            ]

            await query.edit_message_text(
                f"🎬 {info.get('title','Video')}",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        except:
            await query.edit_message_text("❌ Failed to fetch link")

        return

    if option == "audio":

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": f"{DOWNLOAD_DIR}/%(title)s.%(ext)s",
            "quiet": True
        }

    else:

        quality_map = {
            "360": "bestvideo[height<=360]+bestaudio/best",
            "720": "bestvideo[height<=720]+bestaudio/best",
            "1080": "bestvideo[height<=1080]+bestaudio/best"
        }

        ydl_opts = {
            "format": quality_map.get(option, "best"),
            "outtmpl": f"{DOWNLOAD_DIR}/%(title)s.%(ext)s",
            "merge_output_format": "mp4",
            "quiet": True
        }

    try:

        await query.edit_message_text("📥 Downloading...")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        await query.edit_message_text("📤 Uploading...")

        if option == "audio":

            await query.message.reply_audio(
                audio=open(file_path, "rb"),
                caption=info.get("title", "Audio")
            )

        else:

            await query.message.reply_video(
                video=open(file_path, "rb"),
                caption=info.get("title", "Video")
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
        CallbackQueryHandler(button_handler)
    )

    print("🚀 All-in-One Downloader Bot Running")

    app.run_polling()


if __name__ == "__main__":
    main()
