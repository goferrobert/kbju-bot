from telegram import Update, InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import asyncio

# === Основной вызов после завершения анкеты и расчёта целей ===

async def send_consultation_invite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message or update.callback_query.message

    # Ждём 60 секунд перед мотивационной воронкой
    await asyncio.sleep(60)

    # 📸 Фото — заглушка (можно заменить на upload URL или file_id)
    await message.reply_photo(
        photo="https://i.imgur.com/vyF6xNf.jpeg",
        caption="🔥 Пора сделать первый шаг к себе лучшему!"
    )

    # 📝 Мотивация + кнопка
    text = (
        "💡 <b>Ты можешь добиться своей цели</b> — с поддержкой, заботой и персональным планом.\n\n"
        "Готов двигаться вперёд вместе?"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 Записаться на консультацию", callback_data="invite_signup")]
    ])

    await message.reply_text(text, reply_markup=keyboard, parse_mode="HTML")
