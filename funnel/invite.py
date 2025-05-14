from telegram.constants import ParseMode
from telegram import Update
from telegram.ext import ContextTypes
from datetime import timedelta

PHOTO_PATH = "data/1.jpg"
TELEGRAM_USERNAME = "@dryuzefovna"
LINK = f"https://t.me/{TELEGRAM_USERNAME.lstrip('@')}"

async def send_consultation_invite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    # 1. Фото
    with open(PHOTO_PATH, "rb") as photo:
        await context.bot.send_photo(chat_id=chat_id, photo=photo)

    # 2. Сообщение с приглашением
    text = (
        "📩 Хочешь разобраться с питанием, РПП и отношением к телу?\n\n"
        f"Запишись на консультацию — я помогу тебе понять причины трудностей, "
        f"восстановить контакт с телом и выстроить питание без стресса.\n\n"
        f"Напиши 👉 [{TELEGRAM_USERNAME}]({LINK})"
    )
    await context.bot.send_message(chat_id=chat_id, text=text, parse_mode=ParseMode.MARKDOWN)

    # 3. Планируем напоминания
    schedule_reminders(context, chat_id)

def schedule_reminders(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    intervals = [
        ("⏳ Привет! Напоминаю, что ты можешь записаться на консультацию.\n\n" +
         f"Пиши 👉 [{TELEGRAM_USERNAME}]({LINK})", timedelta(hours=2)),

        ("📌 Эй! Ты ещё не записалась — а ведь это может сильно изменить твоё отношение к себе.\n" +
         f"Напиши 👉 [{TELEGRAM_USERNAME}]({LINK})", timedelta(hours=24)),

        ("🕊 Напоминаю в последний раз — можно начать путь к телу и спокойному питанию прямо сейчас.\n\n" +
         f"Пиши 👉 [{TELEGRAM_USERNAME}]({LINK})", timedelta(days=7)),
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
    await context.bot.send_message(
        chat_id=job_data["chat_id"],
        text=job_data["text"],
        parse_mode=ParseMode.MARKDOWN
    )
