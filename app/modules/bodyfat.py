from telegram import Update
from telegram.ext import (
    ContextTypes, ConversationHandler,
    CallbackQueryHandler, MessageHandler, filters
)
from datetime import datetime
from math import log10

from app.handlers.base import BaseHandler
from app.handlers.fsm_states import UserStates
from app.db.models import User, UserRecord
from app.utils.validation import ValidationError
from app.utils.logging import get_logger

from app.modules.kbju import calculate_kbju
from app.modules.my_data import show_user_summary
from app.modules.invite import send_consultation_invite
from app.modules.goals import show_goal_analysis, show_goal_kbju

logger = get_logger(__name__)

class BodyFatHandler(BaseHandler):
    """Handler for body fat calculations."""

    # Константы для расчетов
    BODYFAT_CONSTANTS = {
        "male": {
            "a": 495,
            "b": 1.0324,
            "c": 0.19077,
            "d": 0.15456
        },
        "female": {
            "a": 495,
            "b": 1.29579,
            "c": 0.35004,
            "d": 0.22100
        }
    }

    def __init__(self):
        super().__init__()
        self.handler = ConversationHandler(
            entry_points=[CallbackQueryHandler(self.start_body_fat_calc, pattern="^measure_fat$")],
            states={
                UserStates.WAITING_FOR_WAIST: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_waist)
                ],
                UserStates.WAITING_FOR_NECK: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_neck)
                ],
                UserStates.WAITING_FOR_HIPS: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_hips)
                ],
            },
            fallbacks=[]
        )

    @BaseHandler.handle_errors
    async def start_body_fat_calc(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Начало расчета процента жира"""
        user = await self.get_user(update.effective_user.id)
        if not user or not user.sex or not user.height:
            await self.send_message(
                update,
                "❌ <b>Сначала пройди анкету</b> с помощью команды /start.",
                parse_mode="HTML"
            )
            return ConversationHandler.END

        self.set_user_data(context, "bodyfat", {
            "sex": user.sex,
            "height": user.height
        })

        await self.send_message(
            update,
            "📏 <b>Введи обхват талии</b> (в см):",
            parse_mode="HTML"
        )
        return UserStates.WAITING_FOR_WAIST

    @BaseHandler.handle_errors
    async def handle_waist(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Обработка ввода обхвата талии"""
        try:
            waist = float(update.message.text.strip())
            if not 30 <= waist <= 200:
                raise ValidationError("Обхват талии должен быть от 30 до 200 см")

            bodyfat_data = self.get_user_data(context, "bodyfat", {})
            bodyfat_data["waist"] = waist
            self.set_user_data(context, "bodyfat", bodyfat_data)

            await self.send_message(
                update,
                "📏 <b>Введи обхват шеи</b> (в см):",
                parse_mode="HTML"
            )
            return UserStates.WAITING_FOR_NECK
        except ValueError:
            await self.send_message(
                update,
                "❌ Введите корректное число"
            )
            return UserStates.WAITING_FOR_WAIST
        except ValidationError as e:
            await self.send_message(update, f"❌ {str(e)}")
            return UserStates.WAITING_FOR_WAIST

    @BaseHandler.handle_errors
    async def handle_neck(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Обработка ввода обхвата шеи"""
        try:
            neck = float(update.message.text.strip())
            if not 20 <= neck <= 100:
                raise ValidationError("Обхват шеи должен быть от 20 до 100 см")

            bodyfat_data = self.get_user_data(context, "bodyfat", {})
            bodyfat_data["neck"] = neck
            self.set_user_data(context, "bodyfat", bodyfat_data)

            if bodyfat_data.get("sex") == "женский":
                await self.send_message(
                    update,
                    "📏 <b>Введи обхват бёдер</b> (в см):",
                    parse_mode="HTML"
                )
                return UserStates.WAITING_FOR_HIPS

            return await self.calculate_body_fat(update, context)
        except ValueError:
            await self.send_message(
                update,
                "❌ Введите корректное число"
            )
            return UserStates.WAITING_FOR_NECK
        except ValidationError as e:
            await self.send_message(update, f"❌ {str(e)}")
            return UserStates.WAITING_FOR_NECK

    @BaseHandler.handle_errors
    async def handle_hips(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Обработка ввода обхвата бедер"""
        try:
            hips = float(update.message.text.strip())
            if not 30 <= hips <= 200:
                raise ValidationError("Обхват бёдер должен быть от 30 до 200 см")

            bodyfat_data = self.get_user_data(context, "bodyfat", {})
            bodyfat_data["hips"] = hips
            self.set_user_data(context, "bodyfat", bodyfat_data)

            return await self.calculate_body_fat(update, context)
        except ValueError:
            await self.send_message(
                update,
                "❌ Введите корректное число"
            )
            return UserStates.WAITING_FOR_HIPS
        except ValidationError as e:
            await self.send_message(update, f"❌ {str(e)}")
            return UserStates.WAITING_FOR_HIPS

    def calculate_body_fat_percentage(self, sex: str, height: float, waist: float, neck: float, hips: float = None) -> float:
        """
        Расчет процента жира в организме.
        
        Args:
            sex: Пол пользователя
            height: Рост в см
            waist: Обхват талии в см
            neck: Обхват шеи в см
            hips: Обхват бедер в см (только для женщин)
            
        Returns:
            float: Процент жира
            
        Raises:
            ValidationError: Если данные некорректны
        """
        try:
            constants = self.BODYFAT_CONSTANTS["female" if sex == "женский" else "male"]
            
            if sex == "мужской":
                bodyfat = constants["a"] / (constants["b"] - constants["c"] * log10(waist - neck) + constants["d"] * log10(height)) - 450
            else:
                if not hips:
                    raise ValidationError("Для женщин необходимо указать обхват бёдер")
                bodyfat = constants["a"] / (constants["b"] - constants["c"] * log10(waist + hips - neck) + constants["d"] * log10(height)) - 450
            
            return round(max(bodyfat, 0), 2)
        except Exception as e:
            logger.error(f"Ошибка при расчете процента жира: {str(e)}")
            raise ValidationError(f"Ошибка при расчете процента жира: {str(e)}")

    @BaseHandler.handle_errors
    async def calculate_body_fat(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Расчет и сохранение процента жира"""
        data = self.get_user_data(context, "bodyfat", {})
        sex = data["sex"]
        height = data["height"]
        waist = data["waist"]
        neck = data["neck"]
        hips = data.get("hips")

        bodyfat = self.calculate_body_fat_percentage(sex, height, waist, neck, hips)

        user = await self.get_user(update.effective_user.id)
        record = await self.get_or_create_today_record(user.id)

        # Сохраняем измерения
        record.body_fat = bodyfat
        record.waist = waist
        record.neck = neck
        if hips is not None:
            record.hip = hips

        # Рассчитываем КБЖУ
        from app.modules.kbju import KBJUHandler
        kbju_handler = KBJUHandler()
        await kbju_handler.calculate_kbju(update, context, user, record)

        # Показываем результаты
        from app.modules.my_data import MyDataHandler
        my_data_handler = MyDataHandler()
        await my_data_handler.show_user_summary(update, context, skip_kbju=True)

        from app.modules.goals import GoalsHandler
        goals_handler = GoalsHandler()
        await goals_handler.show_goal_analysis(update, context, user, record)
        await goals_handler.show_goal_kbju(update, context, user, record)

        # Отправляем приглашение на консультацию
        from app.modules.invite import InviteHandler
        invite_handler = InviteHandler()
        await invite_handler.send_consultation_invite(update, context)

        return ConversationHandler.END

def get_bodyfat_handler() -> ConversationHandler:
    """Get the body fat conversation handler."""
    handler = BodyFatHandler()
    return handler.handler
