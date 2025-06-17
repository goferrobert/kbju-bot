from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from app.handlers.base import BaseHandler
from app.handlers.fsm_states import UserStates
from app.db.models import UserRecord
from app.utils.validation import ValidationError
from app.utils.logging import get_logger
from app.utils.calculations import calculate_body_fat

logger = get_logger(__name__)

class UpdateMetricsHandler(BaseHandler):
    """Handler for updating user metrics."""

    async def start_update_metrics(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start the metrics update process."""
        await self.send_message(
            update,
            "Введите ваш текущий вес (кг):"
        )
        return UserStates.WAITING_FOR_UPDATE_WEIGHT

    async def handle_update_weight(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle weight update."""
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

        self.set_user_data(context, "weight", weight)
        await self.send_message(
            update,
            "Введите ваш уровень активности (от 1.2 до 2.0):\n"
            "1.2 - сидячий образ жизни\n"
            "1.375 - легкая активность\n"
            "1.55 - умеренная активность\n"
            "1.725 - высокая активность\n"
            "2.0 - очень высокая активность"
        )
        return UserStates.WAITING_FOR_UPDATE_ACTIVITY

    async def handle_update_activity(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle activity level update."""
        try:
            activity = float(update.message.text.replace(",", "."))
            if activity < 1.2 or activity > 2.0:
                raise ValueError
        except ValueError:
            await self.send_message(
                update,
                "Пожалуйста, введите корректный уровень активности (от 1.2 до 2.0):"
            )
            return UserStates.WAITING_FOR_UPDATE_ACTIVITY

        self.set_user_data(context, "activity_level", activity)
        await self.send_message(
            update,
            "Введите обхват талии (см):"
        )
        return UserStates.WAITING_FOR_UPDATE_WAIST

    async def handle_update_waist(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle waist measurement update."""
        try:
            waist = float(update.message.text.replace(",", "."))
            if waist <= 0 or waist > 200:
                raise ValueError
        except ValueError:
            await self.send_message(
                update,
                "Пожалуйста, введите корректный обхват талии (от 1 до 200 см):"
            )
            return UserStates.WAITING_FOR_UPDATE_WAIST

        self.set_user_data(context, "waist", waist)
        await self.send_message(
            update,
            "Введите обхват шеи (см):"
        )
        return UserStates.WAITING_FOR_UPDATE_NECK

    async def handle_update_neck(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle neck measurement update."""
        try:
            neck = float(update.message.text.replace(",", "."))
            if neck <= 0 or neck > 100:
                raise ValueError
        except ValueError:
            await self.send_message(
                update,
                "Пожалуйста, введите корректный обхват шеи (от 1 до 100 см):"
            )
            return UserStates.WAITING_FOR_UPDATE_NECK

        self.set_user_data(context, "neck", neck)

        # Проверяем пол пользователя
        user = await self.get_user(update.effective_user.id)
        if not user:
            raise ValidationError("Пользователь не найден")

        if user.sex.lower() == "женский":
            await self.send_message(
                update,
                "Введите обхват бёдер (см):"
            )
            return UserStates.WAITING_FOR_UPDATE_HIP
        else:
            return await self.finalize_update(update, context)

    async def handle_update_hip(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle hip measurement update."""
        try:
            hip = float(update.message.text.replace(",", "."))
            if hip <= 0 or hip > 200:
                raise ValueError
        except ValueError:
            await self.send_message(
                update,
                "Пожалуйста, введите корректный обхват бёдер (от 1 до 200 см):"
            )
            return UserStates.WAITING_FOR_UPDATE_HIP

        self.set_user_data(context, "hip", hip)
        return await self.finalize_update(update, context)

    async def finalize_update(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Finalize the metrics update process."""
        user = await self.get_user(update.effective_user.id)
        if not user:
            raise ValidationError("Пользователь не найден")

        # Получаем все данные
        weight = self.get_user_data(context, "weight")
        activity_level = self.get_user_data(context, "activity_level")
        waist = self.get_user_data(context, "waist")
        neck = self.get_user_data(context, "neck")
        hip = self.get_user_data(context, "hip") if user.sex.lower() == "женский" else None

        # Рассчитываем процент жира
        body_fat = calculate_body_fat(
            sex=user.sex,
            waist=waist,
            neck=neck,
            hip=hip,
            height=user.height
        )

        # Создаем новую запись
        record = UserRecord(
            user_id=user.id,
            weight=weight,
            activity_level=activity_level,
            waist=waist,
            neck=neck,
            hip=hip,
            body_fat=body_fat
        )

        try:
            self.session.add(record)
            await self.session.commit()

            await self.send_message(
                update,
                f"✅ Данные обновлены!\n\n"
                f"Вес: {weight} кг\n"
                f"Уровень активности: {activity_level}\n"
                f"Талия: {waist} см\n"
                f"Шея: {neck} см"
                + (f"\nБёдра: {hip} см" if hip else "")
                + f"\nПроцент жира: {body_fat:.1f}%"
            )
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating metrics: {str(e)}", exc_info=True)
            raise

        return ConversationHandler.END

def get_update_metrics_handler() -> ConversationHandler:
    """Get the update metrics conversation handler."""
    handler = UpdateMetricsHandler()
    return ConversationHandler(
        entry_points=[handler.start_update_metrics],
        states={
            UserStates.WAITING_FOR_UPDATE_WEIGHT: [
                handler.handle_update_weight
            ],
            UserStates.WAITING_FOR_UPDATE_ACTIVITY: [
                handler.handle_update_activity
            ],
            UserStates.WAITING_FOR_UPDATE_WAIST: [
                handler.handle_update_waist
            ],
            UserStates.WAITING_FOR_UPDATE_NECK: [
                handler.handle_update_neck
            ],
            UserStates.WAITING_FOR_UPDATE_HIP: [
                handler.handle_update_hip
            ]
        },
        fallbacks=[]
    )
