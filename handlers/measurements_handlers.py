from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from datetime import date, datetime
import logging

from models.database import SessionLocal
from crud.user_crud import get_user
from crud.record_crud import create_or_update_record, get_latest_record, get_user_records
from states.fsm_states import MeasurementsStates
from utils.texts import (
    get_weight_request, get_waist_request, get_neck_request, get_hip_request,
    get_chest_request, get_bicep_request, get_thigh_request,
    get_wrist_request, get_calf_request, get_forearm_request, get_abdomen_request,
    get_sleep_request, get_stress_request,
    get_validation_error, get_final_results_text, get_kbju_explanation,
    get_comprehensive_metrics_text, get_metabolic_analysis_text, get_body_composition_text,
    get_safety_warnings_text, get_adaptive_recommendations_text
)
from utils.buttons import get_main_menu_inline_keyboard, get_stress_keyboard
from utils.validators import (
    validate_weight, validate_measurement, validate_wrist_measurement,
    validate_calf_measurement, validate_forearm_measurement, validate_abdomen_measurement,
    validate_sleep_hours, validate_stress_level
)
from utils.calculations import (
    calculate_bodyfat_precise, calculate_kbju, calculate_step_multiplier,
    calculate_comprehensive_metrics, safety_checks, get_adaptive_recommendations
)

# Конфигурация измерений для универсальной обработки
MEASUREMENT_CONFIG = {
    'waist': {
        'request_func': get_waist_request,
        'validator': 'validate_waist_measurement',
        'state': MeasurementsStates.waist,
        'next': 'neck',
        'error_msg': "Обхват талии должен быть числом от 50 до 200 см"
    },
    'neck': {
        'request_func': get_neck_request,
        'validator': 'validate_neck_measurement',
        'state': MeasurementsStates.neck,
        'next': 'hip',
        'error_msg': "Обхват шеи должен быть числом от 20 до 100 см"
    },
    'hip': {
        'request_func': get_hip_request,
        'validator': 'validate_hip_measurement',
        'state': MeasurementsStates.hip,
        'next': 'chest',
        'error_msg': "Обхват бедер должен быть числом от 50 до 200 см",
        'conditional': True  # Только для женщин
    },
    'chest': {
        'request_func': get_chest_request,
        'validator': 'validate_chest_measurement',
        'state': MeasurementsStates.chest,
        'next': 'bicep',
        'error_msg': "Обхват груди должен быть числом от 60 до 150 см"
    },
    'bicep': {
        'request_func': get_bicep_request,
        'validator': 'validate_bicep_measurement',
        'state': MeasurementsStates.bicep,
        'next': 'thigh',
        'error_msg': "Обхват плеча должен быть числом от 20 до 60 см"
    },
    'thigh': {
        'request_func': get_thigh_request,
        'validator': 'validate_thigh_measurement',
        'state': MeasurementsStates.thigh,
        'next': 'wrist',
        'error_msg': "Обхват бедра должен быть числом от 40 до 100 см"
    },
    'wrist': {
        'request_func': get_wrist_request,
        'validator': 'validate_wrist_measurement',
        'state': MeasurementsStates.wrist,
        'next': 'calf',
        'error_msg': "Обхват запястья должен быть числом от 15 до 25 см"
    },
    'calf': {
        'request_func': get_calf_request,
        'validator': 'validate_calf_measurement',
        'state': MeasurementsStates.calf,
        'next': 'forearm',
        'error_msg': "Обхват голени должен быть числом от 25 до 50 см"
    },
    'forearm': {
        'request_func': get_forearm_request,
        'validator': 'validate_forearm_measurement',
        'state': MeasurementsStates.forearm,
        'next': 'abdomen',
        'error_msg': "Обхват предплечья должен быть числом от 20 до 40 см"
    },
    'abdomen': {
        'request_func': get_abdomen_request,
        'validator': 'validate_abdomen_measurement',
        'state': MeasurementsStates.abdomen,
        'next': 'sleep_hours',
        'error_msg': "Обхват живота должен быть числом от 60 до 150 см"
    }
}

