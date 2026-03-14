import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = os.environ["BOT_TOKEN"]

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
url = update.message.text

```
await update.message.reply_text("Downloading...")

ydl_opts = {
    "format": "best",
    "outtmpl": "/tmp/video.%(ext)s"
}

try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        file_path = ydl.prepare_filename(info)

    with open(file_path, "rb") as video:
        await update.message.reply_document(document=video)

    os.remove(file_path)

except Exception as e:
    await update.message.reply_text(f"Error: {e}")
```

def main():
app = ApplicationBuilder().token(TOKEN).build()

```
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

print("Bot started")

app.run_polling()
```

if **name** == "**main**":
main()
