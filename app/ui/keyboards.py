from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import CallbackQueryHandler, ContextTypes
from app.modules.preferences import start_preferences

main_menu_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔄 Ввести новые параметры", callback_data="update_metrics")],
    [InlineKeyboardButton("👤 Мои данные", callback_data="my_data")],
    [InlineKeyboardButton("📈 Прогресс", callback_data="progress")],
    [InlineKeyboardButton("🍽 Предпочтения в питании", callback_data="preferences")],
    [InlineKeyboardButton("💬 Написать мне", url="https://t.me/dryuzefovna")],
])

def menu_callback_handler():
    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        data = query.data

        if data == "update_metrics":
            from app.modules.update_metrics import start_update_metrics
            await start_update_metrics(update, context)

        elif data == "my_data":
            from app.modules.my_data import show_user_summary
            await show_user_summary(update, context)

        elif data == "progress":
            from app.modules.progress import show_progress
            await show_progress(update, context)

        elif data == "preferences":
            await start_preferences(update, context)

    return CallbackQueryHandler(handler)