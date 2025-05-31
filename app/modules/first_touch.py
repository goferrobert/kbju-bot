from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes, ConversationHandler, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters
)
from datetime import datetime

from app.db.crud import get_user_by_telegram_id, create_user
from app.db.record_utils import get_or_create_today_record
from app.modules.kbju import calculate_kbju
from app.modules.bodyfat import NECK, handle_neck
from app.modules.my_data import show_user_summary
from app.modules.invite import send_consultation_invite
from app.db.session import SessionLocal

# Константы состояний анкеты пользователя (дублируем напрямую, чтобы избежать циклического импорта)
BASIC_NAME, BASIC_BIRTHDAY, BASIC_HEIGHT, BASIC_SEX = range(100, 104)
FIRST_TOUCH_WEIGHT, STEP_COUNT, SPORT_YN, SPORT_TYPE, SPORT_FREQ, FIRST_TOUCH_WAIST = range(900, 906)
GOAL_SELECT = 913

async def start_first_touch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    user = get_user_by_telegram_id(telegram_id)

    if user:
        await update.message.reply_text("⚠️ <b>Ты уже зарегистрирован.</b> Напиши /menu, чтобы продолжить.", parse_mode="HTML")
        return ConversationHandler.END

    context.user_data["flow"] = "first_touch"
    await update.message.reply_text(
        "👋 <b>Привет!</b> Сейчас мы пройдём анкету. Это займёт не больше 1 минуты!",
        parse_mode="HTML"
    )
    await update.message.reply_text("👋 Давай начнём с основного.\nКак тебя зовут? (ФИО или просто имя)", parse_mode="HTML")
    return BASIC_NAME

async def after_form_finished(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message or update.callback_query.message
    telegram_id = update.effective_user.id
 
  # Импортировать: from app.db.crud import create_user
 
    name = context.user_data["name"]
    birthday = context.user_data["birthday"]
    height = context.user_data["height"]
    sex = context.user_data["sex"]

    user = create_user(telegram_id, name, birthday, height, sex)
    context.user_data["user"] = user

    await message.reply_text("⚖️ <b>Введи свой вес</b> в кг (например: 72.5):", parse_mode="HTML")
    return FIRST_TOUCH_WEIGHT

async def handle_first_touch_weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        weight = float(update.message.text.strip())
        if not 30 <= weight <= 300:
            raise ValueError
        context.user_data["weight"] = weight
    except ValueError:
        await update.message.reply_text("❌ Введите <b>реалистичный вес</b> от 30 до 300 кг.", parse_mode="HTML")
        return FIRST_TOUCH_WEIGHT

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🚶 0–3000", callback_data="steps_1"),
         InlineKeyboardButton("🚶‍♂️ 3000–7000", callback_data="steps_2")],
        [InlineKeyboardButton("🚶‍♀️ 7000–10000", callback_data="steps_3"),
         InlineKeyboardButton("🏃 10000–15000", callback_data="steps_4")],
        [InlineKeyboardButton("🏃‍♂️ 15000+", callback_data="steps_5")]
    ])
    msg = update.message or update.callback_query.message
    await msg.reply_text(
        "📍 <b>Сколько шагов вы проходите в день?</b>\n\n👇 Выберите вариант:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    return STEP_COUNT

async def handle_steps_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    level = int(update.callback_query.data.split("_")[1])
    step_multiplier = {1: 1.2, 2: 1.3, 3: 1.4, 4: 1.5, 5: 1.6}.get(level, 1.3)
    context.user_data["step_level"] = level
    context.user_data["step_multiplier"] = step_multiplier
    await update.callback_query.message.reply_text(
        "🏋️ <b>Занимаетесь ли вы спортом?</b>",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Да", callback_data="sport_yes"),
             InlineKeyboardButton("❌ Нет", callback_data="sport_no")]
        ]),
        parse_mode="HTML"
    )
    return SPORT_YN

