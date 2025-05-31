from telegram import Update
from telegram.ext import ContextTypes
from datetime import date

from app.db.crud import get_user_by_telegram_id
from app.db.record_utils import get_latest_record

def calculate_age(birth_date: date) -> int:
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


async def show_user_summary(update: Update, context: ContextTypes.DEFAULT_TYPE, skip_kbju=False):
    telegram_id = update.effective_user.id
    user = get_user_by_telegram_id(telegram_id)
    record = get_latest_record(user.id)

    age = calculate_age(user.date_of_birth) if user.date_of_birth else "—"

    lines = ["<b>📁 Мои данные:</b>"]
    lines.append(f"👤 Имя: <b>{user.name or user.first_name}</b>")
    lines.append(f"🎂 Возраст: <b>{age}</b>")
    lines.append(f"📏 Рост: <b>{user.height} см</b>")
    lines.append(f"⚖️ Вес: <b>{record.weight} кг</b>")

    if record.waist:
        lines.append(f"📉 Талия: <b>{record.waist} см</b>")
    if record.neck:
        lines.append(f"📏 Шея: <b>{record.neck} см</b>")
    if record.hip:
        lines.append(f"🦵 Бёдра: <b>{record.hip} см</b>")
    if record.body_fat:
        lines.append(f"💪 Жир: <b>{record.body_fat}%</b>")

    if record.step_level:
        lines.append(f"🚶 Шаги: <b>Уровень {record.step_level}</b>")
    if record.sport_type and record.sport_type != "нет":
        lines.append(f"💪 Тренировки: <b>{record.sport_type.replace('sport_', '').capitalize()} — {record.sport_freq} р/нед</b>")

    if not skip_kbju and record.calories and record.protein and record.fat and record.carbs:
        lines.append("\n<b>🍽 Твоя дневная норма:</b>")
        lines.append(f"🔥 Калории: <b>{record.calories}</b>")
        lines.append(f"🥩 Белки: <b>{record.protein} г</b>")
        lines.append(f"🧈 Жиры: <b>{record.fat} г</b>")
        lines.append(f"🍞 Углеводы: <b>{record.carbs} г</b>")

    await update.effective_chat.send_message("\n".join(lines), parse_mode="HTML")
