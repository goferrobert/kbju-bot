from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from typing import Optional

from app.handlers.base import BaseHandler
from app.handlers.fsm_states import UserStates
from app.db.models import UserSettings
from app.utils.validation import ValidationError
from app.utils.logger import get_logger

logger = get_logger(__name__)

class SettingsHandler(BaseHandler):
    """Handler for managing user settings."""

    # Константы для форматирования
    MESSAGES = {
        "start": (
            "⚙️ <b>Настройки</b>\n\n"
            "Выберите настройку для изменения:"
        ),
        "language": (
            "🌐 <b>Язык</b>\n\n"
            "Выберите предпочитаемый язык:"
        ),
        "units": (
            "📏 <b>Единицы измерения</b>\n\n"
            "Выберите предпочитаемые единицы измерения:"
        ),
        "theme": (
            "🎨 <b>Тема оформления</b>\n\n"
            "Выберите предпочитаемую тему:"
        ),
        "privacy": (
            "🔒 <b>Конфиденциальность</b>\n\n"
            "Настройте параметры конфиденциальности:"
        ),
        "success": "✅ Настройки успешно сохранены!",
        "error": "❌ Произошла ошибка при сохранении настроек."
    }

    # Константы для клавиатуры
    KEYBOARD = {
        "main": [
            [
                InlineKeyboardButton("Язык", callback_data="language"),
                InlineKeyboardButton("Единицы измерения", callback_data="units")
            ],
            [
                InlineKeyboardButton("Тема", callback_data="theme"),
                InlineKeyboardButton("Конфиденциальность", callback_data="privacy")
            ],
            [InlineKeyboardButton("Назад", callback_data="back")]
        ],
        "language": [
            [
                InlineKeyboardButton("Русский", callback_data="lang_ru"),
                InlineKeyboardButton("English", callback_data="lang_en")
            ],
            [InlineKeyboardButton("Назад", callback_data="back")]
        ],
        "units": [
            [
                InlineKeyboardButton("Метрическая", callback_data="units_metric"),
                InlineKeyboardButton("Имперская", callback_data="units_imperial")
            ],
            [InlineKeyboardButton("Назад", callback_data="back")]
        ],
        "theme": [
            [
                InlineKeyboardButton("Светлая", callback_data="theme_light"),
                InlineKeyboardButton("Темная", callback_data="theme_dark")
            ],
            [InlineKeyboardButton("Назад", callback_data="back")]
        ],
        "privacy": [
            [
                InlineKeyboardButton("Публичный", callback_data="privacy_public"),
                InlineKeyboardButton("Приватный", callback_data="privacy_private")
            ],
            [InlineKeyboardButton("Назад", callback_data="back")]
        ]
    }

    async def get_user_settings(self, user_id: int) -> Optional[UserSettings]:
        """
        Получение настроек пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Optional[UserSettings]: Объект настроек или None
        """
        return await self.session.query(UserSettings).filter(
            UserSettings.user_id == user_id
        ).first()

    async def create_user_settings(self, user_id: int) -> UserSettings:
        """
        Создание настроек пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            UserSettings: Созданный объект настроек
        """
        settings = UserSettings(
            user_id=user_id,
            language="ru",
            units="metric",
            theme="light",
            privacy="private",
            settings_raw="{}"
        )
        self.session.add(settings)
        await self.session.commit()
        return settings

    @BaseHandler.handle_errors
    async def start_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Начало процесса управления настройками.
        
        Args:
            update: Объект обновления Telegram
            context: Контекст бота
            
        Returns:
            int: Код состояния после обработки команды
        """
        await self.send_message(
            update,
            self.MESSAGES["start"],
            reply_markup=InlineKeyboardMarkup(self.KEYBOARD["main"])
        )
        return UserStates.WAITING_FOR_SETTINGS_SECTION

    @BaseHandler.handle_errors
    async def select_section(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Обработка выбора раздела настроек.
        
        Args:
            update: Объект обновления Telegram
            context: Контекст бота
            
        Returns:
            int: Код состояния после обработки команды
        """
        query = update.callback_query
        await query.answer()

        if query.data == "back":
            return ConversationHandler.END

        section = query.data
        if section in self.MESSAGES:
            await self.send_message(
                update,
                self.MESSAGES[section],
                reply_markup=InlineKeyboardMarkup(self.KEYBOARD[section])
            )

        return UserStates.WAITING_FOR_SETTINGS_VALUE

    @BaseHandler.handle_errors
    async def save_setting(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Сохранение выбранной настройки.
        
        Args:
            update: Объект обновления Telegram
            context: Контекст бота
            
        Returns:
            int: Код состояния после обработки команды
        """
        query = update.callback_query
        await query.answer()

        if query.data == "back":
            return await self.start_settings(update, context)

        setting_type, value = query.data.split("_")
        user = await self.get_user(update.effective_user.id)
        if not user:
            raise ValidationError("Пользователь не найден")

        settings = await self.get_user_settings(user.id)
        if not settings:
            settings = await self.create_user_settings(user.id)

        # Обновляем настройки
        setattr(settings, setting_type, value)
        await self.session.commit()

        await self.send_message(update, self.MESSAGES["success"])
        return await self.start_settings(update, context)

def get_settings_handler() -> ConversationHandler:
    """Get the settings conversation handler."""
    handler = SettingsHandler()
    return ConversationHandler(
        entry_points=[handler.start_settings],
        states={
            UserStates.WAITING_FOR_SETTINGS_SECTION: [
                handler.select_section
            ],
            UserStates.WAITING_FOR_SETTINGS_VALUE: [
                handler.save_setting
            ]
        },
        fallbacks=[]
    ) 