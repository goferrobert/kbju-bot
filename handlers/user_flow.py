from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler
from services.calculator import calculate_kbju
from funnel.invite import send_consultation_invite

GENDER, WEIGHT, HEIGHT, AGE, ACTIVITY, TARGET = range(6)

main_menu_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔢 Хочу получить расчёт своего КБЖУ", callback_data="start_kbju")]
])

async def start(update, context):
    await update.message.reply_text(
        "Добро пожаловать! Этот бот создан для расчёта КБЖУ, поехали!",
        reply_markup=main_menu_keyboard
    )
    return ConversationHandler.END

async def handle_start_kbju(update, context):
    print("🚀 handle_start_kbju вызван")
    await update.callback_query.answer()
    sex_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🚹 Мужчина", callback_data="sex_male"),
         InlineKeyboardButton("🚺 Женщина", callback_data="sex_female")]
    ])
    await update.callback_query.message.reply_text(
        "Выберите ваш пол:",
        reply_markup=sex_keyboard
    )
    return GENDER

async def handle_sex_selection(update, context):
    await update.callback_query.answer()
    data = update.callback_query.data

    if data == "sex_male":
        context.user_data["sex"] = "мужчина"
        sex_label = "🚹 Мужчина"
    elif data == "sex_female":
        context.user_data["sex"] = "женщина"
        sex_label = "🚺 Женщина"

    # подтверждение выбора
    await update.callback_query.message.reply_text(f"Вы выбрали: {sex_label} ✅")

    # далее — следующий шаг
    await update.callback_query.message.reply_text(
        "Введите ваш вес в килограммах (кг) ⚖️\nНапример: 68.5"
    )
    return WEIGHT


async def get_weight(update, context):

    print("⚖️ get_weight вызван:", update.message.text)
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

        activity_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("1️⃣", callback_data="activity_1"),
             InlineKeyboardButton("2️⃣", callback_data="activity_2"),
             InlineKeyboardButton("3️⃣", callback_data="activity_3")],
            [InlineKeyboardButton("4️⃣", callback_data="activity_4"),
             InlineKeyboardButton("5️⃣", callback_data="activity_5")]
        ])

        await update.message.reply_text(
            "Выбери уровень физической активности (нажми на кнопку): 🏃‍♀️\n\n"
            "1️⃣ — Минимальный\nпочти нет активности, сидячая работа, редкие прогулки\n\n"
            "2️⃣ — Лёгкий\n1–3 тренировки в неделю, лёгкая подвижность\n\n"
            "3️⃣ — Средний\n3–5 тренировок в неделю, регулярная активность\n\n"
            "4️⃣ — Высокий\nинтенсивные тренировки почти каждый день\n\n"
            "5️⃣ — Очень высокий\nежедневные тренировки или тяжёлый физический труд",
            reply_markup=activity_keyboard
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
    try:
        target = float(update.message.text)
    except ValueError:
        await update.message.reply_text("Пожалуйста, введи целевой вес числом:")
        return TARGET

    context.user_data["target_weight"] = target
    result = calculate_kbju(context.user_data)
    await update.message.reply_text(result)
    await send_consultation_invite(update, context)
    return ConversationHandler.END

async def handle_activity_selection(update, context):
    await update.callback_query.answer()
    data = update.callback_query.data
    level = int(data.split("_")[1])
    context.user_data["activity"] = level

    # краткое описание активности
    activity_labels = {
        1: "1️⃣ — Минимальный",
        2: "2️⃣ — Лёгкий",
        3: "3️⃣ — Средний",
        4: "4️⃣ — Высокий",
        5: "5️⃣ — Очень высокий"
    }

    label = activity_labels.get(level, f"{level}")
    await update.callback_query.message.reply_text(f"Вы выбрали уровень активности: {label} ✅")

    await update.callback_query.message.reply_text(
        "Теперь введи свой целевой вес (в кг) 🎯\nНапример: 60"
    )
    return TARGET