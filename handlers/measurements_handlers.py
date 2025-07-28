from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from datetime import date, datetime
import logging

from models.database import SessionLocal
from crud.user_crud import get_user
from crud.record_crud import create_or_update_record, get_latest_record
from states.fsm_states import MeasurementsStates
from utils.texts import (
    get_weight_request, get_waist_request, get_neck_request, get_hip_request,
    get_validation_error, get_final_results_text, get_kbju_explanation
)
from utils.buttons import get_main_menu_inline_keyboard
from utils.validators import validate_weight, validate_measurement
from utils.calculations import calculate_bodyfat, calculate_kbju, calculate_step_multiplier

async def start_new_measurements(message: types.Message, state: FSMContext):
    """Начать новые измерения"""
    user_id = message.from_user.id
    logging.info(f"start_new_measurements: user_id={user_id}")
    
    # Сохраняем ID пользователя в состояние
    await state.update_data(user_id=user_id)
    
    await message.answer("📝 Давайте сделаем новые замеры!")
    await ask_waist_measurement(message, state)

async def ask_waist_measurement(message: types.Message, state: FSMContext):
    """Запросить измерение талии"""
    logging.info(f"ask_waist_measurement: user={message.from_user.id}")
    await message.answer(get_waist_request())
    await MeasurementsStates.waist.set()

async def process_waist_measurement(message: types.Message, state: FSMContext):
    """Обработать измерение талии"""
    waist = message.text.strip()
    logging.info(f"process_waist_measurement: user={message.from_user.id}, waist={waist}")
    from utils.validators import validate_waist_measurement
    if not validate_waist_measurement(waist):
        logging.warning(f"process_waist_measurement: user={message.from_user.id}, invalid waist={waist}")
        await message.answer(get_validation_error("Обхват талии должен быть числом от 50 до 200 см"))
        return
    await state.update_data(waist=float(waist))
    logging.info(f"process_waist_measurement: user={message.from_user.id}, waist accepted={waist}")
    await message.answer(f"✅ Обхват талии: {waist} см")
    await ask_neck_measurement(message, state)

async def ask_neck_measurement(message: types.Message, state: FSMContext):
    """Запросить измерение шеи"""
    logging.info(f"ask_neck_measurement: user={message.from_user.id}")
    await message.answer(get_neck_request())
    await MeasurementsStates.neck.set()

async def process_neck_measurement(message: types.Message, state: FSMContext):
    """Обработать измерение шеи"""
    neck = message.text.strip()
    logging.info(f"process_neck_measurement: user={message.from_user.id}, neck={neck}")
    from utils.validators import validate_neck_measurement
    if not validate_neck_measurement(neck):
        logging.warning(f"process_neck_measurement: user={message.from_user.id}, invalid neck={neck}")
        await message.answer(get_validation_error("Обхват шеи должен быть числом от 20 до 100 см"))
        return
    await state.update_data(neck=float(neck))
    logging.info(f"process_neck_measurement: user={message.from_user.id}, neck accepted={neck}")
    await message.answer(f"✅ Обхват шеи: {neck} см")
    await ask_hip_measurement(message, state)

async def ask_hip_measurement(message: types.Message, state: FSMContext):
    """Запросить измерение бедер (только для женщин)"""
    logging.info(f"ask_hip_measurement: user={message.from_user.id}")
    db = SessionLocal()
    user = get_user(db, message.from_user.id)
    db.close()
    
    # Если пользователь не существует или пол не указан, пропускаем измерение бедер
    if not user or not user.sex or user.sex != 'female':
        await ask_weight_measurement(message, state)
    else:
        await message.answer(get_hip_request())
        await MeasurementsStates.hip.set()

async def process_hip_measurement(message: types.Message, state: FSMContext):
    """Обработать измерение бедер"""
    hip = message.text.strip()
    logging.info(f"process_hip_measurement: user={message.from_user.id}, hip={hip}")
    from utils.validators import validate_hip_measurement
    if not validate_hip_measurement(hip):
        logging.warning(f"process_hip_measurement: user={message.from_user.id}, invalid hip={hip}")
        await message.answer(get_validation_error("Обхват бедер должен быть числом от 50 до 200 см"))
        return
    await state.update_data(hip=float(hip))
    logging.info(f"process_hip_measurement: user={message.from_user.id}, hip accepted={hip}")
    await message.answer(f"✅ Обхват бедер: {hip} см")
    await ask_weight_measurement(message, state)

async def ask_weight_measurement(message: types.Message, state: FSMContext):
    """Запросить измерение веса"""
    logging.info(f"ask_weight_measurement: user={message.from_user.id}")
    await message.answer("⚖️ Какой у вас текущий вес?\n\nВведите вес в килограммах (например: 70.5)")
    await MeasurementsStates.weight.set()

