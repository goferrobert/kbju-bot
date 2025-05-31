from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes, ConversationHandler, MessageHandler, CallbackQueryHandler,
    filters
)
from app.db.crud import get_user_by_telegram_id
from app.db.record_utils import get_or_create_today_record
from app.modules.bodyfat import calculate_body_fat
from app.ui.menu import send_main_menu
from app.db.session import SessionLocal
from datetime import datetime

UPDATE_WEIGHT, UPDATE_ACTIVITY, UPDATE_WAIST, UPDATE_NECK, UPDATE_HIP = range(810, 815)

STEP_MULTIPLIERS = {
    1: 1.2,
    2: 1.35,
    3: 1.5,
    4: 1.65,
    5: 1.8
}

async def start_update_metrics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text(
        "⚖️ <b>Введи свой текущий вес</b> в кг (например: 72.5):",
        parse_mode="HTML"
    )
    return UPDATE_WEIGHT

async def handle_update_weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        weight = float(update.message.text.strip())
        if not 30 <= weight <= 300:
            raise ValueError
        context.user_data["weight"] = weight
    except ValueError:
        await update.message.reply_text("❌ Пожалуйста, введи <b>реалистичный вес</b> от 30 до 300 кг.", parse_mode="HTML")
        return UPDATE_WEIGHT

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("1️⃣", callback_data="activity_1"),
         InlineKeyboardButton("2️⃣", callback_data="activity_2"),
         InlineKeyboardButton("3️⃣", callback_data="activity_3")],
        [InlineKeyboardButton("4️⃣", callback_data="activity_4"),
         InlineKeyboardButton("5️⃣", callback_data="activity_5")]
    ])
    await update.message.reply_text(
        "🏃 <b>Укажи уровень физической активности за последние 7 дней:</b>\n\n"
        "1️⃣ — минимальный\n2️⃣ — лёгкий\n3️⃣ — средний\n4️⃣ — высокий\n5️⃣ — экстремальный\n\n👇 Выбери кнопку:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    return UPDATE_ACTIVITY

async def handle_update_activity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    level = int(query.data.split("_")[1])
    context.user_data["activity"] = STEP_MULTIPLIERS.get(level, 1.2)
    await query.message.reply_text("📏 <b>Введи обхват талии</b> (в см):", parse_mode="HTML")
    return UPDATE_WAIST

async def handle_update_waist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        waist = float(update.message.text.strip())
        if not 30 <= waist <= 200:
            raise ValueError
        context.user_data["waist"] = waist
    except ValueError:
        await update.message.reply_text("❌ Введите <b>корректный обхват талии</b> от 30 до 200 см.", parse_mode="HTML")
        return UPDATE_WAIST
    await update.message.reply_text("📏 <b>Введи обхват шеи</b> (в см):", parse_mode="HTML")
    return UPDATE_NECK

async def handle_update_neck(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        neck = float(update.message.text.strip())
        if not 20 <= neck <= 80:
            raise ValueError
        context.user_data["neck"] = neck
    except ValueError:
        await update.message.reply_text("❌ Введите <b>корректный обхват шеи</b> от 20 до 80 см.", parse_mode="HTML")
        return UPDATE_NECK

    user = get_user_by_telegram_id(update.effective_user.id)
    if user.sex == "женский":
        await update.message.reply_text("📏 <b>Введи обхват бёдер</b> (в см):", parse_mode="HTML")
        return UPDATE_HIP
    return await finalize_update(update, context)

async def handle_update_hip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        hip = float(update.message.text.strip())
        if not 30 <= hip <= 200:
            raise ValueError
        context.user_data["hip"] = hip
    except ValueError:
        await update.message.reply_text("❌ Введите <b>корректный обхват бёдер</b> от 30 до 200 см.", parse_mode="HTML")
        return UPDATE_HIP
    return await finalize_update(update, context)

async def finalize_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    user = get_user_by_telegram_id(telegram_id)

    weight = context.user_data["weight"]
    activity = context.user_data["activity"]
    waist = context.user_data["waist"]
    neck = context.user_data["neck"]
    hip = context.user_data.get("hip")

    body_fat = calculate_body_fat(
        sex=user.sex,
        height=user.height,
        waist=waist,
        neck=neck,
        hip=hip
    )

    db = SessionLocal()
    record = get_or_create_today_record(user.id, db)
    record.weight = weight
    record.activity_level = activity
    record.waist = waist
    record.neck = neck
    if hip:
        record.hip = hip
    record.body_fat = body_fat
    db.commit()
    db.close()

    text = (
        "✅ <b>Данные обновлены!</b>\n\n"
        f"Процент жира: <b>{round(body_fat, 1)}%</b>\n"
        f"Вес: <b>{weight} кг</b>\n"
        f"Активность: <b>{activity}</b>\n"
    )
    await update.effective_chat.send_message(text, parse_mode="HTML")
    await send_main_menu(update, context)
    return ConversationHandler.END

update_metrics_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_update_metrics, pattern="^update_metrics$")],
    states={
        UPDATE_WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_update_weight)],
        UPDATE_ACTIVITY: [CallbackQueryHandler(handle_update_activity, pattern=r"^activity_\d")],
        UPDATE_WAIST: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_update_waist)],
        UPDATE_NECK: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_update_neck)],
        UPDATE_HIP: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_update_hip)],
    },
    fallbacks=[]
)
