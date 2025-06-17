from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from datetime import date, datetime

from app.handlers.base import BaseHandler
from app.handlers.fsm_states import UserStates
from app.db.models import User, UserRecord
from app.utils.validation import ValidationError
from app.utils.logging import get_logger
from app.utils.calculations import calculate_kbju

logger = get_logger(__name__)

class GoalsHandler(BaseHandler):
    """Handler for user goals and analysis."""

    # Константы для целей
    GOALS = {
        "Нормальное тело": {
            "male": {"min": 0, "max": 25},
            "female": {"min": 0, "max": 32},
            "description": "Достижение здорового процента жира",
            "recommendations": [
                "Сбалансированное питание",
                "Регулярные тренировки",
                "Постепенное снижение веса"
            ],
            "nutrition": [
                "Создайте дефицит калорий",
                "Следите за балансом БЖУ",
                "Пейте достаточно воды"
            ]
        },
        "Спортивное тело": {
            "male": {"min": 15, "max": 25},
            "female": {"min": 21, "max": 32},
            "description": "Развитие мышечной массы",
            "recommendations": [
                "Повышенное потребление белка",
                "Силовые тренировки",
                "Достаточный отдых"
            ],
            "nutrition": [
                "Поддерживайте калории",
                "Увеличьте потребление белка",
                "Следите за качеством пищи"
            ]
        },
        "Сухое тело": {
            "male": {"min": 0, "max": 15},
            "female": {"min": 0, "max": 21},
            "description": "Максимальная рельефность",
            "recommendations": [
                "Строгий контроль питания",
                "Интенсивные тренировки",
                "Регулярные замеры"
            ],
            "nutrition": [
                "Создайте небольшой дефицит",
                "Увеличьте потребление белка",
                "Контролируйте углеводы"
            ]
        }
    }

    def __init__(self):
        super().__init__()

    def calculate_age(self, birth_date: datetime) -> int:
        """
        Расчет возраста пользователя.
        
        Args:
            birth_date: Дата рождения
            
        Returns:
            int: Возраст в годах
        """
        today = datetime.now()
        age = today.year - birth_date.year
        if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
            age -= 1
        return age

    def determine_goal(self, sex: str, body_fat: float) -> str:
        """
        Определение цели на основе пола и процента жира.
        
        Args:
            sex: Пол пользователя
            body_fat: Процент жира
            
        Returns:
            str: Название цели
        """
        sex_key = "female" if sex.lower() == "женский" else "male"
        
        for goal, data in self.GOALS.items():
            if data[sex_key]["min"] <= body_fat <= data[sex_key]["max"]:
                return goal
                
        # Если не попали ни в один диапазон, возвращаем ближайшую цель
        if sex_key == "male":
            return "Нормальное тело" if body_fat > 25 else "Сухое тело"
        else:
            return "Нормальное тело" if body_fat > 32 else "Сухое тело"

    @BaseHandler.handle_errors
    async def show_goal_analysis(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user: User = None, record: UserRecord = None) -> int:
        """
        Показ анализа целей на основе процента жира.
        
        Args:
            update: Объект обновления Telegram
            context: Контекст обновления
            user: Пользователь (опционально)
            record: Запись пользователя (опционально)
            
        Returns:
            int: Следующее состояние
        """
        if not user:
            user = await self.get_user(update.effective_user.id)
        if not user:
            raise ValidationError("Пользователь не найден")

        if not record:
            record = await self.get_latest_record(user.id)
        if not record or not record.body_fat:
            await self.send_message(
                update,
                "Для анализа целей необходимо сначала обновить ваши метрики."
            )
            return ConversationHandler.END

        body_fat = record.body_fat
        goal = self.determine_goal(user.sex, body_fat)

        # Сохраняем цель
        user.goal = goal
        await self.session.commit()

        # Формируем сообщение
        goal_data = self.GOALS[goal]
        message = (
            f"📊 <b>Анализ вашего текущего состояния:</b>\n\n"
            f"Процент жира: <b>{body_fat:.1f}%</b>\n"
            f"Рекомендуемая цель: <b>{goal}</b>\n\n"
            f"🎯 <b>Ваша цель:</b> {goal_data['description']}\n"
            f"📝 <b>Рекомендации:</b>\n"
        )
        message += "\n".join(f"• {rec}" for rec in goal_data["recommendations"])

        keyboard = [[InlineKeyboardButton("Рассчитать КБЖУ", callback_data="calculate_kbju")]]
        await self.send_message(
            update,
            message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )
        return UserStates.WAITING_FOR_GOAL

    @BaseHandler.handle_errors
    async def show_goal_kbju(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user: User = None, record: UserRecord = None) -> int:
        """
        Показ расчета КБЖУ на основе цели пользователя.
        
        Args:
            update: Объект обновления Telegram
            context: Контекст обновления
            user: Пользователь (опционально)
            record: Запись пользователя (опционально)
            
        Returns:
            int: Следующее состояние
        """
        query = update.callback_query
        await query.answer()

        if not user:
            user = await self.get_user(update.effective_user.id)
        if not user:
            raise ValidationError("Пользователь не найден")

        if not record:
            record = await self.get_latest_record(user.id)
        if not record:
            await self.send_message(
                update,
                "Для расчета КБЖУ необходимо сначала обновить ваши метрики."
            )
            return ConversationHandler.END

        # Рассчитываем КБЖУ
        kbju = calculate_kbju(
            weight=record.weight,
            height=user.height,
            age=self.calculate_age(user.date_of_birth),
            sex=user.sex,
            activity_level=record.activity_level,
            goal=user.goal
        )

        # Сохраняем КБЖУ
        record.calories = kbju["calories"]
        record.protein = kbju["protein"]
        record.fat = kbju["fat"]
        record.carbs = kbju["carbs"]
        await self.session.commit()

        # Формируем сообщение
        goal_data = self.GOALS[user.goal]
        message = (
            f"🍽 <b>Ваше КБЖУ для цели '{user.goal}':</b>\n\n"
            f"Калории: <b>{kbju['calories']}</b> ккал\n"
            f"Белки: <b>{kbju['protein']}</b> г\n"
            f"Жиры: <b>{kbju['fat']}</b> г\n"
            f"Углеводы: <b>{kbju['carbs']}</b> г\n\n"
            f"📝 <b>Рекомендации по питанию:</b>\n"
        )
        message += "\n".join(f"• {rec}" for rec in goal_data["nutrition"])

        await self.send_message(
            update,
            message,
            parse_mode="HTML"
        )
        return ConversationHandler.END

def get_goals_handler() -> ConversationHandler:
    """Get the goals conversation handler."""
    handler = GoalsHandler()
    return ConversationHandler(
        entry_points=[handler.show_goal_analysis],
        states={
            UserStates.WAITING_FOR_GOAL: [
                handler.show_goal_kbju
            ]
        },
        fallbacks=[]
    )

# Создаем экземпляр обработчика
goals_handler = GoalsHandler()
