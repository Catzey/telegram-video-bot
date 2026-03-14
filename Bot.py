import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
await update.message.reply_text("Bot is working!")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.ALL, handle))

print("Bot started")
app.run_polling()
