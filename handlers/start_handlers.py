from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
import logging

from states.fsm_states import UserInfoStates
from utils.texts import get_welcome_text, get_funnel_text_with_image
from utils.buttons import get_start_keyboard, get_funnel_keyboard, get_main_menu_inline_keyboard
from utils.calculations import calculate_bodyfat, calculate_kbju
from crud.user_crud import create_user, get_user
from utils.validators import validate_name, validate_birthday, validate_height, validate_weight, validate_measurement
from models.database import SessionLocal

async def cmd_start(message: types.Message, state: FSMContext):
    """Обработчик команды /start"""
    logging.info(f"cmd_start: user={message.from_user.id}")
    await state.finish()
    
    # Проверяем, есть ли уже пользователь
    db = SessionLocal()
    user = get_user(db, message.from_user.id)
    db.close()
    
    if user:
        # Пользователь уже есть - показываем только меню и сообщение
        await message.answer(
            'Вы уже зарегистрированы! Можете добавить новые замеры или воспользоваться меню.',
            reply_markup=get_main_menu_inline_keyboard()
        )
    else:
        # Новый пользователь - показываем приветствие
        await message.answer(
            get_welcome_text(),
            reply_markup=get_start_keyboard()
        )

async def start_survey_callback(callback: types.CallbackQuery, state: FSMContext):
    """Обработчик начала анкеты"""
    logging.info(f"start_survey_callback: user={callback.from_user.id}")
    await callback.answer()
    
    # Сохраняем выбор пользователя
    await callback.message.edit_text(
        f"{callback.message.text}\n\n✅ Выбрано: Начать тестирование"
    )
    
    from handlers.user_info_handlers import ask_name
    await ask_name(callback.message, state)

async def cmd_data(message: types.Message, state: FSMContext):
    """Обработчик команды /data - показывает воронку с фото"""
    logging.info(f"cmd_data: user={message.from_user.id}")
    await state.finish()
    
    with open('data/1.jpg', 'rb') as photo:
        await message.answer_photo(
            photo=photo,
            caption=get_funnel_text_with_image(),
            reply_markup=get_funnel_keyboard(),
            parse_mode='Markdown'
        )

def register_start_handlers(dp: Dispatcher):
    """Регистрация обработчиков старта"""
    dp.register_message_handler(cmd_start, commands=['start'])
    dp.register_message_handler(cmd_data, commands=['data'])
    dp.register_callback_query_handler(start_survey_callback, text='start_survey') 