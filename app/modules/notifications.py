from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from typing import List, Optional, Dict
from datetime import datetime, time

from app.handlers.base import BaseHandler
from app.handlers.fsm_states import UserStates
from app.db.models import User, UserNotification
from app.utils.validation import ValidationError
from app.utils.logging import get_logger

logger = get_logger(__name__)

class NotificationsHandler(BaseHandler):
    """Handler for managing user notifications."""

    # Константы для форматирования
    MESSAGES = {
        "start": "Выберите тип уведомлений:",
        "time": "Введите время уведомления в формате ЧЧ:ММ (например, 09:00):",
        "invalid_time": "Неверный формат времени. Пожалуйста, используйте формат ЧЧ:ММ (например, 09:00).",
        "success": "Уведомление успешно настроено!",
        "list": "Ваши текущие уведомления:\n{notifications}",
        "empty": "У вас пока нет настроенных уведомлений.",
        "deleted": "Уведомление удалено."
    }

    # Константы для клавиатуры
    KEYBOARD = {
        "main": [
            [
                InlineKeyboardButton("Вес", callback_data="weight"),
                InlineKeyboardButton("Шаги", callback_data="steps")
            ],
            [
                InlineKeyboardButton("Спорт", callback_data="sport"),
                InlineKeyboardButton("Питание", callback_data="nutrition")
            ],
            [InlineKeyboardButton("Назад", callback_data="back")]
        ]
    }

    def format_time(self, notification_time: time) -> str:
        """
        Форматирование времени уведомления.
        
        Args:
            notification_time: Время уведомления
            
        Returns:
            str: Отформатированное время
        """
        return notification_time.strftime("%H:%M")

    def parse_time(self, time_str: str) -> Optional[time]:
        """
        Парсинг времени из строки.
        
        Args:
            time_str: Строка с временем
            
        Returns:
            Optional[time]: Объект времени или None при ошибке
        """
        try:
            hour, minute = map(int, time_str.split(":"))
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                return time(hour, minute)
        except (ValueError, TypeError):
            pass
        return None

    def format_notifications(self, notifications: List[UserNotification]) -> str:
        """
        Форматирование списка уведомлений.
        
        Args:
            notifications: Список уведомлений
            
        Returns:
            str: Отформатированный список
        """
        if not notifications:
            return self.MESSAGES["empty"]

        result = []
        for notification in notifications:
            time_str = self.format_time(notification.notification_time)
            result.append(f"• {notification.type}: {time_str}")
        return "\n".join(result)

    async def get_user_notifications(self, user_id: int) -> List[UserNotification]:
        """
        Получение уведомлений пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            List[UserNotification]: Список уведомлений
        """
        return await self.session.query(UserNotification).filter(
            UserNotification.user_id == user_id
        ).all()

    @BaseHandler.handle_errors
    async def start_notifications(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Начало процесса управления уведомлениями.
        
        Args:
            update: Объект обновления Telegram
            context: Контекст бота
            
        Returns:
            int: Код состояния после обработки команды
        """
        user = await self.get_user(update.effective_user.id)
        if not user:
            raise ValidationError("Пользователь не найден")

        notifications = await self.get_user_notifications(user.id)
        if notifications:
            await self.send_message(
                update,
                self.MESSAGES["list"].format(
                    notifications=self.format_notifications(notifications)
                )
            )

        await self.send_message(
            update,
            self.MESSAGES["start"],
            reply_markup=InlineKeyboardMarkup(self.KEYBOARD["main"])
        )
        return UserStates.WAITING_FOR_NOTIFICATION_TYPE

    @BaseHandler.handle_errors
    async def select_type(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Обработка выбора типа уведомления.
        
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

        notification_type = query.data
        self.set_user_data(context, "notification_type", notification_type)

        await self.send_message(update, self.MESSAGES["time"])
        return UserStates.WAITING_FOR_NOTIFICATION_TIME

    @BaseHandler.handle_errors
    async def enter_time(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Обработка ввода времени уведомления.
        
        Args:
            update: Объект обновления Telegram
            context: Контекст бота
            
        Returns:
            int: Код состояния после обработки команды
        """
        time_str = update.message.text.strip()
        notification_time = self.parse_time(time_str)

        if not notification_time:
            await self.send_message(update, self.MESSAGES["invalid_time"])
            return UserStates.WAITING_FOR_NOTIFICATION_TIME

        notification_type = self.get_user_data(context, "notification_type")
        user = await self.get_user(update.effective_user.id)
        if not user:
            raise ValidationError("Пользователь не найден")

        # Создаем новое уведомление
        notification = UserNotification(
            user_id=user.id,
            type=notification_type,
            notification_time=notification_time
        )
        self.session.add(notification)
        await self.session.commit()

        # Показываем обновленный список
        notifications = await self.get_user_notifications(user.id)
        await self.send_message(
            update,
            self.MESSAGES["success"] + "\n\n" +
            self.MESSAGES["list"].format(
                notifications=self.format_notifications(notifications)
            )
        )

        return await self.start_notifications(update, context)

    @BaseHandler.handle_errors
    async def delete_notification(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Удаление уведомления.
        
        Args:
            update: Объект обновления Telegram
            context: Контекст бота
            
        Returns:
            int: Код состояния после обработки команды
        """
        query = update.callback_query
        await query.answer()

        notification_id = int(query.data.split("_")[1])
        notification = await self.session.query(UserNotification).get(notification_id)
        if notification:
            await self.session.delete(notification)
            await self.session.commit()

        await self.send_message(update, self.MESSAGES["deleted"])
        return await self.start_notifications(update, context)

def get_notifications_handler() -> ConversationHandler:
    """Get the notifications conversation handler."""
    handler = NotificationsHandler()
    return ConversationHandler(
        entry_points=[handler.start_notifications],
        states={
            UserStates.WAITING_FOR_NOTIFICATION_TYPE: [
                handler.select_type
            ],
            UserStates.WAITING_FOR_NOTIFICATION_TIME: [
                handler.enter_time
            ]
        },
        fallbacks=[handler.delete_notification]
    ) 