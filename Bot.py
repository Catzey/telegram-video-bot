import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
msg = update.message.text
await update.message.reply_text("Received: " + msg)

async def main():
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT, handle))
print("Bot started")
await app.run_polling()

if **name** == "**main**":
import asyncio
asyncio.run(main())
