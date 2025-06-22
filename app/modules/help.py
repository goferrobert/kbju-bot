from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from app.handlers.base import BaseHandler
from app.handlers.fsm_states import UserStates
from app.utils.logger import get_logger

logger = get_logger(__name__)

class HelpHandler(BaseHandler):
    """Handler for providing user assistance."""

    # Константы для форматирования
    MESSAGES = {
        "start": (
            "🤖 <b>Добро пожаловать в справку!</b>\n\n"
            "Выберите интересующий вас раздел:"
        ),
        "commands": (
            "📋 <b>Основные команды:</b>\n\n"
            "• /start - Начать работу с ботом\n"
            "• /help - Показать это сообщение\n"
            "• /weight - Ввести вес\n"
            "• /steps - Ввести количество шагов\n"
            "• /sport - Ввести данные о спорте\n"
            "• /progress - Показать прогресс\n"
            "• /preferences - Настроить предпочтения\n"
            "• /notifications - Управление уведомлениями\n"
            "• /cancel - Отменить текущее действие"
        ),
        "weight": (
            "⚖️ <b>Ввод веса:</b>\n\n"
            "• Используйте команду /weight для ввода веса\n"
            "• Введите вес в килограммах (например, 75.5)\n"
            "• Вес должен быть в диапазоне от 30 до 300 кг\n"
            "• Рекомендуется вводить вес ежедневно в одно и то же время"
        ),
        "steps": (
            "👣 <b>Ввод шагов:</b>\n\n"
            "• Используйте команду /steps для ввода шагов\n"
            "• Введите количество шагов за день\n"
            "• Количество шагов должно быть от 0 до 100000\n"
            "• Рекомендуется вводить данные вечером"
        ),
        "sport": (
            "🏃 <b>Ввод данных о спорте:</b>\n\n"
            "• Используйте команду /sport для ввода данных\n"
            "• Выберите тип активности\n"
            "• Укажите длительность тренировки\n"
            "• Введите интенсивность тренировки\n"
            "• Рекомендуется вводить данные сразу после тренировки"
        ),
        "progress": (
            "📊 <b>Просмотр прогресса:</b>\n\n"
            "• Используйте команду /progress для просмотра\n"
            "• Бот покажет график изменений веса\n"
            "• Отобразит процент жира (если введен)\n"
            "• Даст рекомендации по достижению цели"
        ),
        "preferences": (
            "⚙️ <b>Настройка предпочтений:</b>\n\n"
            "• Используйте команду /preferences\n"
            "• Добавьте любимые продукты\n"
            "• Укажите нелюбимые продукты\n"
            "• Настройки помогут в составлении рациона"
        ),
        "notifications": (
            "🔔 <b>Управление уведомлениями:</b>\n\n"
            "• Используйте команду /notifications\n"
            "• Выберите тип уведомления\n"
            "• Укажите время получения\n"
            "• Бот будет напоминать о вводе данных"
        ),
        "contact": (
            "📞 <b>Связаться с нами:</b>\n\n"
            "• По всем вопросам обращайтесь к @support\n"
            "• Время работы: Пн-Пт, 9:00-18:00\n"
            "• Среднее время ответа: 1-2 часа"
        )
    }

    # Константы для клавиатуры
    KEYBOARD = {
        "main": [
            [
                InlineKeyboardButton("Команды", callback_data="commands"),
                InlineKeyboardButton("Вес", callback_data="weight")
            ],
            [
                InlineKeyboardButton("Шаги", callback_data="steps"),
                InlineKeyboardButton("Спорт", callback_data="sport")
            ],
            [
                InlineKeyboardButton("Прогресс", callback_data="progress"),
                InlineKeyboardButton("Предпочтения", callback_data="preferences")
            ],
            [
                InlineKeyboardButton("Уведомления", callback_data="notifications"),
                InlineKeyboardButton("Контакты", callback_data="contact")
            ],
            [InlineKeyboardButton("Назад", callback_data="back")]
        ]
    }

    @BaseHandler.handle_errors
    async def start_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Начало процесса помощи.
        
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
        return UserStates.WAITING_FOR_HELP_SECTION

    @BaseHandler.handle_errors
    async def show_section(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Показ выбранного раздела помощи.
        
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
                reply_markup=InlineKeyboardMarkup(self.KEYBOARD["main"])
            )

        return UserStates.WAITING_FOR_HELP_SECTION

def get_help_handler() -> ConversationHandler:
    """Get the help conversation handler."""
    handler = HelpHandler()
    return ConversationHandler(
        entry_points=[handler.start_help],
        states={
            UserStates.WAITING_FOR_HELP_SECTION: [
                handler.show_section
            ]
        },
        fallbacks=[]
    ) 