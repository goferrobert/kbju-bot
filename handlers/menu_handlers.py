from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
import logging

from utils.texts import get_main_menu_text
from utils.buttons import get_main_menu_inline_keyboard
from crud.user_crud import get_user
from utils.calculations import calculate_bodyfat, calculate_kbju
from utils.progress import create_progress_graph
from models.database import SessionLocal
from handlers.food_handlers import start_food_preferences
from handlers.measurements_handlers import start_new_measurements

async def start_new_measurements_wrapper(user_id: int, state: FSMContext):
    """Обертка для start_new_measurements"""
    from main import bot
    from aiogram import types
    
    # Создаем фейковое сообщение для совместимости
    class FakeMessage:
        def __init__(self, user_id):
            self.from_user = types.User(id=user_id, is_bot=False, first_name="User")
            self.answer = lambda text, **kwargs: bot.send_message(user_id, text, **kwargs)
    
    fake_message = FakeMessage(user_id)
    await start_new_measurements(fake_message, state)

async def start_food_preferences_wrapper(user_id: int, state: FSMContext):
    """Обертка для start_food_preferences"""
    from main import bot
    from aiogram import types
    
    # Создаем фейковое сообщение для совместимости
    class FakeMessage:
        def __init__(self, user_id):
            self.from_user = types.User(id=user_id, is_bot=False, first_name="User")
            self.answer = lambda text, **kwargs: bot.send_message(user_id, text, **kwargs)
    
    fake_message = FakeMessage(user_id)
    await start_food_preferences(fake_message, state)

async def show_main_menu(message: types.Message, state: FSMContext):
    """Показать главное меню"""
    logging.info(f"show_main_menu: user={message.from_user.id}")
    await state.finish()
    
    db = SessionLocal()
    user = get_user(db, message.from_user.id)
    db.close()
    
    if not user:
        await message.answer("❌ Сначала пройдите анкету! Используйте /start")
        return
    
    await message.answer(get_main_menu_text(), reply_markup=get_main_menu_inline_keyboard())

async def show_my_data(message: types.Message, state: FSMContext):
    """Показать данные пользователя"""
    try:
        # Получаем user_id из message или напрямую
        if hasattr(message, 'from_user') and hasattr(message.from_user, 'id'):
            user_id = message.from_user.id
        else:
            user_id = message  # Если передали user_id напрямую
        
        db = SessionLocal()
        user = get_user(db, user_id)
        db.close()
        
        if not user:
            # Определяем, как отправить сообщение
            if hasattr(message, 'answer'):
                await message.answer("❌ Сначала пройдите анкету! Используйте /start")
            else:
                # Если это user_id, нужно отправить через bot
                from main import bot
                await bot.send_message(user_id, "❌ Сначала пройдите анкету! Используйте /start")
            return
        
        # Получаем последнюю запись для расчета процента жира и отображения динамики
        db = SessionLocal()
        from crud.record_crud import get_latest_record
        latest_record = get_latest_record(db, user_id)
        db.close()
        
        if latest_record:
            user_data = {
                'sex': user.sex,
                'height': latest_record.height,
                'weight': latest_record.weight,
                'waist': latest_record.waist,
                'neck': latest_record.neck,
                'hip': latest_record.hip,
                'steps': latest_record.steps,
                'sport_type': latest_record.sport_type,
                'sport_freq': latest_record.sport_freq,
                'goal': latest_record.goal
            }
            bodyfat = calculate_bodyfat(user_data)
        else:
            bodyfat = 0
        
        # Форматируем данные активности
        sport_names = {
            'none': '❌ Не занимаюсь',
            'walking': '🚶 Ходьба/Прогулки',
            'running': '🏃 Бег/Кардио',
            'strength': '🏋️ Тренажерный зал',
            'yoga': '🧘 Йога/Пилатес',
            'swimming': '🏊 Плавание',
            'cycling': '🚴 Велосипед',
            'team': '⚽ Футбол/Баскетбол'
        }
        
        goal_names = {
            'healthy': '🧘 Здоровое тело',
            'athletic': '🏋 Спортивное тело',
            'lean': '🔥 Сухое тело'
        }
        
        text = f"""📊 **Ваши данные**

👤 **Основная информация:**
• Имя: {user.first_name}
• Дата рождения: {user.date_of_birth}
• Пол: {'Мужской' if user.sex == 'male' else 'Женский'}
• Рост: {latest_record.height if latest_record else 'Не указано'} см

🏃‍♂️ **Активность:**
• Шаги в день: {latest_record.steps if latest_record else 'Не указано'}
• Спорт: {sport_names.get(latest_record.sport_type, 'Не указано') if latest_record else 'Не указано'}
• Частота: {latest_record.sport_freq if latest_record else 'Не указано'} раз в неделю

📐 **Последние замеры:**
• Вес: {latest_record.weight if latest_record else 'Не указано'} кг
• Талия: {latest_record.waist if latest_record else 'Не указано'} см
• Шея: {latest_record.neck if latest_record else 'Не указано'} см"""

        if latest_record and latest_record.hip:
            text += f"\n• Бёдра: {latest_record.hip} см"
        
        text += f"""

🎯 **Цель:** {goal_names.get(latest_record.goal, 'Не указана') if latest_record else 'Не указана'}
🔥 **Процент жира:** {bodyfat:.1f}%"""
        
        # Определяем, как отправить сообщение
        if hasattr(message, 'answer'):
            await message.answer(text, parse_mode='Markdown')
        else:
            # Если это user_id, нужно отправить через bot
            from main import bot
            await bot.send_message(user_id, text, parse_mode='Markdown')
    except Exception as e:
        logging.error(f"show_my_data error: {e}")
        if hasattr(message, 'answer'):
            await message.answer("❌ Произошла ошибка при получении данных. Попробуйте позже.")
        else:
            from main import bot
            await bot.send_message(user_id, "❌ Произошла ошибка при получении данных. Попробуйте позже.")

