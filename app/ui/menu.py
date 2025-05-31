from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from app.ui.keyboards import main_menu_keyboard
from app.modules.preferences import start_preferences

async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📋 <b>Главное меню</b>\n\n"
        "Выберите действие ниже ⬇️"
    )
    if update.message:
        await update.message.reply_text(text, reply_markup=main_menu_keyboard, parse_mode="HTML")
    elif update.callback_query:
        await update.callback_query.message.edit_text(text, reply_markup=main_menu_keyboard, parse_mode="HTML")

def menu_callback_handler():
    return CallbackQueryHandler(callback=start_preferences, pattern="^preferences$")