async def start_new_measurements(message: types.Message, state: FSMContext):
    """Начать новые измерения"""
    user_id = message.from_user.id
    logging.info(f"start_new_measurements: user_id={user_id}")
    
    # Сохраняем ID пользователя в состояние
    await state.update_data(user_id=user_id)
    
    await message.answer("📝 Давайте сделаем новые замеры!")
    await ask_measurement(message, state, 'waist')

async def ask_measurement(message: types.Message, state: FSMContext, measurement_type: str):
    """Универсальная функция для запроса измерения"""
    config = MEASUREMENT_CONFIG.get(measurement_type)
    if not config:
        logging.error(f"Unknown measurement type: {measurement_type}")
        return
    
    # Проверяем условные измерения (например, бедра только для женщин)
    if config.get('conditional'):
        db = SessionLocal()
        user = get_user(db, message.from_user.id)
        db.close()
        
        if not user or not user.sex or user.sex != 'female':
            # Пропускаем это измерение
            await ask_measurement(message, state, config['next'])
            return
    
    logging.info(f"ask_measurement: user={message.from_user.id}, type={measurement_type}")
    await message.answer(config['request_func']())
    await config['state'].set()

async def process_measurement(message: types.Message, state: FSMContext, measurement_type: str):
    """Универсальная функция для обработки измерения"""
    config = MEASUREMENT_CONFIG.get(measurement_type)
    if not config:
        logging.error(f"Unknown measurement type: {measurement_type}")
        return
    
    value = message.text.strip()
    logging.info(f"process_measurement: user={message.from_user.id}, type={measurement_type}, value={value}")
    
    # Импортируем валидатор динамически
    import utils.validators as validators
    validator_func = getattr(validators, config['validator'])
    
    if not validator_func(value):
        logging.warning(f"process_measurement: user={message.from_user.id}, invalid {measurement_type}={value}")
        await message.answer(get_validation_error(config['error_msg']))
        return
    
    await state.update_data(**{measurement_type: float(value)})
    logging.info(f"process_measurement: user={message.from_user.id}, {measurement_type} accepted={value}")
    await message.answer(f"✅ {measurement_type.title()}: {value} см")
    
    # Переходим к следующему измерению
    await ask_measurement(message, state, config['next'])

# Специальные обработчики для измерений, которые не подходят под универсальный шаблон
async def ask_sleep_hours(message: types.Message, state: FSMContext):
    """Запросить часы сна"""
    logging.info(f"ask_sleep_hours: user={message.from_user.id}")
    await message.answer(get_sleep_request())
    await MeasurementsStates.sleep_hours.set()

async def process_sleep_hours(message: types.Message, state: FSMContext):
    """Обработать часы сна"""
    sleep = message.text.strip()
    logging.info(f"process_sleep_hours: user={message.from_user.id}, sleep={sleep}")
    if not validate_sleep_hours(sleep):
        logging.warning(f"process_sleep_hours: user={message.from_user.id}, invalid sleep={sleep}")
        await message.answer(get_validation_error("Часы сна должны быть числом от 4 до 12 часов"))
        return
    await state.update_data(sleep_hours=float(sleep))
    logging.info(f"process_sleep_hours: user={message.from_user.id}, sleep accepted={sleep}")
    await message.answer(f"✅ Часы сна: {sleep} часов")
    await ask_stress_level(message, state)

async def ask_stress_level(message: types.Message, state: FSMContext):
    """Запросить уровень стресса"""
    logging.info(f"ask_stress_level: user={message.from_user.id}")
    await message.answer(get_stress_request(), reply_markup=get_stress_keyboard())
    await MeasurementsStates.stress_level.set()

