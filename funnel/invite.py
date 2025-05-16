# invite.py — отправка приглашения и напоминаний с кнопкой

from telegram.constants import ParseMode
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from datetime import timedelta
import asyncio


PHOTO_PATH = "data/1.jpg"
TELEGRAM_USERNAME = "@dryuzefovna"
LINK = f"https://t.me/{TELEGRAM_USERNAME.lstrip('@')}"

async def send_consultation_invite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    await asyncio.sleep(2 * 60)


    # 1. Фото
    with open(PHOTO_PATH, "rb") as photo:
        await context.bot.send_photo(chat_id=chat_id, photo=photo)

    # 2. Сообщение с текстом
    text = (
        "📩 Хочешь разобраться с питанием, РПП и отношением к телу?\n\n"
        "Запишись на консультацию — я помогу тебе понять причины трудностей, "
        "восстановить контакт с телом и выстроить питание без стресса."
    )
    await context.bot.send_message(chat_id=chat_id, text=text)

    # 3. Кнопка с приглашением
    invite_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 Записаться на консультацию", url=LINK)]
    ])

    await context.bot.send_message(
        chat_id=chat_id,
        text="👇 Нажми на кнопку, чтобы записаться:",
        reply_markup=invite_keyboard
    )

    # 4. Планируем напоминания
    schedule_reminders(context, chat_id)

def schedule_reminders(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    intervals = [
        ("⏳ Привет! Напоминаю, что ты можешь записаться на консультацию.", timedelta(hours=2)),
        ("📌 Эй! Ты ещё не записалась — а ведь это может изменить твоё отношение к себе.", timedelta(hours=24)),
        ("🕊 Напоминаю в последний раз — можно начать путь к телу и спокойному питанию прямо сейчас.", timedelta(days=7)),
    ]

    for message_text, when in intervals:
        context.job_queue.run_once(
            reminder_callback,
            when,
            data={"chat_id": chat_id, "text": message_text},
            name=f"reminder_{chat_id}_{when}"
        )

async def reminder_callback(context: ContextTypes.DEFAULT_TYPE):
    job_data = context.job.data
    chat_id = job_data["chat_id"]
    text = job_data["text"]

    invite_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 Записаться на консультацию", url=LINK)]
    ])

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"{text}\n\n👇 Нажми на кнопку, чтобы записаться:",
        reply_markup=invite_keyboard
    )