async def process_weight_measurement(message: types.Message, state: FSMContext):
    """Обработать измерение веса"""
    weight = message.text.strip()
    logging.info(f"process_weight_measurement: user={message.from_user.id}, weight={weight}")
    from utils.validators import validate_weight
    
    if not validate_weight(weight):
        logging.warning(f"process_weight_measurement: user={message.from_user.id}, invalid weight={weight}")
        await message.answer(get_validation_error("Вес должен быть числом от 30 до 300 кг"))
        return
    
    await state.update_data(weight=float(weight))
    logging.info(f"process_weight_measurement: user={message.from_user.id}, weight accepted={weight}")
    await message.answer(f"✅ Вес: {weight} кг")
    await ask_steps_measurement(message, state)

async def ask_steps_measurement(message: types.Message, state: FSMContext):
    """Запросить количество шагов"""
    logging.info(f"ask_steps_measurement: user={message.from_user.id}")
    from utils.texts import get_steps_request
    from utils.buttons import get_steps_keyboard
    await message.answer(get_steps_request(), reply_markup=get_steps_keyboard())
    await MeasurementsStates.steps.set()

async def process_steps_measurement(callback: types.CallbackQuery, state: FSMContext):
    """Обработать выбор шагов"""
    await callback.answer()
    steps = callback.data.split('_')[1]  # steps_8000-10000 -> 8000-10000
    logging.info(f"process_steps_measurement: user={callback.from_user.id}, steps={steps}")
    
    await state.update_data(steps=steps)
    await callback.message.edit_text(f"{callback.message.text}\n\n✅ Выбрано: {steps} шагов")
    await ask_sport_type_measurement(callback.message, state)

async def ask_sport_type_measurement(message: types.Message, state: FSMContext):
    """Запросить тип спорта"""
    logging.info(f"ask_sport_type_measurement: user={message.from_user.id}")
    from utils.texts import get_sport_request
    from utils.buttons import get_sport_keyboard
    await message.answer(get_sport_request(), reply_markup=get_sport_keyboard())
    await MeasurementsStates.sport_type.set()

async def process_sport_type_measurement(callback: types.CallbackQuery, state: FSMContext):
    """Обработать выбор типа спорта"""
    await callback.answer()
    sport_type = callback.data.split('_')[1]  # sport_running -> running
    logging.info(f"process_sport_type_measurement: user={callback.from_user.id}, sport_type={sport_type}")
    
    # Форматируем название спорта для отображения
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
    
    sport_text = sport_names.get(sport_type, sport_type)
    
    await state.update_data(sport_type=sport_type)
    await callback.message.edit_text(f"{callback.message.text}\n\n✅ Выбрано: {sport_text}")
    await ask_sport_freq_measurement(callback.message, state)

async def ask_sport_freq_measurement(message: types.Message, state: FSMContext):
    """Запросить частоту спорта"""
    logging.info(f"ask_sport_freq_measurement: user={message.from_user.id}")
    from utils.texts import get_frequency_request
    from utils.buttons import get_frequency_keyboard
    await message.answer(get_frequency_request(), reply_markup=get_frequency_keyboard())
    await MeasurementsStates.sport_freq.set()

async def process_sport_freq_measurement(callback: types.CallbackQuery, state: FSMContext):
    """Обработать выбор частоты спорта"""
    await callback.answer()
    sport_freq = callback.data.split('_')[1]  # freq_3 -> 3
    logging.info(f"process_sport_freq_measurement: user={callback.from_user.id}, sport_freq={sport_freq}")
    
    # Форматируем частоту тренировок
    freq_names = {
        '0': '0 раз в неделю',
        '1': '1 раз в неделю',
        '2': '2 раза в неделю',
        '3': '3 раза в неделю',
        '4': '4 раза в неделю',
        '5': '5 раз в неделю',
        '6': '6 раз в неделю',
        'daily': 'Ежедневно'
    }
    
    freq_text = freq_names.get(sport_freq, f"{sport_freq} раз в неделю")
    
    await state.update_data(sport_freq=sport_freq)
    await callback.message.edit_text(f"{callback.message.text}\n\n✅ Выбрано: {freq_text}")
    await finish_measurements(callback.message, state)