async def process_stress_level(callback: types.CallbackQuery, state: FSMContext):
    """Обработать уровень стресса"""
    stress_level = callback.data.split('_')[1]  # stress_low -> low
    logging.info(f"process_stress_level: user={callback.from_user.id}, stress_level={stress_level}")
    
    stress_names = {
        'low': 'Низкий',
        'medium': 'Средний',
        'high': 'Высокий'
    }
    
    await state.update_data(stress_level=stress_level)
    await callback.answer()
    await callback.message.edit_text(f"✅ Уровень стресса: {stress_names.get(stress_level, stress_level)}")
    await ask_weight_measurement(callback.message, state)

async def ask_weight_measurement(message: types.Message, state: FSMContext):
    """Запросить измерение веса"""
    logging.info(f"ask_weight_measurement: user={message.from_user.id}")
    await message.answer(get_weight_request())
    await MeasurementsStates.weight.set()

async def process_weight_measurement(message: types.Message, state: FSMContext):
    """Обработать измерение веса"""
    weight = message.text.strip()
    logging.info(f"process_weight_measurement: user={message.from_user.id}, weight={weight}")
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
    """Обработать количество шагов"""
    steps_data = callback.data.split('_')[1]  # steps_8000_10000 -> 8000_10000
    logging.info(f"process_steps_measurement: user={callback.from_user.id}, steps_data={steps_data}")
    
    # Преобразуем callback_data в steps
    steps_mapping = {
        '0_3000': '0-3000',
        '3000_5000': '3000-5000',
        '5000_8000': '5000-8000',
        '8000_10000': '8000-10000',
        '10000_plus': '10000+'
    }
    
    steps = steps_mapping.get(steps_data, '8000-10000')
    
    await state.update_data(steps=steps)
    await callback.answer()
    await callback.message.edit_text(f"✅ Шаги: {steps}")
    await ask_sport_type_measurement(callback.message, state)

async def ask_sport_type_measurement(message: types.Message, state: FSMContext):
    """Запросить тип спорта"""
    logging.info(f"ask_sport_type_measurement: user={message.from_user.id}")
    from utils.texts import get_sport_request
    from utils.buttons import get_sport_keyboard
    await message.answer(get_sport_request(), reply_markup=get_sport_keyboard())
    await MeasurementsStates.sport_type.set()

async def process_sport_type_measurement(callback: types.CallbackQuery, state: FSMContext):
    """Обработать тип спорта"""
    sport_type = callback.data.split('_')[1]  # sport_walking -> walking
    logging.info(f"process_sport_type_measurement: user={callback.from_user.id}, sport_type={sport_type}")
    
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
    
    await state.update_data(sport_type=sport_type)
    await callback.answer()
    await callback.message.edit_text(f"✅ Спорт: {sport_names.get(sport_type, sport_type)}")
    await ask_sport_freq_measurement(callback.message, state)

async def ask_sport_freq_measurement(message: types.Message, state: FSMContext):
    """Запросить частоту спорта"""
    logging.info(f"ask_sport_freq_measurement: user={message.from_user.id}")
    from utils.texts import get_frequency_request
    from utils.buttons import get_frequency_keyboard
    await message.answer(get_frequency_request(), reply_markup=get_frequency_keyboard())
    await MeasurementsStates.sport_freq.set()

