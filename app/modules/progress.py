import os
import matplotlib.pyplot as plt
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
from sqlalchemy import asc
from app.db.session import get_db
from app.db.crud import get_user_by_telegram_id
from app.db.models import UserRecord

def get_all_records_for_user(user_id: int, db: Session) -> list[UserRecord]:
    return (
        db.query(UserRecord)
        .filter(UserRecord.user_id == user_id)
        .order_by(asc(UserRecord.created_at))
        .all()
    )

def describe_period(days: int) -> str:
    if days < 7:
        return f"всего за {days} дней"
    months = days / 30
    if months < 1.5:
        return "всего за 1 месяц"
    elif months < 2.5:
        return "всего за 1.5 месяца"
    elif months < 3.5:
        return "всего за 2 месяца"
    elif months < 6:
        return f"всего за {round(months)} месяца"
    else:
        return f"всего за {round(months)} месяцев"

def smart_progress_message(weight_diff, fat_diff, days):
    if weight_diff < 0 and fat_diff < 0:
        return (
            f"🌟 <b>WOW! Ты большой молодец!</b>\n"
            f"Ты снизил вес на <b>{abs(weight_diff):.1f} кг</b> и жир на <b>{abs(fat_diff):.1f}%</b> — "
            f"{describe_period(days)}! 🔥\n"
            f"Не останавливайся!"
        )
    elif weight_diff < 0 and fat_diff > 0:
        return (
            f"📉 Вес снизился на <b>{abs(weight_diff):.1f} кг</b>! 🔥\n"
            f"Но % жира вырос на <b>{abs(fat_diff):.1f}%</b> — такое бывает.\n"
            f"{describe_period(days).capitalize()} — продолжай 💪"
        )
    elif weight_diff > 0 and fat_diff < 0:
        return (
            f"🎯 Жир снизился на <b>{abs(fat_diff):.1f}%</b>! 🎉\n"
            f"А вес вырос на <b>{abs(weight_diff):.1f} кг</b> — возможно, это мышцы или вода.\n"
            f"{describe_period(days).capitalize()} — супер!"
        )
    elif weight_diff == 0 and fat_diff == 0:
        return f"📊 У тебя стабильный уровень.\n{describe_period(days).capitalize()} — это уже хорошо!"
    else:
        return (
            f"⚠️ Есть небольшой рост веса или жира.\n"
            f"{describe_period(days).capitalize()} — ты уже сделал шаг, не сдавайся!"
        )

async def show_progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = next(get_db())
    user = get_user_by_telegram_id(update.effective_user.id)
    if not user:
        await update.message.reply_text("❌ Пользователь не найден.", parse_mode="HTML")
        return

    records = get_all_records_for_user(user.id, db)
    if not records or len(records) < 2:
        await update.message.reply_text("ℹ️ Недостаточно данных для анализа прогресса.", parse_mode="HTML")
        return

    weight_records = sorted([(r.created_at.date(), r.weight) for r in records if r.weight is not None])
    fat_records = sorted([(r.created_at.date(), r.body_fat) for r in records if r.body_fat is not None])

    if len(weight_records) < 2 or len(fat_records) < 2:
        await update.message.reply_text("📉 Нужно хотя бы 2 записи веса и жира для построения графика.", parse_mode="HTML")
        return

    dates = [d for d, w in weight_records]
    weights = [w for d, w in weight_records]
    weight_diff = weights[-1] - weights[0]
    fat_diff = fat_records[-1][1] - fat_records[0][1]
    days = (dates[-1] - dates[0]).days

    # График
    plt.figure(figsize=(8, 4))
    plt.plot(dates, weights, marker='o', linestyle='-', linewidth=2, label='Вес (кг)')
    plt.title("Прогресс веса")
    plt.xlabel("Дата")
    plt.ylabel("Вес (кг)")
    plt.grid(True)
    plt.tight_layout()

    graph_path = "static/progress_graph.png"
    os.makedirs("static", exist_ok=True)
    plt.savefig(graph_path)
    plt.close()

    text = (
        "📈 <b>Вот как ты продвигаешься:</b>\n\n"
        f"{smart_progress_message(weight_diff, fat_diff, days)}"
    )
    await update.message.reply_text(text, parse_mode="HTML")

    with open(graph_path, "rb") as f:
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=f)
