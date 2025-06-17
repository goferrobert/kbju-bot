from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from app.handlers.base import BaseHandler
from app.handlers.fsm_states import UserStates
from app.db.models import UserRecord
from app.utils.validation import ValidationError
from app.utils.logging import get_logger

logger = get_logger(__name__)

class SportHandler(BaseHandler):
    """Handler for managing user's sport activities."""

    ACTIVITY_LEVELS = {
        "low": "Низкая (1-2 раза в неделю)",
        "medium": "Средняя (3-4 раза в неделю)",
        "high": "Высокая (5+ раз в неделю)"
    }

    async def start_sport(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start the sport activity tracking process."""
        keyboard = [
            [InlineKeyboardButton(level, callback_data=level_id)]
            for level_id, level in self.ACTIVITY_LEVELS.items()
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await self.send_message(
            update,
            "Выберите ваш уровень физической активности:",
            reply_markup=reply_markup
        )
        return UserStates.WAITING_FOR_ACTIVITY_LEVEL

    async def handle_activity_level(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle activity level selection."""
        query = update.callback_query
        await query.answer()

        activity_level = query.data
        if activity_level not in self.ACTIVITY_LEVELS:
            raise ValidationError("Неверный уровень активности")

        user = await self.get_user(update.effective_user.id)
        if not user:
            raise ValidationError("Пользователь не найден")

        # Получаем последнюю запись пользователя
        record = await self.session.query(UserRecord).filter(
            UserRecord.user_id == user.id
        ).order_by(UserRecord.created_at.desc()).first()

        if not record:
            record = UserRecord(user_id=user.id)
            self.session.add(record)

        # Обновляем уровень активности
        record.activity_level = activity_level
        await self.session.commit()

        # Формируем рекомендации
        recommendations = self._get_activity_recommendations(activity_level, user.goal)
        
        message = (
            f"✅ Уровень активности обновлен: {self.ACTIVITY_LEVELS[activity_level]}\n\n"
            f"Рекомендации:\n{recommendations}"
        )

        await self.send_message(update, message)
        return ConversationHandler.END

    def _get_activity_recommendations(self, activity_level: str, goal: str) -> str:
        """Get activity recommendations based on level and goal."""
        recommendations = []

        if goal == "Нормальное тело":
            if activity_level == "low":
                recommendations.extend([
                    "• Начните с 2-3 тренировок в неделю",
                    "• Фокус на кардио и базовых упражнениях",
                    "• Постепенно увеличивайте нагрузку"
                ])
            elif activity_level == "medium":
                recommendations.extend([
                    "• Поддерживайте 3-4 тренировки в неделю",
                    "• Комбинируйте кардио и силовые",
                    "• Следите за восстановлением"
                ])
            else:  # high
                recommendations.extend([
                    "• Отлично! Поддерживайте высокую активность",
                    "• Разнообразьте тренировки",
                    "• Не забывайте про отдых и восстановление"
                ])
        elif goal == "Спортивное тело":
            if activity_level == "low":
                recommendations.extend([
                    "• Увеличьте частоту тренировок до 3-4 раз",
                    "• Добавьте больше силовых упражнений",
                    "• Следите за прогрессией нагрузок"
                ])
            elif activity_level == "medium":
                recommendations.extend([
                    "• Идеальная частота для набора массы",
                    "• Фокус на базовых упражнениях",
                    "• Следите за техникой выполнения"
                ])
            else:  # high
                recommendations.extend([
                    "• Отлично! Поддерживайте интенсивность",
                    "• Разделите тренировки по группам мышц",
                    "• Уделите внимание восстановлению"
                ])
        else:  # Сухое тело
            if activity_level == "low":
                recommendations.extend([
                    "• Увеличьте частоту до 3-4 раз",
                    "• Добавьте больше кардио",
                    "• Следите за питанием"
                ])
            elif activity_level == "medium":
                recommendations.extend([
                    "• Идеальная частота для сушки",
                    "• Комбинируйте кардио и силовые",
                    "• Контролируйте калории"
                ])
            else:  # high
                recommendations.extend([
                    "• Отлично! Поддерживайте активность",
                    "• Следите за восстановлением",
                    "• Не допускайте перетренированности"
                ])

        return "\n".join(recommendations)

def get_sport_handler() -> ConversationHandler:
    """Get the sport conversation handler."""
    handler = SportHandler()
    return ConversationHandler(
        entry_points=[handler.start_sport],
        states={
            UserStates.WAITING_FOR_ACTIVITY_LEVEL: [
                handler.handle_activity_level
            ]
        },
        fallbacks=[]
    ) 