async def handle_sport_yn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    if update.callback_query.data == "sport_no":
        context.user_data["sport_type"] = "нет"
        context.user_data["sport_freq"] = 0
        context.user_data["sport_multiplier"] = 1.0
        return await ask_waist(update, context)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🧘 Йога / Пилатес", callback_data="sport_yoga")],
        [InlineKeyboardButton("🏃 Бег / Кардио", callback_data="sport_cardio")],
        [InlineKeyboardButton("🏋️ Фитнес / Зал", callback_data="sport_fitness")],
        [InlineKeyboardButton("🥵 Кроссфит / HIIT", callback_data="sport_hiit")]
    ])
    await update.callback_query.message.reply_text(
        "💪 <b>Какие тренировки вы выполняете?</b>",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    return SPORT_TYPE

async def handle_sport_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    type_map = {
        "sport_yoga": 1.05,
        "sport_cardio": 1.10,
        "sport_fitness": 1.20,
        "sport_hiit": 1.30
    }
    context.user_data["sport_type"] = update.callback_query.data
    context.user_data["sport_multiplier"] = type_map[update.callback_query.data]
    await update.callback_query.message.reply_text("📅 <b>Сколько раз в неделю вы тренируетесь?</b> (1–7)", parse_mode="HTML")
    return SPORT_FREQ

async def handle_sport_freq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        freq = int(update.message.text.strip())
        if not 1 <= freq <= 7:
            raise ValueError
        freq_scale = freq / 7.0
        context.user_data["sport_freq"] = freq
        context.user_data["sport_multiplier"] *= freq_scale
    except ValueError:
        await update.message.reply_text("❌ Введите <b>целое число</b> от 1 до 7.", parse_mode="HTML")
        return SPORT_FREQ

    return await ask_waist(update, context)

async def ask_waist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📏 <b>Введи обхват талии</b> (в см):", parse_mode="HTML")
    return FIRST_TOUCH_WAIST

async def handle_first_touch_waist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        waist = float(update.message.text.strip())
        if not 30 <= waist <= 200:
            raise ValueError
    except ValueError:
        await update.message.reply_text("❌ Введите <b>корректный обхват талии</b> от 30 до 200 см.", parse_mode="HTML")
        return FIRST_TOUCH_WAIST

    telegram_id = update.effective_user.id
    user = context.user_data.get("user") or get_user_by_telegram_id(telegram_id)
    weight = context.user_data.get("weight")
    step = context.user_data.get("step_multiplier", 1.3)
    sport = context.user_data.get("sport_multiplier", 1.0)
    activity = round(step * sport, 2)

    step_level = context.user_data.get("step_level")
    sport_type = context.user_data.get("sport_type")
    sport_freq = context.user_data.get("sport_freq")

    db = SessionLocal()
    record = get_or_create_today_record(user.id, db)
    record.weight = weight
    record.activity_level = activity
    record.waist = waist
    record.step_level = step_level
    record.sport_type = sport_type
    record.sport_freq = sport_freq
    db.commit()
    db.close()

    context.user_data["bodyfat"] = {
        "sex": user.sex,
        "height": user.height,
        "waist": waist
    }
    await update.message.reply_text("📏 <b>Введи обхват шеи</b> (в см):", parse_mode="HTML")
    return NECK

# === BASIC INFO HANDLERS ===

async def handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["name"] = update.message.text.strip()
    await update.message.reply_text("📅 Введи дату рождения (дд.мм.гггг):")
    return BASIC_BIRTHDAY

async def handle_birthday(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["birthday"] = update.message.text.strip()
    await update.message.reply_text("📏 Введи свой рост в см:")
    return BASIC_HEIGHT

async def handle_height(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["height"] = update.message.text.strip()
    await update.message.reply_text("👨 Укажи пол (Мужчина / Женщина):")
    return BASIC_SEX

async def handle_sex(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["sex"] = update.message.text.strip().lower()
    return await after_form_finished(update, context)



first_touch_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start_first_touch)],
    states={
        BASIC_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_name)],
        BASIC_BIRTHDAY: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_birthday)],
        BASIC_HEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_height)],
        BASIC_SEX: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_sex)],
        FIRST_TOUCH_WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_first_touch_weight)],
        STEP_COUNT: [CallbackQueryHandler(handle_steps_selection)],
        SPORT_YN: [CallbackQueryHandler(handle_sport_yn)],
        SPORT_TYPE: [CallbackQueryHandler(handle_sport_type)],
        SPORT_FREQ: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_sport_freq)],
        FIRST_TOUCH_WAIST: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_first_touch_waist)],
        NECK: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_neck)],
    },
    fallbacks=[],
    per_user=True,
    per_chat=True,
    per_message=False,
)

