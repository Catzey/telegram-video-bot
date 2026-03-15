import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text("Bot working!")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.ALL, reply))

print("Bot started")

app.run_polling()