async def process_sport_freq_measurement(callback: types.CallbackQuery, state: FSMContext):
    """Обработать частоту спорта"""
    freq_data = callback.data.split('_')[1]  # freq_1_2 -> 1_2
    logging.info(f"process_sport_freq_measurement: user={callback.from_user.id}, freq_data={freq_data}")
    
    # Преобразуем callback_data в sport_freq
    freq_mapping = {
        '1_2': '2',  # 1-2 раза -> 2 раза
        '3_4': '4',  # 3-4 раза -> 4 раза  
        '5_6': '5',  # 5-6 раз -> 5 раз
        'daily': '6'  # Ежедневно -> 6 раз
    }
    
    sport_freq = freq_mapping.get(freq_data, '0')
    
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
    
    await state.update_data(sport_freq=sport_freq)
    await callback.answer()
    await callback.message.edit_text(f"✅ Частота: {freq_names.get(sport_freq, f'{sport_freq} раз в неделю')}")
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
    latest_record = get_latest_record(db, user_id)
    
    # Рассчитываем множитель шагов
    step_multiplier = calculate_step_multiplier(measurements_data.get('steps', '8000-10000'))
    
    # Рассчитываем процент жира ДО сохранения записи
    user_data = {
        'sex': user.sex,
        'height': latest_record.height if latest_record else 170,
        'weight': measurements_data['weight'],
        'waist': measurements_data['waist'],
        'neck': measurements_data['neck'],
        'hip': measurements_data.get('hip'),
        'chest': measurements_data.get('chest'),
        'bicep': measurements_data.get('bicep'),
        'thigh': measurements_data.get('thigh'),
        'wrist': measurements_data.get('wrist'),
        'calf': measurements_data.get('calf'),
        'forearm': measurements_data.get('forearm'),
        'abdomen': measurements_data.get('abdomen'),
        'sleep_hours': measurements_data.get('sleep_hours', 7.0),
        'stress_level': measurements_data.get('stress_level', 'medium'),
        'sport_type': measurements_data.get('sport_type', 'none'),
        'sport_freq': measurements_data.get('sport_freq', '0')
    }
    
    bodyfat = calculate_bodyfat_precise(user_data)
    
    # Рассчитываем комплексные метрики
    comprehensive_metrics = calculate_comprehensive_metrics(user_data, bodyfat)
    
    # Проверяем безопасность
    safety_data = safety_checks(user_data, comprehensive_metrics)
    
    # Получаем адаптивные рекомендации
    adaptive_data = get_adaptive_recommendations(user_data, comprehensive_metrics)
    
    # Создаем новую запись со всеми данными
    record_result = create_or_update_record(
        db,
        user_id,
        date.today(),
        weight=measurements_data['weight'],
        waist=measurements_data['waist'],
        neck=measurements_data['neck'],
        hip=measurements_data.get('hip'),
        chest=measurements_data.get('chest'),
        bicep=measurements_data.get('bicep'),
        thigh=measurements_data.get('thigh'),
        wrist=measurements_data.get('wrist'),
        calf=measurements_data.get('calf'),
        forearm=measurements_data.get('forearm'),
        abdomen=measurements_data.get('abdomen'),
        sleep_hours=measurements_data.get('sleep_hours', 7.0),
        stress_level=measurements_data.get('stress_level', 'medium'),
        steps=measurements_data.get('steps', '8000-10000'),
        sport_type=measurements_data.get('sport_type', 'none'),
        sport_freq=measurements_data.get('sport_freq', '0'),
        step_multiplier=step_multiplier,
        height=latest_record.height if latest_record else 170,
        goal=latest_record.goal if latest_record else 'maintain',
        bodyfat=bodyfat,
        bmi=comprehensive_metrics['basic_metrics']['bmi'] if comprehensive_metrics else None,
        lbm=comprehensive_metrics['basic_metrics']['lbm'] if comprehensive_metrics else None,
        whr=comprehensive_metrics['basic_metrics']['whr'] if comprehensive_metrics else None,
        bmr=comprehensive_metrics['metabolic_metrics']['bmr'] if comprehensive_metrics else None,
        tdee=comprehensive_metrics['metabolic_metrics']['tdee'] if comprehensive_metrics else None,
        metabolic_age=comprehensive_metrics['metabolic_metrics']['metabolic_age'] if comprehensive_metrics else None,
        body_type=comprehensive_metrics['classifications']['body_type'] if comprehensive_metrics else None,
        bodyfat_category=comprehensive_metrics['classifications']['bodyfat_category'] if comprehensive_metrics else None
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
    
    # Показываем основные результаты
    text = f"""✅ **Новые замеры сохранены!**

📊 **Ваши измерения:**
• Вес: {measurements_data['weight']} кг
• Талия: {measurements_data['waist']} см
• Шея: {measurements_data['neck']} см"""

    if measurements_data.get('hip'):
        text += f"\n• Бёдра: {measurements_data['hip']} см"
    
    if measurements_data.get('chest'):
        text += f"\n• Грудь: {measurements_data['chest']} см"
    
    if measurements_data.get('bicep'):
        text += f"\n• Плечо: {measurements_data['bicep']} см"
    
    if measurements_data.get('thigh'):
        text += f"\n• Бедро: {measurements_data['thigh']} см"
    
    if measurements_data.get('wrist'):
        text += f"\n• Запястье: {measurements_data['wrist']} см"
    
    if measurements_data.get('calf'):
        text += f"\n• Голень: {measurements_data['calf']} см"
    
    if measurements_data.get('forearm'):
        text += f"\n• Предплечье: {measurements_data['forearm']} см"
    
    if measurements_data.get('abdomen'):
        text += f"\n• Живот: {measurements_data['abdomen']} см"
    
    text += f"""

🏃‍♂️ **Активность:**
• Шаги: {measurements_data.get('steps', '8000-10000')}
• Спорт: {sport_names.get(measurements_data.get('sport_type', 'none'), 'Не указано')}
• Частота: {freq_names.get(measurements_data.get('sport_freq', '0'), f"{measurements_data.get('sport_freq', '0')} раз в неделю")}

😴 **Образ жизни:**
• Сон: {measurements_data.get('sleep_hours', 7.0)} часов
• Стресс: {measurements_data.get('stress_level', 'medium')}

🔥 **Процент жира:** {bodyfat:.1f}%"""

    await message.answer(text, parse_mode='Markdown')
    
    # Показываем комплексные метрики
    if comprehensive_metrics:
        await message.answer(
            get_comprehensive_metrics_text(comprehensive_metrics),
            parse_mode='Markdown'
        )
        
        # Показываем анализ метаболизма
        await message.answer(
            get_metabolic_analysis_text(comprehensive_metrics),
            parse_mode='Markdown'
        )
        
        # Показываем анализ состава тела
        await message.answer(
            get_body_composition_text(comprehensive_metrics),
            parse_mode='Markdown'
        )
    
    # Показываем адаптивные рекомендации
    await message.answer(
        get_adaptive_recommendations_text(adaptive_data),
        parse_mode='Markdown'
    )
    
    # Показываем предупреждения безопасности
    safety_text = get_safety_warnings_text(safety_data)
    if safety_text:
        await message.answer(safety_text, parse_mode='Markdown')
    
    # Показываем мотивирующее сообщение, если есть прогресс
    if len(all_records) >= 2:
        from utils.progress import get_motivational_message
        motivational_text = get_motivational_message(all_records)
        await message.answer(motivational_text, parse_mode='Markdown')
    
    await state.finish()

def register_measurements_handlers(dp: Dispatcher):
    """Регистрация обработчиков измерений"""
    dp.register_message_handler(start_new_measurements, text="📝 Новые замеры")
    
    # Регистрируем универсальные обработчики для всех измерений
    for measurement_type in MEASUREMENT_CONFIG.keys():
        config = MEASUREMENT_CONFIG[measurement_type]
        dp.register_message_handler(
            lambda msg, state, mt=measurement_type: process_measurement(msg, state, mt),
            state=config['state']
        )
    
    # Специальные обработчики
    dp.register_message_handler(process_sleep_hours, state=MeasurementsStates.sleep_hours)
    dp.register_message_handler(process_weight_measurement, state=MeasurementsStates.weight)
    
    # Обработчики для callback (шаги, спорт, стресс)
    dp.register_callback_query_handler(process_steps_measurement, lambda c: c.data.startswith('steps_'), state=MeasurementsStates.steps)
    dp.register_callback_query_handler(process_sport_type_measurement, lambda c: c.data.startswith('sport_'), state=MeasurementsStates.sport_type)
    dp.register_callback_query_handler(process_sport_freq_measurement, lambda c: c.data.startswith('freq_'), state=MeasurementsStates.sport_freq)
    dp.register_callback_query_handler(process_stress_level, lambda c: c.data.startswith('stress_'), state=MeasurementsStates.stress_level) 