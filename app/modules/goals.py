from telegram import Update
from telegram.ext import ContextTypes
from datetime import date

from app.modules.kbju import calculate_kbju


def calculate_age(birth_date: date) -> int:
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


async def show_goal_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE, user, record):
    bf = record.body_fat
    bmi = record.weight / ((user.height / 100) ** 2)

    if bf >= 25:
        goal_type = "fat_loss"
        text = (
            f"📉 У тебя повышенный уровень жира — <b>{bf}%</b>.\n"
            "Это говорит о лишней массе, которая может мешать здоровью и активности.\n\n"
            "🎯 <b>Рекомендуемая цель:</b> снижение жира 🔥"
        )
    elif bf <= 12:
        goal_type = "mass_gain"
        text = (
            f"💪 У тебя низкий процент жира — <b>{bf}%</b>. Отличный результат!\n"
            "Если хочешь нарастить мышцы — это отличный момент.\n\n"
            "🎯 <b>Рекомендуемая цель:</b> набор массы 📈"
        )
    else:
        goal_type = "recomposition"
        text = (
            f"⚖️ Процент жира — <b>{bf}%</b>. Очень сбалансировано!\n"
            "Можно одновременно снижать жир и укреплять мышечную массу.\n\n"
            "🎯 <b>Рекомендуемая цель:</b> рекомпозиция тела 🧬"
        )

    context.user_data["goal_type"] = goal_type
    await update.effective_chat.send_message(text, parse_mode="HTML")


async def show_goal_kbju(update: Update, context: ContextTypes.DEFAULT_TYPE, user, record):
    goal = context.user_data.get("goal_type", "fat_loss")
    kbju = calculate_kbju(user, record, goal=goal)

    text = (
        "\n\n<b>📌 КБЖУ для достижения цели:</b>\n"
        f"🔥 Калории: <b>{kbju['calories']}</b>\n"
        f"🥩 Белки: <b>{kbju['protein']} г</b>\n"
        f"🧈 Жиры: <b>{kbju['fat']} г</b>\n"
        f"🍞 Углеводы: <b>{kbju['carbs']} г</b>"
    )

    await update.effective_chat.send_message(text, parse_mode="HTML")
