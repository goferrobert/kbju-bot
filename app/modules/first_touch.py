from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes, ConversationHandler, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters
)
from datetime import datetime

from app.handlers.base import BaseHandler
from app.handlers.fsm_states import UserStates
from app.db.models import User, UserRecord
from app.utils.validation import ValidationError
from app.utils.logging import get_logger

logger = get_logger(__name__)

class FirstTouchHandler(BaseHandler):
    """Handler for first user interaction."""

    STEP_LEVELS = {
        "low": "Менее 5000 шагов",
        "medium": "5000-10000 шагов",
        "high": "Более 10000 шагов"
    }

    SPORT_TYPES = {
        "yoga": ("Йога / Пилатес", 1.05),
        "cardio": ("Бег / Кардио", 1.10),
        "fitness": ("Фитнес / Зал", 1.20),
        "hiit": ("Кроссфит / HIIT", 1.30)
    }

    def __init__(self):
        super().__init__()
        self.handler = ConversationHandler(
            entry_points=[CommandHandler("start", self.start_first_touch)],
            states={
                UserStates.WAITING_FOR_NAME: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_name)
                ],
                UserStates.WAITING_FOR_BIRTHDAY: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_birthday)
                ],
                UserStates.WAITING_FOR_HEIGHT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_height)
                ],
                UserStates.WAITING_FOR_SEX: [
                    CallbackQueryHandler(self.handle_sex, pattern="^sex_")
                ],
                UserStates.WAITING_FOR_WEIGHT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_weight)
                ],
                UserStates.WAITING_FOR_STEPS: [
                    CallbackQueryHandler(self.handle_steps, pattern="^steps_")
                ],
                UserStates.WAITING_FOR_SPORT_YN: [
                    CallbackQueryHandler(self.handle_sport_yn, pattern="^sport_")
                ],
                UserStates.WAITING_FOR_SPORT_TYPE: [
                    CallbackQueryHandler(self.handle_sport_type, pattern="^sport_")
                ],
                UserStates.WAITING_FOR_SPORT_FREQ: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_sport_freq)
                ],
                UserStates.WAITING_FOR_WAIST: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_waist)
                ],
                UserStates.WAITING_FOR_GOAL: [
                    CallbackQueryHandler(self.handle_goal, pattern="^goal_")
                ]
            },
            fallbacks=[]
        )

    @BaseHandler.handle_errors
    async def start_first_touch(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start first interaction with user."""
        user = await self.get_user(update.effective_user.id)
        if user:
            await self.send_message(update, "🎉 Поздравляю, ты уже зарегистрирован!")
            from app.ui.menu import send_main_menu
            await send_main_menu(update, context)
            return ConversationHandler.END

        if not update.effective_user.username:
            await self.send_message(
                update,
                "❌ Для регистрации необходимо установить username в Telegram."
            )
            return ConversationHandler.END

        await self.send_message(
            update,
            "👋 <b>Привет!</b> Сейчас мы пройдём анкету. Это займёт не больше 1 минуты!",
            parse_mode="HTML"
        )
        await self.send_message(
            update,
            "👋 Давай начнём с основного.\nКак тебя зовут? (ФИО или просто имя)",
            parse_mode="HTML"
        )
        return UserStates.WAITING_FOR_NAME

    @BaseHandler.handle_errors
    async def handle_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle name input."""
        try:
            name = update.message.text.strip()
            if not name or len(name) < 2:
                raise ValidationError("Имя должно содержать минимум 2 символа")

            self.set_user_data(context, "name", name)
            await self.send_message(
                update,
                "📅 Введи дату рождения (дд.мм.гггг):"
            )
            return UserStates.WAITING_FOR_BIRTHDAY
        except ValidationError as e:
            await self.send_message(update, f"❌ {str(e)}")
            return UserStates.WAITING_FOR_NAME

    @BaseHandler.handle_errors
    async def handle_birthday(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle birthday input."""
        try:
            birthday = datetime.strptime(update.message.text.strip(), "%d.%m.%Y").date()
            if birthday > datetime.now().date():
                raise ValidationError("Дата рождения не может быть в будущем")

            self.set_user_data(context, "birthday", birthday)
            await self.send_message(
                update,
                "📏 Введи свой рост (в см):"
            )
            return UserStates.WAITING_FOR_HEIGHT
        except ValueError:
            await self.send_message(
                update,
                "❌ Введите дату в формате дд.мм.гггг"
            )
            return UserStates.WAITING_FOR_BIRTHDAY
        except ValidationError as e:
            await self.send_message(update, f"❌ {str(e)}")
            return UserStates.WAITING_FOR_BIRTHDAY

    @BaseHandler.handle_errors
    async def handle_height(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle height input."""
        try:
            height = float(update.message.text.strip())
            if not 100 <= height <= 250:
                raise ValidationError("Рост должен быть от 100 до 250 см")

            self.set_user_data(context, "height", height)
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("Мужской", callback_data="sex_male")],
                [InlineKeyboardButton("Женский", callback_data="sex_female")]
            ])
            await self.send_message(
                update,
                "👤 Выберите пол:",
                reply_markup=keyboard
            )
            return UserStates.WAITING_FOR_SEX
        except ValueError:
            await self.send_message(
                update,
                "❌ Введите корректное число"
            )
            return UserStates.WAITING_FOR_HEIGHT
        except ValidationError as e:
            await self.send_message(update, f"❌ {str(e)}")
            return UserStates.WAITING_FOR_HEIGHT

    @BaseHandler.handle_errors
    async def handle_sex(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle sex selection."""
        query = update.callback_query
        await query.answer()

        sex = query.data.split("_")[1]
        self.set_user_data(context, "sex", sex)

        await self.send_message(
            update,
            "⚖️ Введи свой вес в кг (например: 72.5):"
        )
        return UserStates.WAITING_FOR_WEIGHT

    @BaseHandler.handle_errors
    async def handle_weight(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle weight input."""
        try:
            weight = float(update.message.text.strip())
            if not 30 <= weight <= 300:
                raise ValidationError("Вес должен быть от 30 до 300 кг")

            self.set_user_data(context, "weight", weight)

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(level, callback_data=f"steps_{level_id}")]
                for level_id, level in self.STEP_LEVELS.items()
            ])
            await self.send_message(
                update,
                "📍 Сколько шагов вы проходите в день?",
                reply_markup=keyboard
            )
            return UserStates.WAITING_FOR_STEPS
        except ValueError:
            await self.send_message(
                update,
                "❌ Введите корректное число"
            )
            return UserStates.WAITING_FOR_WEIGHT
        except ValidationError as e:
            await self.send_message(update, f"❌ {str(e)}")
            return UserStates.WAITING_FOR_WEIGHT

    @BaseHandler.handle_errors
    async def handle_steps(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle steps selection."""
        query = update.callback_query
        await query.answer()

        step_level = query.data.split("_")[1]
        self.set_user_data(context, "step_level", step_level)

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Да", callback_data="sport_yes")],
            [InlineKeyboardButton("❌ Нет", callback_data="sport_no")]
        ])
        await self.send_message(
            update,
            "🏋️ Занимаетесь ли вы спортом?",
            reply_markup=keyboard
        )
        return UserStates.WAITING_FOR_SPORT_YN

    @BaseHandler.handle_errors
    async def handle_sport_yn(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle sport yes/no selection."""
        query = update.callback_query
        await query.answer()

        if query.data == "sport_no":
            self.set_user_data(context, "sport_type", "none")
            self.set_user_data(context, "sport_freq", 0)
            return await self.ask_waist(update, context)

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(desc, callback_data=f"sport_{type_}")]
            for type_, (desc, _) in self.SPORT_TYPES.items()
        ])
        await self.send_message(
            update,
            "💪 Какие тренировки вы выполняете?",
            reply_markup=keyboard
        )
        return UserStates.WAITING_FOR_SPORT_TYPE

    @BaseHandler.handle_errors
    async def handle_sport_type(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle sport type selection."""
        query = update.callback_query
        await query.answer()

        sport_type = query.data.split("_")[1]
        self.set_user_data(context, "sport_type", sport_type)
        self.set_user_data(context, "sport_multiplier", self.SPORT_TYPES[sport_type][1])

        await self.send_message(
            update,
            "📅 Сколько раз в неделю вы тренируетесь? (1-7)"
        )
        return UserStates.WAITING_FOR_SPORT_FREQ

    @BaseHandler.handle_errors
    async def handle_sport_freq(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle sport frequency input."""
        try:
            freq = int(update.message.text.strip())
            if not 1 <= freq <= 7:
                raise ValidationError("Частота должна быть от 1 до 7 раз в неделю")

            self.set_user_data(context, "sport_freq", freq)
            return await self.ask_waist(update, context)
        except ValueError:
            await self.send_message(
                update,
                "❌ Введите целое число"
            )
            return UserStates.WAITING_FOR_SPORT_FREQ
        except ValidationError as e:
            await self.send_message(update, f"❌ {str(e)}")
            return UserStates.WAITING_FOR_SPORT_FREQ

    @BaseHandler.handle_errors
    async def ask_waist(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Ask for waist measurement."""
        await self.send_message(
            update,
            "📏 Введи обхват талии (в см):"
        )
        return UserStates.WAITING_FOR_WAIST

    @BaseHandler.handle_errors
    async def handle_waist(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle waist measurement input."""
        try:
            waist = float(update.message.text.strip())
            if not 50 <= waist <= 200:
                raise ValidationError("Обхват талии должен быть от 50 до 200 см")

            self.set_user_data(context, "waist", waist)

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("Нормальное тело", callback_data="goal_normal")],
                [InlineKeyboardButton("Спортивное тело", callback_data="goal_athletic")],
                [InlineKeyboardButton("Сухое тело", callback_data="goal_lean")]
            ])
            await self.send_message(
                update,
                "🎯 Выберите вашу цель:",
                reply_markup=keyboard
            )
            return UserStates.WAITING_FOR_GOAL
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
    async def handle_goal(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle goal selection and finalize registration."""
        query = update.callback_query
        await query.answer()

        goal = query.data.split("_")[1]
        goal_map = {
            "normal": "Нормальное тело",
            "athletic": "Спортивное тело",
            "lean": "Сухое тело"
        }
        self.set_user_data(context, "goal", goal_map[goal])

        # Создаем пользователя
        user = User(
            telegram_id=update.effective_user.id,
            username=update.effective_user.username,
            name=self.get_user_data(context, "name"),
            sex=self.get_user_data(context, "sex"),
            date_of_birth=self.get_user_data(context, "birthday"),
            height=self.get_user_data(context, "height"),
            goal=self.get_user_data(context, "goal")
        )
        self.session.add(user)
        await self.session.commit()

        # Создаем первую запись
        record = UserRecord(
            user_id=user.id,
            weight=self.get_user_data(context, "weight"),
            waist=self.get_user_data(context, "waist"),
            step_level=self.get_user_data(context, "step_level"),
            sport_type=self.get_user_data(context, "sport_type"),
            sport_freq=self.get_user_data(context, "sport_freq")
        )
        self.session.add(record)
        await self.session.commit()

        # Рассчитываем КБЖУ
        from app.modules.kbju import KBJUHandler
        kbju_handler = KBJUHandler()
        await kbju_handler.calculate_kbju(update, context, user, record)

        # Рассчитываем процент жира
        from app.modules.bodyfat import BodyFatHandler
        bodyfat_handler = BodyFatHandler()
        await bodyfat_handler.calculate_bodyfat(update, context, user, record)

        # Показываем сводку
        from app.modules.my_data import MyDataHandler
        my_data_handler = MyDataHandler()
        await my_data_handler.show_user_summary(update, context)

        # Отправляем приглашение на консультацию
        from app.modules.invite import InviteHandler
        invite_handler = InviteHandler()
        await invite_handler.send_consultation_invite(update, context)

        return ConversationHandler.END

def get_first_touch_handler() -> ConversationHandler:
    """Get the first touch conversation handler."""
    handler = FirstTouchHandler()
    return handler.handler