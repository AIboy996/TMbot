from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
import os
TOKEN=os.getenv('token')

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = '你好~我是一个python-telegram-bot'
    await context.bot.send_message(chat_id=update.effective_chat.id,text=text)

start_handler = CommandHandler('hello', hello)

application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(start_handler)
application.run_polling()