import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = os.environ["BOT_TOKEN"]

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
text = update.message.text
await update.message.reply_text("Received: " + text)

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT, handle))

print("Bot started")

app.run_polling()
