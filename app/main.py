from fastapi import FastAPI
from telegram import Bot, Update
from telegram.ext import (
    Application, ApplicationBuilder,
    CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, ContextTypes, filters
)

from core.env import IS_PROD, BOT_TOKEN, WEBHOOK_SECRET
from app.db.session import init_db

from app.modules.user import user_flow_handler
from app.modules.kbju import kbju_handler
from app.modules.bodyfat import bodyfat_handler
from app.modules.first_touch import first_touch_handler
from app.modules.update_metrics import update_metrics_handler
from app.modules.preferences import preferences_handler

from app.modules.progress import show_progress
from app.ui.menu import menu_callback_handler
from app.ui.menu import send_main_menu

# === Инициализация Telegram Bot + FastAPI ===
bot = Bot(token=BOT_TOKEN)
app = FastAPI()
application: Application = ApplicationBuilder().token(BOT_TOKEN).build()

# === Регистрация хендлеров ===
application.add_handler(first_touch_handler)
application.add_handler(user_flow_handler)
application.add_handler(kbju_handler)
application.add_handler(bodyfat_handler)
application.add_handler(update_metrics_handler)
application.add_handler(preferences_handler())

application.add_handler(CommandHandler("menu", send_main_menu))
application.add_handler(CommandHandler("progress", show_progress))
application.add_handler(menu_callback_handler())

# === Webhook режим (продакшн) ===
if IS_PROD:
    @app.post(f"/webhook/{WEBHOOK_SECRET}")
    async def telegram_webhook(update: dict):
        await application.update_queue.put(Update.de_json(update, application.bot))
        return {"status": "ok"}

    @app.on_event("startup")
    async def on_startup():
        await application.initialize()
        await application.start()
        webhook_url = f"https://your-domain.com/webhook/{WEBHOOK_SECRET}"
        await application.bot.set_webhook(url=webhook_url)
        print(f"✅ Webhook установлен: {webhook_url}")

    @app.on_event("shutdown")
    async def on_shutdown():
        await application.stop()

# === Polling режим (локальная отладка) ===
if not IS_PROD:
    if __name__ == "__main__":
        init_db()
        application.run_polling()
