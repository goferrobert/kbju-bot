from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from datetime import date, datetime
import logging
import asyncio

from models.database import SessionLocal
from crud.user_crud import create_user, update_user, get_user
from states.fsm_states import UserInfoStates
from utils.texts import (
    get_name_request, get_birthday_request, get_sex_request, 
    get_height_request, get_weight_request, get_steps_request,
    get_sport_request, get_frequency_request, get_goal_request,
    get_waist_request, get_neck_request, get_hip_request,
    get_chest_request, get_bicep_request, get_thigh_request,
    get_validation_error, get_final_results_text, get_kbju_explanation,
    get_funnel_text_with_image, get_kbju_text
)
from utils.buttons import (
    get_sex_keyboard, get_steps_keyboard, get_sport_keyboard,
    get_frequency_keyboard, get_goal_keyboard, get_main_menu_inline_keyboard,
    get_funnel_keyboard
)
from utils.validators import validate_name, validate_birthday, validate_height, validate_weight, validate_measurement
from utils.calculations import calculate_bodyfat, calculate_kbju, calculate_step_multiplier
from crud.record_crud import create_or_update_record

async def ask_name(message: types.Message, state: FSMContext):
    logging.info(f"ask_name: user={message.from_user.id}")
    """Запрашиваем имя"""
    await message.answer(get_name_request())
    await UserInfoStates.name.set()

async def process_name(message: types.Message, state: FSMContext):
    """Обработать имя пользователя"""
    name = message.text.strip()
    logging.info(f"process_name: user={message.from_user.id}, name={name}")
    
    if not validate_name(name):
        logging.warning(f"process_name: user={message.from_user.id}, invalid name={name}")
        await message.answer(
            "❌ **Некорректное имя!**\n\n"
            "Имя должно содержать:\n"
            "• Минимум 2 слова (имя и фамилия)\n"
            "• Только русские и английские буквы\n"
            "• Пробелы и дефисы\n"
            "• Каждое слово минимум 2 буквы\n\n"
            "**Примеры правильных имен:**\n"
            "• Иван Иванов\n"
            "• Anna Smith\n"
            "• Мария-Анна Петрова\n\n"
            "Попробуйте еще раз!"
        )
        return
    
    await state.update_data(name=name)
    logging.info(f"process_name: user={message.from_user.id}, name accepted={name}")
    await ask_birthday(message, state)

async def ask_birthday(message: types.Message, state: FSMContext):
    """Запрашиваем дату рождения"""
    await message.answer(get_birthday_request())
    await UserInfoStates.birthday.set()

async def process_birthday(message: types.Message, state: FSMContext):
    """Обработать дату рождения"""
    birthday = message.text.strip()
    logging.info(f"process_birthday: user={message.from_user.id}, birthday={birthday}")
    
    if not validate_birthday(birthday):
        logging.warning(f"process_birthday: user={message.from_user.id}, invalid birthday={birthday}")
        await message.answer(
            "❌ **Некорректная дата рождения!**\n\n"
            "Дата должна быть:\n"
            "• В формате ДД.ММ.ГГГГ\n"
            "• Не в будущем\n"
            "• Возраст от 10 до 120 лет\n\n"
            "**Примеры правильных дат:**\n"
            "• 15.03.1990\n"
            "• 01.01.2000\n"
            "• 31.12.1985\n\n"
            "Попробуйте еще раз!"
        )
        return
    
    await state.update_data(birthday=birthday)
    logging.info(f"process_birthday: user={message.from_user.id}, birthday accepted={birthday}")
    await ask_sex(message, state)

async def ask_sex(message: types.Message, state: FSMContext):
    """Запрашиваем пол"""
    await message.answer(get_sex_request(), reply_markup=get_sex_keyboard())
    await UserInfoStates.sex.set()

