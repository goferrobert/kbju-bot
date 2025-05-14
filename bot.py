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
async def telegram_webhook(update: dict):
    await application.update_queue.put(Update.de_json(update, application.bot))
    return {"status": "ok"}

# Запуск Telegram Application при старте FastAPI
@app.on_event("startup")
async def on_startup():
    await application.initialize()
    await application.start()
  # Устанавливаем Webhook при старте
    webhook_url = f"https://telegram-patient-rain-1293.fly.dev/webhook/{WEBHOOK_SECRET}"
    await application.bot.set_webhook(url=webhook_url)
    print(f"✅ Webhook установлен: {webhook_url}")

# Остановка Telegram Application при выключении FastAPI
@app.on_event("shutdown")
async def on_shutdown():
    await application.stop()