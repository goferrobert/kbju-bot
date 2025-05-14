import os
from fastapi import FastAPI, Request
from telegram import Update, Bot
from telegram.ext import Application, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, ConversationHandler, filters

from handlers.user_flow import (
    start, get_gender, get_weight, get_height, get_age,
    get_activity, get_target,
    GENDER, WEIGHT, HEIGHT, AGE, ACTIVITY, TARGET
)
from funnel.invite import send_consultation_invite

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET") or "secret"

bot = Bot(token=TOKEN)
app = FastAPI()

application: Application = ApplicationBuilder().token(TOKEN).build()

# Conversation logic
conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_gender)],
        WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_weight)],
        HEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_height)],
        AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
        ACTIVITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_activity)],
        TARGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_target)],
    },
    fallbacks=[],
    allow_reentry=True
)

application.add_handler(conv_handler)

# Webhook endpoint
@app.post(f"/webhook/{WEBHOOK_SECRET}")
async def