async def process_sex_callback(callback: types.CallbackQuery, state: FSMContext):
    """Обрабатываем выбор пола"""
    await callback.answer()
    
    sex = callback.data.split('_')[1]  # sex_male -> male
    sex_text = "Мужской" if sex == "male" else "Женский"
    
    # Обновляем сообщение с выбором
    await callback.message.edit_text(
        f"{callback.message.text}\n\n✅ Выбрано: {sex_text}"
    )
    
    await state.update_data(sex=sex)
    await ask_height(callback.message, state)

async def ask_height(message: types.Message, state: FSMContext):
    """Запрашиваем рост"""
    await message.answer(get_height_request())
    await UserInfoStates.height.set()

async def process_height(message: types.Message, state: FSMContext):
    """Обрабатываем рост"""
    height = message.text.strip()
    
    if not validate_height(height):
        await message.answer(get_validation_error("Рост должен быть числом от 100 до 250 см"))
        return
    
    await state.update_data(height=int(height))
    await message.answer(f"✅ Рост: {height} см")
    await ask_weight(message, state)

async def ask_weight(message: types.Message, state: FSMContext):
    """Запрашиваем вес"""
    await message.answer(get_weight_request())
    await UserInfoStates.weight.set()

async def process_weight(message: types.Message, state: FSMContext):
    """Обрабатываем вес"""
    weight = message.text.strip()
    
    if not validate_weight(weight):
        await message.answer(get_validation_error("Вес должен быть числом от 30 до 300 кг"))
        return
    
    await state.update_data(weight=float(weight))
    await message.answer(f"✅ Вес: {weight} кг")
    await ask_steps(message, state)

async def ask_steps(message: types.Message, state: FSMContext):
    """Запрашиваем количество шагов"""
    await message.answer(get_steps_request(), reply_markup=get_steps_keyboard())
    await UserInfoStates.steps.set()

async def process_steps_callback(callback: types.CallbackQuery, state: FSMContext):
    """Обрабатываем выбор шагов"""
    await callback.answer()
    
    steps_data = callback.data.split('_')[1:]  # steps_0_3000 -> ['0', '3000']
    if len(steps_data) == 2:
        steps = f"{steps_data[0]}-{steps_data[1]}"
    else:
        steps = "10000+"
    
    # Обновляем сообщение с выбором
    await callback.message.edit_text(
        f"{callback.message.text}\n\n✅ Выбрано: {steps} шагов"
    )
    
    await state.update_data(steps=steps)
    await ask_sport(callback.message, state)

async def ask_sport(message: types.Message, state: FSMContext):
    """Запрашиваем тип спорта"""
    await message.answer(get_sport_request(), reply_markup=get_sport_keyboard())
    await UserInfoStates.sport_type.set()

async def process_sport_callback(callback: types.CallbackQuery, state: FSMContext):
    """Обрабатываем выбор спорта"""
    await callback.answer()
    
    sport_type = callback.data.split('_')[1]  # sport_walking -> walking
    sport_names = {
        'none': 'Не занимаюсь',
        'walking': 'Ходьба/Прогулки',
        'running': 'Бег/Кардио',
        'strength': 'Тренажерный зал',
        'yoga': 'Йога/Пилатес',
        'swimming': 'Плавание',
        'cycling': 'Велосипед',
        'team': 'Футбол/Баскетбол'
    }
    
    sport_text = sport_names.get(sport_type, sport_type)
    
    # Обновляем сообщение с выбором
    await callback.message.edit_text(
        f"{callback.message.text}\n\n✅ Выбрано: {sport_text}"
    )
    
    await state.update_data(sport_type=sport_type)
    await ask_frequency(callback.message, state)

async def ask_frequency(message: types.Message, state: FSMContext):
    """Запрашиваем частоту тренировок"""
    await message.answer(get_frequency_request(), reply_markup=get_frequency_keyboard())
    await UserInfoStates.sport_freq.set()

