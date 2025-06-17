from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import json

from app.handlers.base import BaseHandler
from app.handlers.fsm_states import UserStates
from app.db.models import User, UserReminder
from app.utils.validation import ValidationError
from app.utils.logging import get_logger

logger = get_logger(__name__)

class RemindersHandler(BaseHandler):
    """Handler for managing user reminders."""

    # Константы для форматирования
    MESSAGES = {
        "start": (
            "⏰ <b>Управление напоминаниями</b>\n\n"
            "Выберите действие:"
        ),
        "list": (
            "📋 <b>Ваши напоминания</b>\n\n"
            "{reminders}\n"
            "Выберите напоминание для редактирования или создайте новое:"
        ),
        "reminder": (
            "• {time} - {type}\n"
            "  Статус: {status}"
        ),
        "create": (
            "Создание нового напоминания\n\n"
            "Выберите тип напоминания:"
        ),
        "time": (
            "Введите время напоминания в формате ЧЧ:ММ\n"
            "Например: 09:00"
        ),
        "success": "✅ Напоминание успешно {action}",
        "delete_confirm": (
            "⚠️ Вы уверены, что хотите удалить напоминание?\n"
            "• Время: {time}\n"
            "• Тип: {type}"
        ),
        "no_reminders": "У вас пока нет напоминаний.",
        "invalid_time": "❌ Неверный формат времени. Используйте формат ЧЧ:ММ",
        "invalid_type": "❌ Неверный тип напоминания",
        "back": "Назад"
    }

    # Константы для клавиатуры
    KEYBOARD = {
        "main": [
            [
                InlineKeyboardButton("Список напоминаний", callback_data="list"),
                InlineKeyboardButton("Создать напоминание", callback_data="create")
            ],
            [InlineKeyboardButton("Назад", callback_data="back")]
        ],
        "types": [
            [
                InlineKeyboardButton("Вес", callback_data="weight"),
                InlineKeyboardButton("Шаги", callback_data="steps")
            ],
            [
                InlineKeyboardButton("Спорт", callback_data="sport"),
                InlineKeyboardButton("Питание", callback_data="nutrition")
            ],
            [InlineKeyboardButton("Назад", callback_data="back")]
        ],
        "actions": [
            [
                InlineKeyboardButton("Редактировать", callback_data="edit"),
                InlineKeyboardButton("Удалить", callback_data="delete")
            ],
            [InlineKeyboardButton("Назад", callback_data="back")]
        ]
    }

    REMINDER_TYPES = {
        "weight": "Вес",
        "steps": "Шаги",
        "sport": "Спорт",
        "nutrition": "Питание"
    }

    def format_reminder(self, reminder: UserReminder) -> str:
        """
        Форматирование напоминания для отображения.
        
        Args:
            reminder: Объект напоминания
            
        Returns:
            str: Отформатированное напоминание
        """
        return self.MESSAGES["reminder"].format(
            time=reminder.time.strftime("%H:%M"),
            type=self.REMINDER_TYPES.get(reminder.type, reminder.type),
            status="✅ Активно" if reminder.is_active else "❌ Отключено"
        )

    def format_reminders_list(self, reminders: List[UserReminder]) -> str:
        """
        Форматирование списка напоминаний.
        
        Args:
            reminders: Список напоминаний
            
        Returns:
            str: Отформатированный список
        """
        if not reminders:
            return self.MESSAGES["no_reminders"]
        
        return "\n".join(self.format_reminder(r) for r in reminders)

    def validate_time(self, time_str: str) -> Optional[datetime.time]:
        """
        Валидация времени напоминания.
        
        Args:
            time_str: Строка с временем
            
        Returns:
            Optional[datetime.time]: Объект времени или None
        """
        try:
            hour, minute = map(int, time_str.split(":"))
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                return datetime.time(hour, minute)
        except (ValueError, TypeError):
            pass
        return None

    @BaseHandler.handle_errors
    async def start_reminders(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Начало процесса управления напоминаниями.
        
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
        return UserStates.WAITING_FOR_REMINDER_ACTION

    @BaseHandler.handle_errors
    async def list_reminders(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Отображение списка напоминаний.
        
        Args:
            update: Объект обновления Telegram
            context: Контекст бота
            
        Returns:
            int: Код состояния после обработки команды
        """
        query = update.callback_query
        await query.answer()

        user = await self.get_user(update.effective_user.id)
        if not user:
            raise ValidationError("Пользователь не найден")

        reminders = await self.get_all_reminders(user.id)
        message = self.MESSAGES["list"].format(
            reminders=self.format_reminders_list(reminders)
        )

        await self.send_message(
            update,
            message,
            reply_markup=InlineKeyboardMarkup(self.KEYBOARD["main"])
        )
        return UserStates.WAITING_FOR_REMINDER_ACTION

    @BaseHandler.handle_errors
    async def create_reminder(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Создание нового напоминания.
        
        Args:
            update: Объект обновления Telegram
            context: Контекст бота
            
        Returns:
            int: Код состояния после обработки команды
        """
        query = update.callback_query
        await query.answer()

        await self.send_message(
            update,
            self.MESSAGES["create"],
            reply_markup=InlineKeyboardMarkup(self.KEYBOARD["types"])
        )
        return UserStates.WAITING_FOR_REMINDER_TYPE

    @BaseHandler.handle_errors
    async def select_reminder_type(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Выбор типа напоминания.
        
        Args:
            update: Объект обновления Telegram
            context: Контекст бота
            
        Returns:
            int: Код состояния после обработки команды
        """
        query = update.callback_query
        await query.answer()

        if query.data == "back":
            return await self.start_reminders(update, context)

        if query.data not in self.REMINDER_TYPES:
            await self.send_message(update, self.MESSAGES["invalid_type"])
            return await self.create_reminder(update, context)

        context.user_data["reminder_type"] = query.data
        await self.send_message(update, self.MESSAGES["time"])
        return UserStates.WAITING_FOR_REMINDER_TIME

    @BaseHandler.handle_errors
    async def set_reminder_time(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Установка времени напоминания.
        
        Args:
            update: Объект обновления Telegram
            context: Контекст бота
            
        Returns:
            int: Код состояния после обработки команды
        """
        time_str = update.message.text
        time = self.validate_time(time_str)

        if not time:
            await self.send_message(update, self.MESSAGES["invalid_time"])
            return UserStates.WAITING_FOR_REMINDER_TIME

        user = await self.get_user(update.effective_user.id)
        if not user:
            raise ValidationError("Пользователь не найден")

        reminder_type = context.user_data.get("reminder_type")
        if not reminder_type:
            return await self.start_reminders(update, context)

        # Создаем напоминание
        reminder = UserReminder(
            user_id=user.id,
            type=reminder_type,
            time=time,
            is_active=True
        )
        await self.save_reminder(reminder)

        await self.send_message(
            update,
            self.MESSAGES["success"].format(action="создано"),
            reply_markup=InlineKeyboardMarkup(self.KEYBOARD["main"])
        )
        return UserStates.WAITING_FOR_REMINDER_ACTION

    @BaseHandler.handle_errors
    async def edit_reminder(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Редактирование напоминания.
        
        Args:
            update: Объект обновления Telegram
            context: Контекст бота
            
        Returns:
            int: Код состояния после обработки команды
        """
        query = update.callback_query
        await query.answer()

        reminder_id = context.user_data.get("selected_reminder_id")
        if not reminder_id:
            return await self.start_reminders(update, context)

        reminder = await self.get_reminder(reminder_id)
        if not reminder:
            return await self.start_reminders(update, context)

        # Переключаем статус
        reminder.is_active = not reminder.is_active
        await self.save_reminder(reminder)

        await self.send_message(
            update,
            self.MESSAGES["success"].format(
                action="активировано" if reminder.is_active else "деактивировано"
            ),
            reply_markup=InlineKeyboardMarkup(self.KEYBOARD["main"])
        )
        return UserStates.WAITING_FOR_REMINDER_ACTION

    @BaseHandler.handle_errors
    async def delete_reminder(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Удаление напоминания.
        
        Args:
            update: Объект обновления Telegram
            context: Контекст бота
            
        Returns:
            int: Код состояния после обработки команды
        """
        query = update.callback_query
        await query.answer()

        reminder_id = context.user_data.get("selected_reminder_id")
        if not reminder_id:
            return await self.start_reminders(update, context)

        reminder = await self.get_reminder(reminder_id)
        if not reminder:
            return await self.start_reminders(update, context)

        await self.delete_reminder(reminder_id)

        await self.send_message(
            update,
            self.MESSAGES["success"].format(action="удалено"),
            reply_markup=InlineKeyboardMarkup(self.KEYBOARD["main"])
        )
        return UserStates.WAITING_FOR_REMINDER_ACTION

def get_reminders_handler() -> ConversationHandler:
    """Get the reminders conversation handler."""
    handler = RemindersHandler()
    return ConversationHandler(
        entry_points=[handler.start_reminders],
        states={
            UserStates.WAITING_FOR_REMINDER_ACTION: [
                handler.list_reminders,
                handler.create_reminder
            ],
            UserStates.WAITING_FOR_REMINDER_TYPE: [
                handler.select_reminder_type
            ],
            UserStates.WAITING_FOR_REMINDER_TIME: [
                handler.set_reminder_time
            ]
        },
        fallbacks=[]
    ) 