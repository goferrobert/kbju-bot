from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from app.handlers.base import BaseHandler
from app.handlers.fsm_states import UserStates
from app.db.models import UserRecord
from app.utils.validation import ValidationError
from app.utils.logging import get_logger

logger = get_logger(__name__)

class StepsHandler(BaseHandler):
    """Handler for managing user's daily steps."""

    STEP_LEVELS = {
        "low": "Менее 5000 шагов",
        "medium": "5000-10000 шагов",
        "high": "Более 10000 шагов"
    }

    async def start_steps(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start the steps tracking process."""
        keyboard = [
            [InlineKeyboardButton(level, callback_data=level_id)]
            for level_id, level in self.STEP_LEVELS.items()
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await self.send_message(
            update,
            "Выберите ваш средний уровень ежедневной активности:",
            reply_markup=reply_markup
        )
        return UserStates.WAITING_FOR_STEP_LEVEL

    async def handle_step_level(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle step level selection."""
        query = update.callback_query
        await query.answer()

        step_level = query.data
        if step_level not in self.STEP_LEVELS:
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

        # Обновляем уровень шагов
        record.step_level = step_level
        await self.session.commit()

        # Формируем рекомендации
        recommendations = self._get_step_recommendations(step_level, user.goal)
        
        message = (
            f"✅ Уровень активности обновлен: {self.STEP_LEVELS[step_level]}\n\n"
            f"Рекомендации:\n{recommendations}"
        )

        await self.send_message(update, message)
        return ConversationHandler.END

    def _get_step_recommendations(self, step_level: str, goal: str) -> str:
        """Get step recommendations based on level and goal."""
        recommendations = []

        if goal == "Нормальное тело":
            if step_level == "low":
                recommendations.extend([
                    "• Старайтесь делать минимум 5000 шагов в день",
                    "• Используйте лестницу вместо лифта",
                    "• Совершайте короткие прогулки"
                ])
            elif step_level == "medium":
                recommendations.extend([
                    "• Отличный уровень активности!",
                    "• Поддерживайте текущий уровень",
                    "• Добавьте прогулки в парке"
                ])
            else:  # high
                recommendations.extend([
                    "• Отлично! Вы очень активны",
                    "• Следите за восстановлением",
                    "• Не забывайте про растяжку"
                ])
        elif goal == "Спортивное тело":
            if step_level == "low":
                recommendations.extend([
                    "• Увеличьте ежедневную активность",
                    "• Добавьте кардио тренировки",
                    "• Больше ходите пешком"
                ])
            elif step_level == "medium":
                recommendations.extend([
                    "• Хороший уровень для набора массы",
                    "• Комбинируйте с силовыми",
                    "• Следите за питанием"
                ])
            else:  # high
                recommendations.extend([
                    "• Высокая активность",
                    "• Увеличьте калории",
                    "• Следите за восстановлением"
                ])
        else:  # Сухое тело
            if step_level == "low":
                recommendations.extend([
                    "• Увеличьте ежедневную активность",
                    "• Добавьте больше кардио",
                    "• Ходите пешком минимум 1 час"
                ])
            elif step_level == "medium":
                recommendations.extend([
                    "• Идеальный уровень для сушки",
                    "• Поддерживайте активность",
                    "• Следите за питанием"
                ])
            else:  # high
                recommendations.extend([
                    "• Отличный уровень для сушки",
                    "• Контролируйте калории",
                    "• Не допускайте перетренированности"
                ])

        return "\n".join(recommendations)

def get_steps_handler() -> ConversationHandler:
    """Get the steps conversation handler."""
    handler = StepsHandler()
    return ConversationHandler(
        entry_points=[handler.start_steps],
        states={
            UserStates.WAITING_FOR_STEP_LEVEL: [
                handler.handle_step_level
            ]
        },
        fallbacks=[]
    ) 