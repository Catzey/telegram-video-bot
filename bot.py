import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = os.environ["BOT_TOKEN"]

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
text = update.message.text
await update.message.reply_text(f"You said: {text}")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

print("Bot started")

app.run_polling()
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = os.environ["BOT_TOKEN"]

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
await update.message.reply_text("Bot working!")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.ALL, reply))

print("Bot started")

app.run_polling()
