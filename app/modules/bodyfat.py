from telegram import Update
from telegram.ext import (
    ContextTypes, ConversationHandler,
    CallbackQueryHandler, MessageHandler, filters
)
from datetime import datetime
from math import log10

from app.db.crud import get_user_by_telegram_id
from app.db.record_utils import get_or_create_today_record
from app.ui.menu import send_main_menu
from app.db.session import SessionLocal

from app.modules.kbju import calculate_kbju
from app.modules.my_data import show_user_summary
from app.modules.invite import send_consultation_invite
from app.modules.goals import show_goal_analysis, show_goal_kbju

WAIST, NECK, HIPS = range(10, 13)

async def start_body_fat_calc(update: Update, context: ContextTypes.DEFAULT_TYPE, user_data=None):
    if user_data is None:
        telegram_id = update.effective_user.id
        user = get_user_by_telegram_id(telegram_id)
        if not user or not user.sex or not user.height:
            await update.message.reply_text("❌ <b>Сначала пройди анкету</b> с помощью команды /start.", parse_mode="HTML")
            return ConversationHandler.END
        user_data = {"sex": user.sex, "height": user.height}

    context.user_data["bodyfat"] = user_data
    await update.effective_chat.send_message("📏 <b>Введи обхват талии</b> (в см):", parse_mode="HTML")
    return WAIST

async def handle_waist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        waist = float(update.message.text.strip())
        if not 30 <= waist <= 200:
            raise ValueError
    except ValueError:
        await update.message.reply_text("❌ Введи число от 30 до 200 см.", parse_mode="HTML")
        return WAIST

    context.user_data["bodyfat"]["waist"] = waist
    await update.message.reply_text("📏 <b>Введи обхват шеи</b> (в см):", parse_mode="HTML")
    return NECK

async def handle_neck(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        neck = float(update.message.text.strip())
        if not 20 <= neck <= 100:
            raise ValueError
    except ValueError:
        await update.message.reply_text("❌ Введи число от 20 до 100 см.", parse_mode="HTML")
        return NECK

    context.user_data["bodyfat"]["neck"] = neck

    if context.user_data["bodyfat"].get("sex") == "женский":
        await update.message.reply_text("📏 <b>Введи обхват бёдер</b> (в см):", parse_mode="HTML")
        return HIPS

    return await calculate_body_fat(update, context)

async def handle_hips(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        hips = float(update.message.text.strip())
        if not 30 <= hips <= 200:
            raise ValueError
    except ValueError:
        await update.message.reply_text("❌ Введи число от 30 до 200 см.", parse_mode="HTML")
        return HIPS

    context.user_data["bodyfat"]["hips"] = hips
    return await calculate_body_fat(update, context)

def calculate_body_fat_percentage(sex: str, height: float, waist: float, neck: float, hips: float = None) -> float:
    if sex == "мужской":
        bodyfat = 495 / (1.0324 - 0.19077 * log10(waist - neck) + 0.15456 * log10(height)) - 450
    else:
        bodyfat = 495 / (1.29579 - 0.35004 * log10(waist + hips - neck) + 0.22100 * log10(height)) - 450
    return round(max(bodyfat, 0), 2)

async def calculate_body_fat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = context.user_data["bodyfat"]
    sex = data["sex"]
    height = data["height"]
    waist = data["waist"]
    neck = data["neck"]
    hips = data.get("hips")

    bodyfat = calculate_body_fat_percentage(sex, height, waist, neck, hips)

    telegram_id = update.effective_user.id
    user = get_user_by_telegram_id(telegram_id)
    dbsession = SessionLocal()
    record = get_or_create_today_record(user.id, db=dbsession)
    record.body_fat = bodyfat
    record.waist = waist
    record.neck = neck
    if hips is not None:
        record.hip = hips

    # расчёт КБЖУ и сохранение
    kbju = calculate_kbju(user, record)
    record.calories = kbju["calories"]
    record.protein = kbju["protein"]
    record.fat = kbju["fat"]
    record.carbs = kbju["carbs"]

    dbsession.commit()
    dbsession.close()

    # показываем мои данные без КБЖУ
    await show_user_summary(update, context, skip_kbju=True)
    await show_goal_analysis(update, context, user, record)
    await show_goal_kbju(update, context, user, record)
    await send_consultation_invite(update, context)

    return ConversationHandler.END

bodyfat_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_body_fat_calc, pattern="^measure_fat$")],
    states={
        WAIST: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_waist)],
        NECK: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_neck)],
        HIPS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_hips)],
    },
    fallbacks=[]
)
