from typing import Optional, Any
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TelegramError

class BaseBotError(Exception):
    """Базовый класс для всех ошибок бота"""
    def __init__(self, message: str, user_id: Optional[int] = None):
        self.message = message
        self.user_id = user_id
        super().__init__(self.message)

class ValidationError(BaseBotError):
    """Ошибка валидации данных"""
    pass

class DatabaseError(BaseBotError):
    """Ошибка работы с базой данных"""
    pass

class CalculationError(BaseBotError):
    """Ошибка в расчетах"""
    pass

async def handle_error(update: Update, context: ContextTypes.DEFAULT_TYPE, error: Exception) -> None:
    """Обработчик ошибок для бота"""
    error_message = "❌ Произошла ошибка. Пожалуйста, попробуйте позже."
    
    if isinstance(error, ValidationError):
        error_message = f"❌ {error.message}"
    elif isinstance(error, DatabaseError):
        error_message = "❌ Ошибка при работе с данными. Попробуйте позже."
    elif isinstance(error, CalculationError):
        error_message = f"❌ {error.message}"
    elif isinstance(error, TelegramError):
        error_message = "❌ Ошибка при отправке сообщения. Попробуйте позже."
    
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(error_message, parse_mode="HTML")
        elif update and update.callback_query:
            await update.callback_query.message.reply_text(error_message, parse_mode="HTML")
    except Exception as e:
        # Если не удалось отправить сообщение об ошибке, логируем это
        print(f"Failed to send error message: {str(e)}")
    
    # Логируем ошибку
    print(f"Error occurred: {str(error)}")
    if context and context.error:
        print(f"Context error: {str(context.error)}") 