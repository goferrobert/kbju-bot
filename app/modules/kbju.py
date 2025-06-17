from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler
from app.handlers.base import BaseHandler
from app.handlers.fsm_states import UserStates
from app.db.models import User, UserRecord
from app.utils.validation import ValidationError
from app.utils.logging import get_logger

logger = get_logger(__name__)

class KBJUHandler(BaseHandler):
    """Handler for KBJU calculations."""

    # Константы для расчетов
    CALORIE_MULTIPLIERS = {
        "fat_loss": 0.85,
        "mass_gain": 1.10,
        "recomposition": 0.95
    }

    PROTEIN_PER_KG = 2.0
    FAT_PER_KG = 1.0
    CALORIES_PER_GRAM = {
        "protein": 4,
        "fat": 9,
        "carbs": 4
    }

    def __init__(self):
        super().__init__()
        self.handler = ConversationHandler(
            entry_points=[],  # Подключи в main: CommandHandler("kbju", self.handle_kbju_command)
            states={
                UserStates.WAITING_FOR_GOAL: [
                    CallbackQueryHandler(self.handle_kbju_goal, pattern="^goal_")
                ],
            },
            fallbacks=[]
        )

    @BaseHandler.handle_errors
    async def calculate_kbju(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user: User, record: UserRecord) -> dict:
        """
        Расчет КБЖУ на основе данных пользователя.
        
        Args:
            update: Объект обновления Telegram
            context: Контекст обновления
            user: Объект пользователя
            record: Запись с текущими данными
            
        Returns:
            dict: Рассчитанные значения КБЖУ
        """
        try:
            weight = record.weight
            height = user.height
            age = (record.created_at.year - user.date_of_birth.year)
            sex = user.sex
            activity = record.activity_level or 1.3

            if not all([weight, height, age, sex]):
                raise ValidationError("Недостаточно данных для расчета КБЖУ")

            # Расчет базового метаболизма
            if sex == "мужской":
                bmr = 10 * weight + 6.25 * height - 5 * age + 5
            else:
                bmr = 10 * weight + 6.25 * height - 5 * age - 161

            calories = bmr * activity

            # Корректировка по цели
            goal = user.goal
            if goal and goal in self.CALORIE_MULTIPLIERS:
                calories *= self.CALORIE_MULTIPLIERS[goal]

            # Расчет белков и жиров
            protein = self.PROTEIN_PER_KG * weight
            fat = self.FAT_PER_KG * weight

            # Расчет углеводов
            kcal_from_protein = protein * self.CALORIES_PER_GRAM["protein"]
            kcal_from_fat = fat * self.CALORIES_PER_GRAM["fat"]
            remaining_kcal = calories - (kcal_from_protein + kcal_from_fat)
            carbs = max(0, remaining_kcal / self.CALORIES_PER_GRAM["carbs"])

            kbju = {
                "calories": round(calories),
                "protein": round(protein),
                "fat": round(fat),
                "carbs": round(carbs)
            }

            # Сохраняем результаты в запись
            record.calories = kbju["calories"]
            record.protein = kbju["protein"]
            record.fat = kbju["fat"]
            record.carbs = kbju["carbs"]
            await self.session.commit()

            # Отправляем сообщение с результатами
            await self.send_message(
                update,
                f"<b>📌 КБЖУ для цели '{goal.replace('_', ' ')}':</b>\n"
                f"🔥 Калории: <b>{kbju['calories']}</b>\n"
                f"🥩 Белки: <b>{kbju['protein']} г</b>\n"
                f"🧈 Жиры: <b>{kbju['fat']} г</b>\n"
                f"🍞 Углеводы: <b>{kbju['carbs']} г</b>",
                parse_mode="HTML"
            )

            return kbju

        except Exception as e:
            logger.error(f"Ошибка при расчете КБЖУ: {str(e)}")
            raise ValidationError(f"Ошибка при расчете КБЖУ: {str(e)}")

    @BaseHandler.handle_errors
    async def handle_kbju_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Обработчик команды /kbju"""
        user = await self.get_user(update.effective_user.id)
        if not user:
            await self.send_message(
                update,
                "❌ Сначала нужно зарегистрироваться. Используйте /start"
            )
            return ConversationHandler.END

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔥 Снижение жира", callback_data="goal_fat_loss")],
            [InlineKeyboardButton("📈 Набор массы", callback_data="goal_mass_gain")],
            [InlineKeyboardButton("⚖️ Рекомпозиция", callback_data="goal_recomposition")]
        ])
        await self.send_message(
            update,
            "🎯 <b>Выбери свою цель:</b>",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        return UserStates.WAITING_FOR_GOAL

    @BaseHandler.handle_errors
    async def handle_kbju_goal(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Обработчик выбора цели для КБЖУ"""
        query = update.callback_query
        await query.answer()

        goal = query.data.replace("goal_", "")
        if goal not in self.CALORIE_MULTIPLIERS:
            raise ValidationError("Неверная цель")

        user = await self.get_user(update.effective_user.id)
        if not user:
            raise ValidationError("Пользователь не найден")

        record = await self.get_or_create_today_record(user.id)
        await self.calculate_kbju(update, context, user, record)

        return ConversationHandler.END

def get_kbju_handler() -> ConversationHandler:
    """Get the KBJU conversation handler."""
    handler = KBJUHandler()
    return handler.handler