async def finish_measurements(message: types.Message, state: FSMContext):
    """Завершить измерения и сохранить данные"""
    # Получаем правильный ID пользователя
    user_id = None
    
    # Проверяем, есть ли в состоянии информация о пользователе
    measurements_data = await state.get_data()
    
    # Если это callback message, получаем ID из chat
    if hasattr(message, 'chat') and hasattr(message.chat, 'id'):
        user_id = message.chat.id
    else:
        # Пытаемся получить ID из различных источников
        if hasattr(message, 'from_user') and hasattr(message.from_user, 'id'):
            user_id = message.from_user.id
        elif hasattr(message, 'chat') and hasattr(message.chat, 'id'):
            user_id = message.chat.id
        else:
            # Используем ID из состояния или из данных измерений
            user_id = measurements_data.get('user_id')
    
    logging.info(f"finish_measurements: user_id={user_id}")
    
    if not user_id:
        logging.error(f"finish_measurements: не удалось определить ID пользователя")
        await message.answer("❌ Ошибка: не удалось определить пользователя!")
        await message.answer("🏠 Главное меню", reply_markup=get_main_menu_inline_keyboard())
        await state.finish()
        return
    
    db = SessionLocal()
    
    # Сначала получаем или создаем пользователя
    user = get_user(db, user_id)
    
    if not user:
        # Создаем пользователя с базовыми данными
        from crud.user_crud import create_user
        user = create_user(
            db, 
            user_id,
            username=None,  # Не можем получить username из callback
            first_name="Пользователь",
            last_name="Тестовый",
            sex='male'  # По умолчанию, можно будет изменить позже
        )
        if not user:
            logging.error(f"finish_measurements: НЕ удалось создать пользователя для ID {user_id}")
            await message.answer("❌ Ошибка: не удалось создать пользователя!")
            await message.answer("🏠 Главное меню", reply_markup=get_main_menu_inline_keyboard())
            await state.finish()
            db.close()
            return
    
    # Получаем последнюю запись для получения роста и других данных
    from crud.record_crud import get_latest_record, get_user_records
    latest_record = get_latest_record(db, user_id)
    
    # Рассчитываем множитель шагов
    from utils.calculations import calculate_step_multiplier
    step_multiplier = calculate_step_multiplier(measurements_data.get('steps', '8000-10000'))
    
    # Рассчитываем процент жира ДО сохранения записи
    user_data = {
        'sex': user.sex,
        'height': latest_record.height if latest_record else 170,
        'weight': measurements_data['weight'],
        'waist': measurements_data['waist'],
        'neck': measurements_data['neck'],
        'hip': measurements_data.get('hip')
    }
    
    bodyfat = calculate_bodyfat(user_data)
    
    # Создаем новую запись со всеми данными, включая правильный bodyfat
    record_result = create_or_update_record(
        db,
        user_id,
        date.today(),
        weight=measurements_data['weight'],
        waist=measurements_data['waist'],
        neck=measurements_data['neck'],
        hip=measurements_data.get('hip'),
        steps=measurements_data.get('steps', '8000-10000'),
        sport_type=measurements_data.get('sport_type', 'none'),
        sport_freq=measurements_data.get('sport_freq', '0'),
        step_multiplier=step_multiplier,
        height=latest_record.height if latest_record else 170,
        goal=latest_record.goal if latest_record else 'maintain',
        bodyfat=bodyfat  # Сохраняем правильный процент жира
    )
    
    if not record_result:
        logging.error(f"finish_measurements: НЕ удалось создать запись измерений для пользователя {user_id}")
        await message.answer("❌ Ошибка: не удалось сохранить измерения!")
        await message.answer("🏠 Главное меню", reply_markup=get_main_menu_inline_keyboard())
        await state.finish()
        db.close()
        return
    
    # Получаем все записи пользователя для анализа прогресса
    all_records = get_user_records(db, user_id)
    db.close()
    
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
    
    freq_names = {
        '0': '0 раз в неделю',
        '1': '1 раз в неделю',
        '2': '2 раза в неделю',
        '3': '3 раза в неделю',
        '4': '4 раза в неделю',
        '5': '5 раз в неделю',
        '6': '6 раз в неделю',
        'daily': 'Ежедневно'
    }
    
    # Показываем результаты
    text = f"""✅ **Новые замеры сохранены!**

📊 **Ваши измерения:**
• Вес: {measurements_data['weight']} кг
• Талия: {measurements_data['waist']} см
• Шея: {measurements_data['neck']} см"""

    if measurements_data.get('hip'):
        text += f"\n• Бёдра: {measurements_data['hip']} см"
    
    text += f"""

🏃‍♂️ **Активность:**
• Шаги: {measurements_data.get('steps', '8000-10000')}
• Спорт: {sport_names.get(measurements_data.get('sport_type', 'none'), 'Не указано')}
• Частота: {freq_names.get(measurements_data.get('sport_freq', '0'), f"{measurements_data.get('sport_freq', '0')} раз в неделю")}

🔥 **Процент жира:** {bodyfat:.1f}%"""
    
    await message.answer(text, parse_mode='Markdown')
    
    # Показываем мотивирующее сообщение, если есть прогресс
    if len(all_records) >= 2:
        from utils.progress import get_motivational_message
        motivational_text = get_motivational_message(all_records)
        await message.answer(motivational_text, parse_mode='Markdown')
    
    await state.finish()

def register_measurements_handlers(dp: Dispatcher):
    """Регистрация обработчиков измерений"""
    dp.register_message_handler(start_new_measurements, text="📝 Новые замеры")
    dp.register_message_handler(process_waist_measurement, state=MeasurementsStates.waist)
    dp.register_message_handler(process_neck_measurement, state=MeasurementsStates.neck)
    dp.register_message_handler(process_hip_measurement, state=MeasurementsStates.hip)
    dp.register_message_handler(process_weight_measurement, state=MeasurementsStates.weight)
    
    # Обработчики для callback (шаги и спорт)
    dp.register_callback_query_handler(process_steps_measurement, lambda c: c.data.startswith('steps_'), state=MeasurementsStates.steps)
    dp.register_callback_query_handler(process_sport_type_measurement, lambda c: c.data.startswith('sport_'), state=MeasurementsStates.sport_type)
    dp.register_callback_query_handler(process_sport_freq_measurement, lambda c: c.data.startswith('freq_'), state=MeasurementsStates.sport_freq) 