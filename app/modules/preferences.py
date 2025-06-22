from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from typing import List, Optional
import json

from app.handlers.base import BaseHandler
from app.handlers.fsm_states import UserStates
from app.db.models import UserPreference
from app.utils.validation import ValidationError
from app.utils.logger import get_logger

logger = get_logger(__name__)

class PreferencesHandler(BaseHandler):
    """Handler for managing user preferences."""

    # Константы для форматирования
    MESSAGES = {
        "start": "Выберите тип предпочтений:",
        "current": "Текущие {type}:\n{items}\n\nВведите новый продукт:",
        "empty": "Нет записей",
        "new": "Введите продукт для добавления в {type}:",
        "invalid": "Пожалуйста, введите название продукта.",
        "updated": "Обновленный список {type}:\n{items}\n\nВведите еще один продукт или нажмите /cancel для завершения.",
        "deleted": "Предпочтение удалено."
    }

    # Константы для клавиатуры
    KEYBOARD = {
        "main": [
            [
                InlineKeyboardButton("Любимые продукты", callback_data="likes"),
                InlineKeyboardButton("Нелюбимые продукты", callback_data="dislikes")
            ],
            [InlineKeyboardButton("Назад", callback_data="back")]
        ]
    }

    def format_items(self, items: List[str]) -> str:
        """
        Форматирование списка продуктов.
        
        Args:
            items: Список продуктов
            
        Returns:
            str: Отформатированный список
        """
        return "\n".join(f"• {item}" for item in items) if items else self.MESSAGES["empty"]

    async def get_user_preferences(self, user_id: int) -> Optional[UserPreference]:
        """
        Получение предпочтений пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Optional[UserPreference]: Объект предпочтений или None
        """
        return await self.session.query(UserPreference).filter(
            UserPreference.user_id == user_id
        ).first()

    async def create_user_preferences(self, user_id: int) -> UserPreference:
        """
        Создание предпочтений пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            UserPreference: Созданный объект предпочтений
        """
        preferences = UserPreference(
            user_id=user_id,
            likes_raw="[]",
            dislikes_raw="[]"
        )
        self.session.add(preferences)
        await self.session.commit()
        return preferences

    @BaseHandler.handle_errors
    async def start_preferences(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Начало процесса управления предпочтениями.
        
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
        return UserStates.WAITING_FOR_PREFERENCES_TYPE

    @BaseHandler.handle_errors
    async def select_type(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Обработка выбора типа предпочтений.
        
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

        preference_type = query.data
        self.set_user_data(context, "preference_type", preference_type)

        user = await self.get_user(update.effective_user.id)
        if not user:
            raise ValidationError("Пользователь не найден")

        preferences = await self.get_user_preferences(user.id)
        if preferences:
            items = json.loads(getattr(preferences, f"{preference_type}_raw", "[]"))
            items_text = self.format_items(items)
            await self.send_message(
                update,
                self.MESSAGES["current"].format(type=preference_type, items=items_text)
            )
        else:
            await self.send_message(
                update,
                self.MESSAGES["new"].format(type=preference_type)
            )

        return UserStates.WAITING_FOR_PREFERENCES_ITEM

    @BaseHandler.handle_errors
    async def enter_item(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Обработка ввода нового продукта.
        
        Args:
            update: Объект обновления Telegram
            context: Контекст бота
            
        Returns:
            int: Код состояния после обработки команды
        """
        item = update.message.text.strip()
        if not item:
            await self.send_message(update, self.MESSAGES["invalid"])
            return UserStates.WAITING_FOR_PREFERENCES_ITEM

        preference_type = self.get_user_data(context, "preference_type")
        user = await self.get_user(update.effective_user.id)
        if not user:
            raise ValidationError("Пользователь не найден")

        preferences = await self.get_user_preferences(user.id)
        if not preferences:
            preferences = await self.create_user_preferences(user.id)

        # Get current items
        items = json.loads(getattr(preferences, f"{preference_type}_raw", "[]"))
        if item not in items:
            items.append(item)
            setattr(preferences, f"{preference_type}_raw", json.dumps(items))
            await self.session.commit()

        # Show updated list
        items_text = self.format_items(items)
        await self.send_message(
            update,
            self.MESSAGES["updated"].format(type=preference_type, items=items_text)
        )

        return UserStates.WAITING_FOR_PREFERENCES_ITEM

    @BaseHandler.handle_errors
    async def confirm_delete(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Обработка подтверждения удаления предпочтения.
        
        Args:
            update: Объект обновления Telegram
            context: Контекст бота
            
        Returns:
            int: Код состояния после обработки команды
        """
        query = update.callback_query
        await query.answer()

        if query.data == "no":
            return await self.start_preferences(update, context)

        preference_id = int(query.data.split("_")[1])
        preference = await self.session.query(UserPreference).get(preference_id)
        if preference:
            await self.session.delete(preference)
            await self.session.commit()

        await self.send_message(update, self.MESSAGES["deleted"])
        return await self.start_preferences(update, context)

def get_preferences_handler() -> ConversationHandler:
    """Get the preferences conversation handler."""
    handler = PreferencesHandler()
    return ConversationHandler(
        entry_points=[handler.start_preferences],
        states={
            UserStates.WAITING_FOR_PREFERENCES_TYPE: [
                handler.select_type
            ],
            UserStates.WAITING_FOR_PREFERENCES_ITEM: [
                handler.enter_item
            ]
        },
        fallbacks=[handler.confirm_delete]
    )
