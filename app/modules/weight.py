from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from app.handlers.base import BaseHandler
from app.handlers.fsm_states import UserStates
from app.db.models import UserRecord
from app.utils.validation import ValidationError
from app.utils.logging import get_logger

logger = get_logger(__name__)

class WeightHandler(BaseHandler):
    """Handler for managing user's weight."""

    async def start_weight(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start the weight tracking process."""
        await self.send_message(
            update,
            "Введите ваш текущий вес (кг):"
        )
        return UserStates.WAITING_FOR_UPDATE_WEIGHT

    async def handle_weight(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle weight input."""
        try:
            weight = float(update.message.text.replace(",", "."))
            if weight <= 0 or weight > 300:
                raise ValueError
        except ValueError:
            await self.send_message(
                update,
                "Пожалуйста, введите корректный вес (от 1 до 300 кг):"
            )
            return UserStates.WAITING_FOR_UPDATE_WEIGHT

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

        # Сохраняем предыдущий вес для анализа
        old_weight = record.weight

        # Обновляем вес
        record.weight = weight
        await self.session.commit()

        # Формируем сообщение
        message = f"✅ Вес обновлен: {weight:.1f} кг\n\n"

        if old_weight:
            weight_change = weight - old_weight
            weight_percent = (weight_change / old_weight) * 100
            message += (
                f"Изменение: {weight_change:+.1f} кг ({weight_percent:+.1f}%)\n\n"
            )

            if user.goal == "Нормальное тело":
                if weight_change < -0.5:
                    message += "Отличный прогресс в снижении веса! Продолжайте в том же духе."
                elif weight_change > 0.5:
                    message += "Внимание: наблюдается набор веса. Проверьте питание и активность."
                else:
                    message += "Вес стабилен. Продолжайте придерживаться текущего режима."
            elif user.goal == "Спортивное тело":
                if weight_change > 0.5:
                    message += "Отличный набор массы! Возможно, это мышцы."
                elif weight_change < -0.5:
                    message += "Внимание: наблюдается потеря веса. Увеличьте калории."
                else:
                    message += "Вес стабилен. Продолжайте тренировки."
            else:  # Сухое тело
                if weight_change < -0.3:
                    message += "Отличный прогресс в снижении веса! Продолжайте в том же духе."
                elif weight_change > 0.3:
                    message += "Внимание: наблюдается набор веса. Проверьте питание."
                else:
                    message += "Вес стабилен. Продолжайте придерживаться текущего режима."

        await self.send_message(update, message)
        return ConversationHandler.END

def get_weight_handler() -> ConversationHandler:
    """Get the weight conversation handler."""
    handler = WeightHandler()
    return ConversationHandler(
        entry_points=[handler.start_weight],
        states={
            UserStates.WAITING_FOR_UPDATE_WEIGHT: [
                handler.handle_weight
            ]
        },
        fallbacks=[]
    ) 