async def process_frequency_callback(callback: types.CallbackQuery, state: FSMContext):
    """Обрабатываем выбор частоты"""
    await callback.answer()
    
    freq = callback.data.split('_')[1]  # freq_1_2 -> 1_2
    freq_names = {
        '1_2': '1-2 раза',
        '3_4': '3-4 раза',
        '5_6': '5-6 раз',
        'daily': 'Ежедневно'
    }
    
    freq_text = freq_names.get(freq, freq)
    
    # Обновляем сообщение с выбором
    await callback.message.edit_text(
        f"{callback.message.text}\n\n✅ Выбрано: {freq_text}"
    )
    
    await state.update_data(sport_freq=freq_text)
    await ask_waist(callback.message, state)

async def ask_waist(message: types.Message, state: FSMContext):
    """Запрашиваем обхват талии"""
    await message.answer(get_waist_request())
    await UserInfoStates.waist.set()

async def process_waist(message: types.Message, state: FSMContext):
    """Обрабатываем обхват талии"""
    waist = message.text.strip()
    logging.info(f"process_waist: user={message.from_user.id}, waist={waist}")
    from utils.validators import validate_waist_measurement
    
    if not validate_waist_measurement(waist):
        logging.warning(f"process_waist: user={message.from_user.id}, invalid waist={waist}")
        await message.answer("❌ Обхват талии должен быть числом от 50 до 200 см")
        return
    
    await state.update_data(waist=float(waist))
    logging.info(f"process_waist: user={message.from_user.id}, waist accepted={waist}")
    await ask_neck(message, state)

async def ask_neck(message: types.Message, state: FSMContext):
    """Запрашиваем обхват шеи"""
    await message.answer(get_neck_request())
    await UserInfoStates.neck.set()

async def process_neck(message: types.Message, state: FSMContext):
    """Обрабатываем обхват шеи"""
    neck = message.text.strip()
    logging.info(f"process_neck: user={message.from_user.id}, neck={neck}")
    from utils.validators import validate_neck_measurement
    
    if not validate_neck_measurement(neck):
        logging.warning(f"process_neck: user={message.from_user.id}, invalid neck={neck}")
        await message.answer("❌ Обхват шеи должен быть числом от 20 до 100 см")
        return
    
    await state.update_data(neck=float(neck))
    logging.info(f"process_neck: user={message.from_user.id}, neck accepted={neck}")
    await ask_hip(message, state)

async def ask_hip(message: types.Message, state: FSMContext):
    """Запрашиваем обхват бедер (только для женщин)"""
    user_data = await state.get_data()
    if user_data.get('sex') == 'female':
        await message.answer(get_hip_request())
        await UserInfoStates.hip.set()
    else:
        await ask_chest(message, state)

async def process_hip(message: types.Message, state: FSMContext):
    """Обрабатываем обхват бедер"""
    hip = message.text.strip()
    logging.info(f"process_hip: user={message.from_user.id}, hip={hip}")
    from utils.validators import validate_hip_measurement
    
    if not validate_hip_measurement(hip):
        logging.warning(f"process_hip: user={message.from_user.id}, invalid hip={hip}")
        await message.answer("❌ Обхват бедер должен быть числом от 50 до 200 см")
        return
    
    await state.update_data(hip=float(hip))
    logging.info(f"process_hip: user={message.from_user.id}, hip accepted={hip}")
    await ask_chest(message, state)

async def ask_chest(message: types.Message, state: FSMContext):
    """Запрашиваем обхват груди"""
    await message.answer(get_chest_request())
    await UserInfoStates.chest.set()

async def process_chest(message: types.Message, state: FSMContext):
    """Обрабатываем обхват груди"""
    chest = message.text.strip()
    logging.info(f"process_chest: user={message.from_user.id}, chest={chest}")
    from utils.validators import validate_chest_measurement
    
    if not validate_chest_measurement(chest):
        logging.warning(f"process_chest: user={message.from_user.id}, invalid chest={chest}")
        await message.answer("❌ Обхват груди должен быть числом от 60 до 150 см")
        return
    
    await state.update_data(chest=float(chest))
    logging.info(f"process_chest: user={message.from_user.id}, chest accepted={chest}")
    await ask_bicep(message, state)

async def ask_bicep(message: types.Message, state: FSMContext):
    """Запрашиваем обхват плеча"""
    await message.answer(get_bicep_request())
    await UserInfoStates.bicep.set()

