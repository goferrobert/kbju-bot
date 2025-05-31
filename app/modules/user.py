# 📦 Модуль: modules/user.py
# Отвечает за анкету пользователя и повторное редактирование через /edit

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes, ConversationHandler, MessageHandler,
    CommandHandler, CallbackQueryHandler, filters
)
from datetime import datetime
from app.db.crud import get_user_by_telegram_id, create_user, update_user
from app.ui.keyboards import menu_callback_handler
from app.modules.first_touch import after_form_finished

# Состояния анкеты
BASIC_NAME, BASIC_BIRTHDAY, BASIC_HEIGHT, BASIC_SEX = range(100, 104)

# Точка входа: первый вход в бота
async def handle_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    user = get_user_by_telegram_id(telegram_id)

    if user is None:
        context.user_data["flow"] = "first_touch"
        return await start_user_form(update, context)

    if not context.user_data.get("skip_registered_message"):
        await update.message.reply_text("🎉 Поздравляем, ты уже зарегистрирован!")
    from app.ui.menu import send_main_menu
    await send_main_menu(update, context)
    return ConversationHandler.END

# /edit — ручной перезапуск анкеты
async def handle_user_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✏️ Повторный запуск анкеты.")
    return await start_user_form(update, context)

# Первый вопрос анкеты — имя
async def start_user_form(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Давай начнём с основного.\nКак тебя зовут? (ФИО или просто имя)",
        parse_mode="HTML"
    )
    return BASIC_NAME

# Обработка имени (ФИО)
async def handle_basic_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    fio = update.message.text.strip().split()
    first_name = fio[0] if len(fio) > 0 else ""
    last_name = " ".join(fio[1:]) if len(fio) > 1 else None
    context.user_data["first_name"] = first_name
    context.user_data["last_name"] = last_name
    context.user_data["name"] = update.message.text.strip()
    await update.message.reply_text("📅 Укажи дату рождения (в формате ДД.ММ.ГГГГ):", parse_mode="HTML")
    return BASIC_BIRTHDAY

# Обработка даты рождения
async def handle_basic_birthday(update: Update, context: ContextTypes.DEFAULT_TYPE):
    date_text = update.message.text.strip()
    try:
        birthday = datetime.strptime(date_text, "%d.%m.%Y").date()
    except ValueError:
        await update.message.reply_text("❌ Неверный формат. Введи дату как ДД.ММ.ГГГГ", parse_mode="HTML")
        return BASIC_BIRTHDAY

    context.user_data["birthday"] = birthday
    await update.message.reply_text("📏 Укажи свой рост (в см):", parse_mode="HTML")
    return BASIC_HEIGHT

# Обработка роста
async def handle_basic_height(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        height = int(update.message.text.strip())
        if not (100 <= height <= 250):
            raise ValueError
    except ValueError:
        await update.message.reply_text("❌ Введи число в сантиметрах (от 100 до 250)", parse_mode="HTML")
        return BASIC_HEIGHT

    context.user_data["height"] = height
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("мужской", callback_data="sex_мужской")],
        [InlineKeyboardButton("женский", callback_data="sex_женский")]
    ])
    await update.message.reply_text("🚻 Укажи пол:", reply_markup=keyboard)
    return BASIC_SEX

# Обработка выбора пола через callback
async def handle_basic_sex_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    sex = query.data.split("_")[1]

    if sex not in ["мужской", "женский"]:
        await query.message.reply_text("❌ Выбери из предложенных вариантов: мужской или женский")
        return BASIC_SEX

    context.user_data["sex"] = sex
    telegram_user = update.effective_user

    existing_user = get_user_by_telegram_id(telegram_user.id)
    if existing_user:
        update_user(
            telegram_user.id,
            telegram_user.username,
            context.user_data.get("first_name", ""),
            context.user_data.get("last_name", None),
            context.user_data.get("name", telegram_user.full_name),
            sex,
            context.user_data["birthday"],
            context.user_data["height"]
        )
        await query.message.edit_text("✅ Данные обновлены!", parse_mode="HTML")
    else:
        create_user(
            telegram_id=telegram_user.id,
            username=telegram_user.username,
            first_name=context.user_data.get("first_name", ""),
            last_name=context.user_data.get("last_name", None),
            name=context.user_data.get("name", telegram_user.full_name),
            sex=sex,
            date_of_birth=context.user_data["birthday"],
            height=context.user_data["height"]
        )
        await query.message.edit_text("✅ Анкета сохранена!", parse_mode="HTML")

    if context.user_data.get("flow") == "first_touch":
        await after_form_finished(update, context)
        return ConversationHandler.END


    from app.ui.menu import send_main_menu
    await send_main_menu(update, context)
    return ConversationHandler.END

# === ConversationHandler для анкеты ===
user_flow_handler = ConversationHandler(
    entry_points=[
        CommandHandler("start", handle_user_start),
        CommandHandler("edit", handle_user_edit),
    ],
    states={
        BASIC_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_basic_name)],
        BASIC_BIRTHDAY: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_basic_birthday)],
        BASIC_HEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_basic_height)],
        BASIC_SEX: [CallbackQueryHandler(handle_basic_sex_callback, pattern=r"^sex_")],
    },
    fallbacks=[],
)

menu_handler = menu_callback_handler()
