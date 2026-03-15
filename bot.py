import os
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")


async def generate_link(update: Update, context: ContextTypes.DEFAULT_TYPE):

    url = update.message.text.strip()

    msg = await update.message.reply_text("🔎 Fetching video info...")

    ydl_opts = {
        "quiet": True,
        "nocheckcertificate": True,
        "geo_bypass": True
    }

    try:

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(url, download=False)

            title = info.get("title", "Video")

            formats = info.get("formats", [])

            video_url = None

            for f in formats:
                if f.get("ext") == "mp4" and f.get("url"):
                    video_url = f["url"]
                    break

        if not video_url:
            await msg.edit_text("❌ Could not fetch video link")
            return

        keyboard = [
            [
                InlineKeyboardButton(
                    "⬇️ Download Video",
                    url=video_url
                )
            ]
        ]

        await msg.edit_text(
            f"🎬 {title}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    except Exception as e:

        print(e)

        await msg.edit_text("❌ Failed to extract video link")


def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, generate_link)
    )

    print("🚀 Direct Link Downloader Bot Running")

    app.run_polling()


if __name__ == "__main__":
    main()