async def process_bicep(message: types.Message, state: FSMContext):
    """Обрабатываем обхват плеча"""
    bicep = message.text.strip()
    logging.info(f"process_bicep: user={message.from_user.id}, bicep={bicep}")
    from utils.validators import validate_bicep_measurement
    
    if not validate_bicep_measurement(bicep):
        logging.warning(f"process_bicep: user={message.from_user.id}, invalid bicep={bicep}")
        await message.answer("❌ Обхват плеча должен быть числом от 20 до 60 см")
        return
    
    await state.update_data(bicep=float(bicep))
    logging.info(f"process_bicep: user={message.from_user.id}, bicep accepted={bicep}")
    await ask_thigh(message, state)

async def ask_thigh(message: types.Message, state: FSMContext):
    """Запрашиваем обхват бедра"""
    await message.answer(get_thigh_request())
    await UserInfoStates.thigh.set()

async def process_thigh(message: types.Message, state: FSMContext):
    """Обрабатываем обхват бедра"""
    thigh = message.text.strip()
    logging.info(f"process_thigh: user={message.from_user.id}, thigh={thigh}")
    from utils.validators import validate_thigh_measurement
    
    if not validate_thigh_measurement(thigh):
        logging.warning(f"process_thigh: user={message.from_user.id}, invalid thigh={thigh}")
        await message.answer("❌ Обхват бедра должен быть числом от 40 до 100 см")
        return
    
    await state.update_data(thigh=float(thigh))
    logging.info(f"process_thigh: user={message.from_user.id}, thigh accepted={thigh}")
    await ask_goal(message, state)

async def ask_goal(message: types.Message, state: FSMContext):
    """Запрашиваем цель"""
    await message.answer(get_goal_request(), reply_markup=get_goal_keyboard())
    await UserInfoStates.goal.set()

async def process_goal_callback(callback: types.CallbackQuery, state: FSMContext):
    """Обрабатываем выбор цели"""
    await callback.answer()
    
    goal = callback.data.split('_')[1]  # goal_healthy -> healthy
    goal_names = {
        'healthy': 'Здоровое тело',
        'athletic': 'Спортивное тело',
        'lean': 'Сухое тело'
    }
    
    goal_text = goal_names.get(goal, goal)
    
    # Обновляем сообщение с выбором
    await callback.message.edit_text(
        f"{callback.message.text}\n\n✅ Выбрано: {goal_text}"
    )
    
    await state.update_data(goal=goal)
    await finish_survey(callback.from_user, state)

