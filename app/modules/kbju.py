from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler
from app.db.crud import get_user_by_telegram_id
from app.db.record_utils import get_or_create_today_record
from app.db.session import SessionLocal

# Состояния для ручного выбора цели
GOAL_SELECT = 913


def calculate_kbju(user, record, goal: str = None):
    weight = record.weight
    height = user.height
    age = (record.created_at.year - user.date_of_birth.year)
    sex = user.sex
    activity = record.activity_level or 1.3

    if sex == "мужской":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    calories = bmr * activity

    # Корректировка по цели
    if goal == "fat_loss":
        calories *= 0.85
    elif goal == "mass_gain":
        calories *= 1.10
    elif goal == "recomposition":
        calories *= 0.95

    protein = 2.0 * weight
    fat = 1.0 * weight

    kcal_from_protein = protein * 4
    kcal_from_fat = fat * 9
    remaining_kcal = calories - (kcal_from_protein + kcal_from_fat)
    carbs = max(0, remaining_kcal / 4)

    return {
        "calories": round(calories),
        "protein": round(protein),
        "fat": round(fat),
        "carbs": round(carbs)
    }


async def handle_kbju_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔥 Снижение жира", callback_data="goal_fat_loss")],
        [InlineKeyboardButton("📈 Набор массы", callback_data="goal_mass_gain")],
        [InlineKeyboardButton("⚖️ Рекомпозиция", callback_data="goal_recomposition")]
    ])
    await update.message.reply_text("🎯 <b>Выбери свою цель:</b>", reply_markup=keyboard, parse_mode="HTML")
    return GOAL_SELECT


async def handle_kbju_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    goal = update.callback_query.data.replace("goal_", "")

    telegram_id = update.effective_user.id
    user = get_user_by_telegram_id(telegram_id)
    db = SessionLocal()
    record = get_or_create_today_record(user.id, db)

    kbju = calculate_kbju(user, record, goal)
    record.calories = kbju["calories"]
    record.protein = kbju["protein"]
    record.fat = kbju["fat"]
    record.carbs = kbju["carbs"]
    record.goal_type = goal

    db.commit()
    db.close()

    await update.callback_query.message.reply_text(
        f"<b>📌 КБЖУ для цели '{goal.replace('_', ' ')}':</b>\n"
        f"🔥 Калории: <b>{kbju['calories']}</b>\n"
        f"🥩 Белки: <b>{kbju['protein']} г</b>\n"
        f"🧈 Жиры: <b>{kbju['fat']} г</b>\n"
        f"🍞 Углеводы: <b>{kbju['carbs']} г</b>",
        parse_mode="HTML"
    )
    return ConversationHandler.END


kbju_handler = ConversationHandler(
    entry_points=[],  # Подключи в main: CommandHandler("kbju", handle_kbju_command)
    states={
        GOAL_SELECT: [CallbackQueryHandler(handle_kbju_goal, pattern="^goal_")],
    },
    fallbacks=[]
)