async def show_progress(user_id: int, state: FSMContext):
    """Показать прогресс"""
    try:
        db = SessionLocal()
        user = get_user(db, user_id)
        db.close()
        
        if not user:
            from main import bot
            await bot.send_message(user_id, "❌ Сначала пройдите анкету! Используйте /start")
            return
        
        db = SessionLocal()
        from crud.record_crud import get_user_records
        records = get_user_records(db, user_id)
        db.close()
        
        if len(records) < 2:
            from main import bot
            await bot.send_message(user_id, "📈 Для отображения прогресса нужно минимум 2 записи. Сделайте новые замеры!")
            return
        
        # Сортируем записи по дате (старые -> новые для правильного анализа)
        records.sort(key=lambda x: x.date)
        
        # Получаем мотивационное сообщение
        from utils.progress import get_motivational_message
        motivational_text = get_motivational_message(records)
        
        # Отправляем мотивационное сообщение
        from main import bot
        await bot.send_message(user_id, motivational_text, parse_mode='Markdown')
        
        # Создаем график прогресса
        from utils.progress import create_progress_graph
        graph_path = create_progress_graph(records)
        
        if graph_path:
            with open(graph_path, 'rb') as photo:
                await bot.send_photo(
                    chat_id=user_id,
                    photo=photo,
                    caption="📈 Ваш график прогресса"
                )
        else:
            await bot.send_message(user_id, "❌ Ошибка при создании графика прогресса")
    except Exception as e:
        logging.error(f"show_progress error: {e}")
        from main import bot
        await bot.send_message(user_id, "❌ Произошла ошибка при получении прогресса. Попробуйте позже.")

async def show_consultation(user_id: int, state: FSMContext):
    """Показать кнопку для консультации"""
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("💬 Написать специалисту", url="https://t.me/dryuzefovna")
    )
    
    from main import bot
    await bot.send_message(
        user_id,
        "💬 **Получить персональную консультацию**\n\n"
        "Нажмите кнопку ниже, чтобы связаться с профессиональным диетологом Екатериной Юзефовной.",
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

# Callback-обработчики для inline-меню
async def menu_callback_handler(callback: types.CallbackQuery, state: FSMContext):
    data = callback.data
    user_id = callback.from_user.id
    logging.info(f"menu_callback_handler: user={user_id}, data={data}")
    
    if data == "menu_my_data":
        await show_my_data(user_id, state)
    elif data == "menu_progress":
        await show_progress(user_id, state)
    elif data == "menu_new_measurements":
        await start_new_measurements_wrapper(user_id, state)
    elif data == "menu_food_prefs":
        await start_food_preferences_wrapper(user_id, state)
    elif data == "menu_consultation":
        await show_consultation(user_id, state)
    await callback.answer()

def register_menu_handlers(dp: Dispatcher):
    """Регистрация обработчиков главного меню"""
    dp.register_message_handler(show_main_menu, commands=["menu"])
    dp.register_callback_query_handler(menu_callback_handler, lambda c: c.data.startswith("menu_")) 