async def finish_survey(user, state: FSMContext):
    """Завершаем анкету и показываем результаты"""
    user_data = await state.get_data()

    # Получаем объект бота
    bot = Dispatcher.get_current().bot

    # Разделяем ФИО: первое слово — фамилия, остальные — имя
    fio_parts = user_data['name'].split()
    last_name = fio_parts[0] if len(fio_parts) > 0 else None
    first_name = ' '.join(fio_parts[1:]) if len(fio_parts) > 1 else None

    # Рассчитываем step_multiplier
    step_multiplier = calculate_step_multiplier(user_data['steps'])
    user_data['step_multiplier'] = step_multiplier

    # Рассчитываем процент жира и КБЖУ
    from utils.calculations import calculate_bodyfat_precise
    bodyfat = calculate_bodyfat_precise(user_data)
    user_data['bodyfat'] = bodyfat
    kbju = calculate_kbju(user_data, bodyfat)

    # Создаём пользователя (только идентификационные и статичные данные)
    db = SessionLocal()
    existing_user = get_user(db, user.id)
    if existing_user:
        await bot.send_message(
            user.id,
            'Вы уже зарегистрированы! Можете добавить новые замеры или воспользоваться меню.',
            reply_markup=get_main_menu_inline_keyboard()
        )
        db.close()
        await state.finish()
        return
    user_obj = create_user(
        db,
        telegram_id=user.id,
        username=user.username,
        first_name=first_name,
        last_name=last_name
    )
    update_user(
        db,
        user.id,
        first_name=first_name,
        last_name=last_name,
        sex=user_data['sex'],
        date_of_birth=datetime.strptime(user_data['birthday'], '%d.%m.%Y').date()
    )

    # Создаём первую запись user_records с полным срезом параметров
    create_or_update_record(
        db,
        user.id,
        date.today(),
        weight=user_data['weight'],
        waist=user_data['waist'],
        neck=user_data['neck'],
        hip=user_data.get('hip'),
        chest=user_data.get('chest'),
        bicep=user_data.get('bicep'),
        thigh=user_data.get('thigh'),
        height=user_data['height'],
        goal=user_data['goal'],
        steps=user_data['steps'],
        sport_type=user_data['sport_type'],
        sport_freq=user_data['sport_freq'],
        step_multiplier=step_multiplier,
        bodyfat=bodyfat
    )
    db.close()

    # Показываем итоговые результаты (без КБЖУ и рекомендаций)
    await bot.send_message(
        user.id,
        get_final_results_text(user_data, bodyfat),
        parse_mode='Markdown'
    )

    # Показываем КБЖУ и рекомендации в одном сообщении
    kbju_explanation = get_kbju_explanation(user_data['goal'], kbju)
    await bot.send_message(
        user.id,
        kbju_explanation,
        parse_mode='Markdown'
    )

    # Ждём 1 минуту перед отправкой воронки
    await asyncio.sleep(60)

    # Воронка: фото, экспертный текст, кнопка
    with open('data/1.jpg', 'rb') as photo:
        await bot.send_photo(user.id, photo=photo)
    await bot.send_message(
        user.id,
        "💬 Хочешь не просто похудеть или набрать форму, а изменить свою жизнь комплексно?\n\n"
        "Эксперт Екатерина Юзефовна — профессиональный психолог и специалист по питанию с многолетним опытом.\n\n"
        "🔹 Поможет разобраться с причинами пищевого поведения\n"
        "🔹 Поддержит на каждом этапе — от работы с сознанием до подбора питания и активности\n"
        "🔹 Индивидуальный подход к твоим целям и особенностям\n"
        "🔹 Комплексное решение: психология, питание, движение, поддержка\n\n"
        "✨ Запишись на консультацию и начни свой путь к гармонии с собой и телом!",
        parse_mode='Markdown',
        reply_markup=get_funnel_keyboard()
    )
    
    await state.finish()

def register_user_info_handlers(dp: Dispatcher):
    """Регистрация обработчиков пользовательской информации"""
    # Обработчики текстовых сообщений
    dp.register_message_handler(process_name, state=UserInfoStates.name)
    dp.register_message_handler(process_birthday, state=UserInfoStates.birthday)
    dp.register_message_handler(process_height, state=UserInfoStates.height)
    dp.register_message_handler(process_weight, state=UserInfoStates.weight)
    dp.register_message_handler(process_waist, state=UserInfoStates.waist)
    dp.register_message_handler(process_neck, state=UserInfoStates.neck)
    dp.register_message_handler(process_hip, state=UserInfoStates.hip)
    dp.register_message_handler(process_chest, state=UserInfoStates.chest)
    dp.register_message_handler(process_bicep, state=UserInfoStates.bicep)
    dp.register_message_handler(process_thigh, state=UserInfoStates.thigh)
    
    # Обработчики callback-запросов
    dp.register_callback_query_handler(process_sex_callback, text_startswith='sex_', state=UserInfoStates.sex)
    dp.register_callback_query_handler(process_steps_callback, text_startswith='steps_', state=UserInfoStates.steps)
    dp.register_callback_query_handler(process_sport_callback, text_startswith='sport_', state=UserInfoStates.sport_type)
    dp.register_callback_query_handler(process_frequency_callback, text_startswith='freq_', state=UserInfoStates.sport_freq)
    dp.register_callback_query_handler(process_goal_callback, text_startswith='goal_', state=UserInfoStates.goal) 