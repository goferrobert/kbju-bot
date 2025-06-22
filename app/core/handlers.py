from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from app.core.logging import get_logger
from app.core.errors import handle_error

logger = get_logger(__name__)

class BaseHandler:
    """
    Базовый класс для всех обработчиков
    """
    def __init__(self):
        self.logger = logger

    def handle_errors(self, func):
        """
        Декоратор для обработки ошибок
        """
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            try:
                return await func(update, context, *args, **kwargs)
            except Exception as e:
                self.logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
                await handle_error(update, context, e)
                return ConversationHandler.END
        return wrapper

    async def send_message(self, update: Update, text: str, **kwargs):
        """
        Отправка сообщения с обработкой ошибок
        """
        try:
            message = update.message or update.callback_query.message
            await message.reply_text(text, **kwargs)
        except Exception as e:
            self.logger.error(f"Error sending message: {str(e)}", exc_info=True)
            raise

    def get_user_data(self, context: ContextTypes.DEFAULT_TYPE, key: str, default=None):
        """
        Безопасное получение данных пользователя
        """
        return context.user_data.get(key, default)

    def set_user_data(self, context: ContextTypes.DEFAULT_TYPE, key: str, value):
        """
        Установка данных пользователя
        """
        context.user_data[key] = value 
