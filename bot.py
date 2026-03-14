import os
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = os.environ["BOT_TOKEN"]

user_links = {}
formats_cache = {}

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
url = update.message.text
chat_id = update.message.chat_id

```
user_links[chat_id] = url

await update.message.reply_text("🔍 Fetching available formats...")

ydl_opts = {
    "quiet": True,
    "noplaylist": True,
    "http_headers": {
        "User-Agent": "Mozilla/5.0"
    }
}

try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    formats = info.get("formats", [])

    buttons = []
    formats_cache[chat_id] = {}

    for f in formats:
        height = f.get("height")
        if height and height not in formats_cache[chat_id]:
            formats_cache[chat_id][height] = f["format_id"]
            buttons.append([InlineKeyboardButton(f"{height}p", callback_data=str(height))])

    buttons.append([InlineKeyboardButton("MP3", callback_data="mp3")])

    await update.message.reply_text(
        "🎬 Choose download quality:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

except Exception:
    await update.message.reply_text("❌ Could not read video formats.")
```

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
query = update.callback_query
await query.answer()

```
chat_id = query.message.chat_id
choice = query.data
url = user_links.get(chat_id)

await query.edit_message_text("⬇️ Downloading...")

try:

    if choice == "mp3":
        ydl_opts = {
            "format": "bestaudio",
            "outtmpl": "/tmp/audio.%(ext)s"
        }
    else:
        format_id = formats_cache[chat_id].get(int(choice))
        ydl_opts = {
            "format": format_id,
            "outtmpl": "/tmp/video.%(ext)s"
        }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        file = ydl.prepare_filename(info)

    with open(file, "rb") as f:
        await query.message.reply_document(document=f)

    os.remove(file)

except Exception:
    await query.message.reply_text("❌ Download failed.")
```

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
app.add_handler(CallbackQueryHandler(button))

print("Bot started")

app.run_polling()
