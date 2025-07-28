from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
import logging

from states.fsm_states import FoodStates
from utils.texts import get_food_preferences_text
from utils.buttons import get_main_menu_inline_keyboard, get_confirm_keyboard
from crud.user_crud import get_user, user_exists
from models.database import SessionLocal
from crud.food_crud import create_or_update_food_preferences, get_food_preferences

logging.basicConfig(filename='bot.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

async def start_food_preferences(message: types.Message, state: FSMContext):
    """Начать настройку пищевых предпочтений"""
    logging.info(f"start_food_preferences: user={message.from_user.id}")
    db = SessionLocal()
    user = get_user(db, message.from_user.id)
    if not user:
        db.close()
        await message.answer("❌ Сначала пройдите анкету! Используйте /start")
        return
    
    # Проверяем, есть ли уже предпочтения
    prefs = get_food_preferences(db, message.from_user.id)
    db.close()
    
    if prefs and (prefs.likes_raw or prefs.dislikes_raw):
        # Показываем текущие предпочтения с возможностью редактирования
        text = "🍎 **Ваши текущие предпочтения:**\n\n"
        if prefs.likes_raw:
            text += f"✅ **Любимые продукты:**\n{prefs.likes_raw}\n\n"
        if prefs.dislikes_raw:
            text += f"❌ **Нелюбимые продукты:**\n{prefs.dislikes_raw}\n\n"
        text += "Хотите отредактировать предпочтения?"
        
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            types.InlineKeyboardButton("✏️ Редактировать", callback_data="edit_preferences"),
            types.InlineKeyboardButton("❌ Отмена", callback_data="cancel_preferences")
        )
        
        await message.answer(text, parse_mode='Markdown', reply_markup=keyboard)
    else:
        # Начинаем создание новых предпочтений
        await message.answer("🍎 **Настройка пищевых предпочтений**\n\nДавайте начнем с ваших любимых продуктов:\n\n✅ **Что вы любите есть?**\n\nРасскажите о продуктах, которые вам нравятся (например: курица, овощи, фрукты, рыба, творог)")
        await FoodStates.likes.set()

async def process_likes(message: types.Message, state: FSMContext):
    """Обработать любимые продукты"""
    logging.info(f"process_likes: user={message.from_user.id}")
    likes = message.text.strip()
    
    if len(likes) < 5:
        await message.answer("❌ Пожалуйста, опишите ваши любимые продукты подробнее (минимум 5 символов)")
        return
    
    # Сохраняем любимые продукты
    await state.update_data(likes=likes)
    
    # Переходим к нелюбимым продуктам
    await message.answer("✅ Любимые продукты сохранены!\n\nТеперь расскажите о продуктах, которые вы не любите:\n\n❌ **Что вы не любите или не можете есть?**\n\nНапример: молоко, орехи, морепродукты, острые блюда")
    await FoodStates.dislikes.set()

async def process_dislikes(message: types.Message, state: FSMContext):
    """Обработать нелюбимые продукты"""
    logging.info(f"process_dislikes: user={message.from_user.id}")
    dislikes = message.text.strip()
    
    # Получаем данные из состояния
    data = await state.get_data()
    likes = data.get('likes', '')
    
    # Валидация нелюбимых продуктов (можно оставить пустым)
    if dislikes and len(dislikes) < 3:
        await message.answer("❌ Пожалуйста, опишите подробнее или оставьте пустым")
        return
    
    # Сохраняем предпочтения
    db = SessionLocal()
    create_or_update_food_preferences(db, message.from_user.id, likes_raw=likes, dislikes_raw=dislikes)
    db.close()
    
    await message.answer("✅ Ваши пищевые предпочтения сохранены!")
    await message.answer("🏠 Главное меню", reply_markup=get_main_menu_inline_keyboard())
    
    await state.finish()

async def show_food_preferences(message: types.Message, state: FSMContext):
    """Показать текущие пищевые предпочтения"""
    logging.info(f"show_food_preferences: user={message.from_user.id}")
    db = SessionLocal()
    user = get_user(db, message.from_user.id)
    if not user:
        db.close()
        await message.answer("❌ Сначала пройдите анкету! Используйте /start")
        return
    
    prefs = get_food_preferences(db, message.from_user.id)
    db.close()
    
    if prefs and (prefs.likes_raw or prefs.dislikes_raw):
        text = "🍎 **Ваши пищевые предпочтения:**\n\n"
        if prefs.likes_raw:
            text += f"✅ **Любимые продукты:**\n{prefs.likes_raw}\n\n"
        if prefs.dislikes_raw:
            text += f"❌ **Нелюбимые продукты:**\n{prefs.dislikes_raw}"
    else:
        text = "🍎 Пищевые предпочтения не указаны.\n\nНажмите кнопку '🍎 Предпочтения' для их настройки."
    
    await message.answer(text, parse_mode='Markdown', reply_markup=get_main_menu_inline_keyboard())

async def edit_preferences_callback(callback: types.CallbackQuery, state: FSMContext):
    """Обработчик кнопки редактирования предпочтений"""
    if callback.data == "edit_preferences":
        await callback.message.edit_text("🍎 **Редактирование предпочтений**\n\nДавайте начнем с ваших любимых продуктов:\n\n✅ **Что вы любите есть?**\n\nРасскажите о продуктах, которые вам нравятся (например: курица, овощи, фрукты, рыба, творог)")
        await FoodStates.likes.set()
    elif callback.data == "cancel_preferences":
        await callback.message.edit_text("❌ Редактирование отменено")
        await callback.message.answer("🏠 Главное меню", reply_markup=get_main_menu_inline_keyboard())
    
    await callback.answer()

def register_food_handlers(dp: Dispatcher):
    """Регистрация обработчиков пищевых предпочтений"""
    dp.register_message_handler(start_food_preferences, text="🍎 Предпочтения")
    dp.register_message_handler(show_food_preferences, text="🍎 Предпочтения")
    dp.register_message_handler(process_likes, state=FoodStates.likes)
    dp.register_message_handler(process_dislikes, state=FoodStates.dislikes)
    dp.register_callback_query_handler(edit_preferences_callback, lambda c: c.data in ["edit_preferences", "cancel_preferences"]) 