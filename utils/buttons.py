from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

def get_start_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для начала анкеты"""
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("🚀 Начать тестирование", callback_data="start_survey")
    )
    return keyboard

def get_sex_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора пола"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("👨 Мужской", callback_data="sex_male"),
        InlineKeyboardButton("👩 Женский", callback_data="sex_female")
    )
    return keyboard

def get_steps_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора количества шагов (группировка)"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("0-3000", callback_data="steps_0_3000"),
        InlineKeyboardButton("3000-5000", callback_data="steps_3000_5000")
    )
    keyboard.add(
        InlineKeyboardButton("5000-8000", callback_data="steps_5000_8000"),
        InlineKeyboardButton("8000-10000", callback_data="steps_8000_10000")
    )
    keyboard.add(
        InlineKeyboardButton("10000+", callback_data="steps_10000_plus")
    )
    return keyboard

def get_sport_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора типа спорта (более понятные примеры)"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("❌ Не занимаюсь", callback_data="sport_none"),
        InlineKeyboardButton("🚶 Ходьба/Прогулки", callback_data="sport_walking")
    )
    keyboard.add(
        InlineKeyboardButton("🏃 Бег/Кардио", callback_data="sport_running"),
        InlineKeyboardButton("🏋️ Тренажерный зал", callback_data="sport_strength")
    )
    keyboard.add(
        InlineKeyboardButton("🧘 Йога/Пилатес", callback_data="sport_yoga"),
        InlineKeyboardButton("🏊 Плавание", callback_data="sport_swimming")
    )
    keyboard.add(
        InlineKeyboardButton("🚴 Велосипед", callback_data="sport_cycling"),
        InlineKeyboardButton("⚽ Футбол/Баскетбол", callback_data="sport_team")
    )
    return keyboard

def get_frequency_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора частоты тренировок"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("1-2 раза", callback_data="freq_1_2"),
        InlineKeyboardButton("3-4 раза", callback_data="freq_3_4")
    )
    keyboard.add(
        InlineKeyboardButton("5-6 раз", callback_data="freq_5_6"),
        InlineKeyboardButton("Ежедневно", callback_data="freq_daily")
    )
    return keyboard

def get_goal_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора цели"""
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("🧘 Здоровое тело", callback_data="goal_healthy")
    )
    keyboard.add(
        InlineKeyboardButton("🏋 Спортивное тело", callback_data="goal_athletic")
    )
    keyboard.add(
        InlineKeyboardButton("🔥 Сухое тело", callback_data="goal_lean")
    )
    return keyboard

def get_funnel_keyboard() -> InlineKeyboardMarkup:
    """Красивая кнопка для записи на консультацию"""
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("✨ Записаться на консультацию", url="https://t.me/dryuzefovna")
    )
    return keyboard

def get_back_keyboard() -> InlineKeyboardMarkup:
    """Кнопка назад"""
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("⬅️ Назад", callback_data="back")
    )
    return keyboard

def get_confirm_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура подтверждения"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("✅ Да", callback_data="confirm_yes"),
        InlineKeyboardButton("❌ Нет", callback_data="confirm_no")
    )
    return keyboard

def get_main_menu_inline_keyboard() -> InlineKeyboardMarkup:
    """Главное меню через inline-кнопки (обновленное)"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("📊 Мои данные", callback_data="menu_my_data"),
        InlineKeyboardButton("📈 Прогресс", callback_data="menu_progress")
    )
    keyboard.add(
        InlineKeyboardButton("📝 Новые замеры", callback_data="menu_new_measurements"),
        InlineKeyboardButton("🍎 Предпочтения", callback_data="menu_food_prefs")
    )
    keyboard.add(
        InlineKeyboardButton("💬 Консультация", callback_data="menu_consultation")
    )
    return keyboard 