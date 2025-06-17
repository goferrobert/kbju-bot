# 📦 Модуль: modules/user.py
# Отвечает за анкету пользователя и повторное редактирование через /edit

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes, ConversationHandler, MessageHandler,
    CommandHandler, CallbackQueryHandler, filters
)
from datetime import datetime
from app.db.crud import get_user_by_telegram_id, create_user, update_user
from app.ui.keyboards import menu_callback_handler
from app.modules.first_touch import after_form_finished
from app.core.validators import (
    validate_name, validate_birthday, validate_height, validate_sex
)
from app.core.errors import ValidationError, DatabaseError
from app.core.states import (
    BASIC_NAME, BASIC_BIRTHDAY, BASIC_HEIGHT, BASIC_SEX
)
from app.core.handlers import BaseHandler
from core.logging import get_logger

logger = get_logger(__name__)

class UserHandler(BaseHandler):
    """
    Обработчик пользовательских данных
    """
    def __init__(self):
        super().__init__()
        self.handler = ConversationHandler(
            entry_points=[
                CommandHandler("start", self.handle_user_start),
                CommandHandler("edit", self.handle_user_edit),
            ],
            states={
                BASIC_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_basic_name)],
                BASIC_BIRTHDAY: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_basic_birthday)],
                BASIC_HEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_basic_height)],
                BASIC_SEX: [CallbackQueryHandler(self.handle_basic_sex_callback, pattern=r"^sex_")],
            },
            fallbacks=[],
        )

    @BaseHandler.handle_errors
    async def handle_user_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        telegram_id = update.effective_user.id
        user = get_user_by_telegram_id(telegram_id)

        if user is None:
            context.user_data["flow"] = "first_touch"
            return await self.start_user_form(update, context)

        if not self.get_user_data(context, "skip_registered_message"):
            await self.send_message(update, "🎉 Поздравляем, ты уже зарегистрирован!")
        from app.ui.menu import send_main_menu
        await send_main_menu(update, context)
        return ConversationHandler.END

    @BaseHandler.handle_errors
    async def handle_user_edit(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /edit"""
        await self.send_message(update, "✏️ Повторный запуск анкеты.")
        return await self.start_user_form(update, context)

    @BaseHandler.handle_errors
    async def start_user_form(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начало заполнения анкеты"""
        await self.send_message(
            update,
            "👋 Давай начнём с основного.\nКак тебя зовут? (ФИО или просто имя)",
            parse_mode="HTML"
        )
        return BASIC_NAME

    @BaseHandler.handle_errors
    async def handle_basic_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка ввода имени"""
        try:
            first_name, last_name = validate_name(update.message.text)
            self.set_user_data(context, "first_name", first_name)
            self.set_user_data(context, "last_name", last_name)
            self.set_user_data(context, "name", update.message.text.strip())
            await self.send_message(update, "📅 Укажи дату рождения (в формате ДД.ММ.ГГГГ):", parse_mode="HTML")
            return BASIC_BIRTHDAY
        except ValidationError as e:
            await self.send_message(update, f"❌ {e.message}", parse_mode="HTML")
            return BASIC_NAME

    @BaseHandler.handle_errors
    async def handle_basic_birthday(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка ввода даты рождения"""
        try:
            birthday = validate_birthday(update.message.text)
            self.set_user_data(context, "birthday", birthday)
            await self.send_message(update, "📏 Укажи свой рост (в см):", parse_mode="HTML")
            return BASIC_HEIGHT
        except ValidationError as e:
            await self.send_message(update, f"❌ {e.message}", parse_mode="HTML")
            return BASIC_BIRTHDAY

    @BaseHandler.handle_errors
    async def handle_basic_height(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка ввода роста"""
        try:
            height = validate_height(update.message.text)
            self.set_user_data(context, "height", height)
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("мужской", callback_data="sex_мужской")],
                [InlineKeyboardButton("женский", callback_data="sex_женский")]
            ])
            await self.send_message(update, "🚻 Укажи пол:", reply_markup=keyboard)
            return BASIC_SEX
        except ValidationError as e:
            await self.send_message(update, f"❌ {e.message}", parse_mode="HTML")
            return BASIC_HEIGHT

    async def save_user_data(self, telegram_user, context: ContextTypes.DEFAULT_TYPE, sex: str):
        """Сохранение данных пользователя"""
        try:
            existing_user = get_user_by_telegram_id(telegram_user.id)
            if existing_user:
                update_user(
                    telegram_user.id,
                    telegram_user.username,
                    self.get_user_data(context, "first_name", ""),
                    self.get_user_data(context, "last_name", None),
                    self.get_user_data(context, "name", telegram_user.full_name),
                    sex,
                    self.get_user_data(context, "birthday"),
                    self.get_user_data(context, "height")
                )
                return "✅ Данные обновлены!"
            else:
                create_user(
                    telegram_id=telegram_user.id,
                    username=telegram_user.username,
                    first_name=self.get_user_data(context, "first_name", ""),
                    last_name=self.get_user_data(context, "last_name", None),
                    name=self.get_user_data(context, "name", telegram_user.full_name),
                    sex=sex,
                    date_of_birth=self.get_user_data(context, "birthday"),
                    height=self.get_user_data(context, "height")
                )
                return "✅ Анкета сохранена!"
        except Exception as e:
            self.logger.error(f"Error saving user data: {str(e)}", exc_info=True)
            raise DatabaseError("Ошибка при сохранении данных", telegram_user.id)

    @BaseHandler.handle_errors
    async def handle_basic_sex_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка выбора пола"""
        query = update.callback_query
        await query.answer()
        
        try:
            sex = validate_sex(query.data.split("_")[1])
            self.set_user_data(context, "sex", sex)
            telegram_user = update.effective_user

            message = await self.save_user_data(telegram_user, context, sex)
            await query.message.edit_text(message, parse_mode="HTML")

            if self.get_user_data(context, "flow") == "first_touch":
                await after_form_finished(update, context)
                return ConversationHandler.END

            from app.ui.menu import send_main_menu
            await send_main_menu(update, context)
            return ConversationHandler.END
        except ValidationError as e:
            await query.message.reply_text(f"❌ {e.message}", parse_mode="HTML")
            return BASIC_SEX

# Создаем экземпляр обработчика
user_handler = UserHandler()
user_flow_handler = user_handler.handler
menu_handler = menu_callback_handler()
