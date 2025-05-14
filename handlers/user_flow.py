from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler
from services.calculator import calculate_kbju
from funnel.invite import send_consultation_invite

GENDER, WEIGHT, HEIGHT, AGE, ACTIVITY, TARGET = range(6)

async def start(update, context):
    keyboard = [["Хочу получить расчёт своего КБЖУ"]]
    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        "Добро пожаловать! Этот бот создан для расчёта КБЖУ, поехали!",
        reply_markup=markup
    )
    return GENDER

async def get_gender(update, context):
    keyboard = [["Мужчина", "Женщина"]]
    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    text = update.message.text.lower()
    if "муж" in text:
        context.user_data["sex"] = "мужчина"
    elif "жен" in text:
        context.user_data["sex"] = "женщина"
    else:
        await update.message.reply_text("Пожалуйста, выбери: мужчина или женщина.", reply_markup=markup)
        return GENDER
    await update.message.reply_text(
        "Введите ваш вес в килограммах (кг) ⚖️\nНапример: 68.5",
        reply_markup=ReplyKeyboardRemove()
    )
    return WEIGHT

async def get_weight(update, context):
    try:
        context.user_data["weight"] = float(update.message.text)
        await update.message.reply_text("Введите ваш рост в сантиметрах (см) 📏\nНапример: 172")
        return HEIGHT
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите вес числом:")
        return WEIGHT

async def get_height(update, context):
    try:
        context.user_data["height"] = float(update.message.text)
        await update.message.reply_text("Сколько вам лет:")
        return AGE
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите рост числом:")
        return HEIGHT

async def get_age(update, context):
    try:
        context.user_data["age"] = int(update.message.text)
        keyboard = [["1", "2", "3", "4", "5"]]
        markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(
            "Выбери уровень физической активности (введи цифру от 1 до 5): 🏃‍♀️\n\n"
            "1️⃣ — Минимальный\nпочти нет активности, сидячая работа, редкие прогулки\n\n"
            "2️⃣ — Лёгкий\n1–3 тренировки в неделю, лёгкая подвижность\n\n"
            "3️⃣ — Средний\n3–5 тренировок в неделю, регулярная активность\n\n"
            "4️⃣ — Высокий\nинтенсивные тренировки почти каждый день\n\n"
            "5️⃣ — Очень высокий\nежедневные тренировки или тяжёлый физический труд",
            reply_markup=markup
        )
        return ACTIVITY
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите возраст числом:")
        return AGE

async def get_activity(update, context):
    try:
        level = int(update.message.text)
        if level < 1 or level > 5:
            raise ValueError
        context.user_data["activity"] = level
        await update.message.reply_text(
            "Теперь введи свой целевой вес (в кг) 🎯\nНапример: 60",
            reply_markup=ReplyKeyboardRemove()
        )
        return TARGET
    except ValueError:
        await update.message.reply_text("Пожалуйста, выбери цифру от 1 до 5:")
        return ACTIVITY

async def get_target(update, context):
    # сначала пробуем распарсить число
    try:
        target = float(update.message.text)
    except ValueError:
        await update.message.reply_text("Пожалуйста, введи целевой вес числом:")
        return TARGET

    # дальше — гарантированно расчёт и завершение
    context.user_data["target_weight"] = target
    result = calculate_kbju(context.user_data)
    await update.message.reply_text(result)
    await send_consultation_invite(update, context)
    return ConversationHandler.END
