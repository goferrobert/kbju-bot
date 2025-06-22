from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import asyncio

from app.handlers.base import BaseHandler
from app.utils.validation import ValidationError
from app.utils.logger import get_logger

logger = get_logger(__name__)

class InviteHandler(BaseHandler):
    """Handler for consultation invites."""

    # Константы
    INVITE_DELAY = 60  # Задержка перед отправкой приглашения в секундах
    INVITE_PHOTO_URL = "https://i.imgur.com/vyF6xNf.jpeg"
    
    # Тексты сообщений
    MESSAGES = {
        "photo_caption": "🔥 Пора сделать первый шаг к себе лучшему!",
        "invite_text": (
            "💡 <b>Ты можешь добиться своей цели</b> — с поддержкой, заботой и персональным планом.\n\n"
            "Готов двигаться вперёд вместе?"
        ),
        "button_text": "📝 Записаться на консультацию"
    }

    @BaseHandler.handle_errors
    async def send_consultation_invite(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Отправка приглашения на консультацию после завершения анкеты.
        
        Args:
            update: Объект обновления Telegram
            context: Контекст бота
        """
        message = update.message or update.callback_query.message
        if not message:
            raise ValidationError("Не удалось получить сообщение")

        # Ждём перед мотивационной воронкой
        await asyncio.sleep(self.INVITE_DELAY)

        # Отправляем фото
        try:
            await message.reply_photo(
                photo=self.INVITE_PHOTO_URL,
                caption=self.MESSAGES["photo_caption"]
            )
        except Exception as e:
            logger.error(f"Error sending invite photo: {str(e)}", exc_info=True)
            # Продолжаем выполнение даже если фото не отправилось

        # Отправляем мотивационное сообщение с кнопкой
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(self.MESSAGES["button_text"], callback_data="invite_signup")]
        ])

        await self.send_message(
            update,
            self.MESSAGES["invite_text"],
            reply_markup=keyboard,
            parse_mode="HTML"
        )

    @BaseHandler.handle_errors
    async def handle_invite_signup(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Обработка нажатия на кнопку записи на консультацию.
        
        Args:
            update: Объект обновления Telegram
            context: Контекст бота
        """
        query = update.callback_query
        await query.answer()

        # Здесь можно добавить логику для записи на консультацию
        # Например, отправка формы или перенаправление на сайт
        await self.send_message(
            update,
            "🎉 Отлично! Скоро мы свяжемся с тобой для согласования времени консультации."
        )

def get_invite_handler() -> InviteHandler:
    """Get the invite handler instance."""
    return InviteHandler()
