def get_welcome_text() -> str:
    return (
        "Спасибо, что перешел, ты уже большой молодец! 🎉\n\n"
        "Давай пройдем небольшое тестирование, чтобы я мог составить расчет КБЖУ для твоих целей и процента жира. Дам полезные советы и рекомендации.\n\n"
        "Готов начать? 💪"
    )

def get_name_request() -> str:
    return """👤 Как вас зовут?

Введите ваше полное имя (ФИО)"""

def get_birthday_request() -> str:
    return """🎂 Когда вы родились?

Введите дату в формате ДД.ММ.ГГГГ
Например: 15.03.1990"""

def get_sex_request() -> str:
    return """👥 Выберите ваш пол:"""

def get_height_request() -> str:
    return """📏 Какой у вас рост?

Введите рост в сантиметрах (например: 175)"""

def get_weight_request() -> str:
    return """⚖️ Какой у вас вес?

Введите вес в килограммах (например: 70.5)"""

def get_steps_request() -> str:
    return """👟 Сколько шагов вы проходите в день?

Выберите ваш уровень активности:"""

def get_sport_request() -> str:
    return """🏃‍♂️ Занимаетесь ли вы спортом?

Выберите тип физической активности:"""

def get_frequency_request() -> str:
    return """📅 Как часто вы занимаетесь спортом?

Выберите частоту тренировок:"""

def get_waist_request() -> str:
    return """📐 Измерьте окружность талии

Введите значение в сантиметрах (например: 85)"""

def get_neck_request() -> str:
    return """📐 Измерьте окружность шеи

Введите значение в сантиметрах (например: 40)"""

def get_hip_request() -> str:
    return """📐 Измерьте окружность бёдер

Введите значение в сантиметрах (например: 95)"""

def get_goal_request() -> str:
    return """🎯 Какую цель вы преследуете?

Выберите вашу цель:"""

def get_goal_description(goal: str) -> str:
    descriptions = {
        'healthy': """🧘 Здоровое тело
Поддержание здоровья и хорошего самочувствия
Рекомендуется для большинства людей""",
        'athletic': """🏋 Спортивное тело
Набор мышечной массы и силы
Для тех, кто хочет стать сильнее""",
        'lean': """🔥 Сухое тело
Снижение процента жира
Для тех, кто хочет стать стройнее"""
    }
    return descriptions.get(goal, "Неизвестная цель")

def get_main_menu_text() -> str:
    return """🏠 Главное меню

Выберите действие:"""

def get_funnel_text() -> str:
    return """🎁 Специальное предложение!

Получите персональную консультацию по питанию и тренировкам от профессионального диетолога.

💬 Нажмите кнопку ниже, чтобы связаться с @dryuzefovna"""

def get_funnel_text_with_image() -> str:
    return """🎯 **Персональная консультация от специалиста**

Дорогой друг! 👋

Ты только что получил базовые рекомендации по питанию, но это только начало твоего пути к здоровому телу.

**Почему стоит обратиться к специалисту?**

🔹 **Индивидуальный подход** — твои особенности, аллергии, предпочтения
🔹 **Корректировка плана** — адаптация под твои результаты и изменения
🔹 **Поддержка и мотивация** — ты не один на этом пути
🔹 **Всесторонняя поддержка** — психологическая и физиологическая помощь

**Екатерина Юзефовна** — психолог и специалист по расстройствам пищевого поведения с разносторонним образованием, поможет тебе:
• Составить персональный план питания
• Настроить правильные отношения с едой
• Достичь твоих целей безопасно и эффективно
• Получить психологическую поддержку на пути к изменениям

💬 **Нажми кнопку ниже и получи персональную консультацию**

*Первая консультация — бесплатно!* ✨"""

def get_food_preferences_text() -> str:
    return """🍽 Предпочтения в еде

Расскажите о ваших пищевых предпочтениях:

✅ Что вы любите есть?
❌ Что не любите или не можете есть?

Введите ваши предпочтения:"""

def get_progress_text(weight_change: float, bodyfat_change: float, measurements_change: dict) -> str:
    text = "📈 Ваш прогресс:\n\n"
    
    if weight_change != 0:
        direction = "📈" if weight_change > 0 else "📉"
        text += f"{direction} Вес: {abs(weight_change):.1f} кг\n"
    
    if bodyfat_change != 0:
        direction = "📈" if bodyfat_change > 0 else "📉"
        text += f"{direction} % жира: {abs(bodyfat_change):.1f}%\n"
    
    for measurement, change in measurements_change.items():
        if change != 0:
            direction = "📈" if change > 0 else "📉"
            text += f"{direction} {measurement}: {abs(change):.1f} см\n"
    
    return text

def get_validation_error(error: str) -> str:
    return f"❌ Ошибка: {error}\n\nПопробуйте ещё раз!"

def get_success_message() -> str:
    return "✅ Данные успешно сохранены!"

def get_kbju_text(kbju: dict) -> str:
    return f"""🍽 Ваши КБЖУ:

🔥 Калории: {kbju['calories']} ккал
🥩 Белки: {kbju['protein']} г
🥑 Жиры: {kbju['fat']} г
🍞 Углеводы: {kbju['carbs']} г"""

def get_final_results_text(user_data: dict, bodyfat: float) -> str:
    from datetime import datetime
    goal_names = {
        'healthy': '🧘 Здоровое тело',
        'athletic': '🏋 Спортивное тело', 
        'lean': '🔥 Сухое тело'
    }
    sport_names = {
        'none': '❌ Нет спорта',
        'walking': '🚶 Ходьба',
        'running': '🏃 Бег',
        'strength': '🏋️‍♂️ Силовые тренировки',
        'yoga': '🧘 Йога',
        'swimming': '🏊 Плавание',
        'cycling': '🚴 Велосипед',
        'team': '⚽ Футбол/Баскетбол'
    }
    # Возраст
    birthday = user_data.get('birthday', '')
    age = ''
    if birthday:
        try:
            bdate = datetime.strptime(birthday, '%d.%m.%Y')
            today = datetime.today()
            age = today.year - bdate.year - ((today.month, today.day) < (bdate.month, bdate.day))
        except Exception as e:
            import logging
            logging.error(f"Error calculating age from birthday '{birthday}': {e}")
            age = ''
    text = f"""🎉 **Твои результаты готовы!**

📊 **Основные данные:**
👤 Имя: {user_data.get('name', 'Не указано')}
🎂 Дата рождения: {user_data.get('birthday', 'Не указано')}
🗓 Возраст: {age if age != '' else 'Не определён'}
👥 Пол: {'Мужской' if user_data.get('sex') == 'male' else 'Женский'}
📏 Рост: {user_data.get('height', 'Не указано')} см
⚖️ Вес: {user_data.get('weight', 'Не указано')} кг

🏃‍♂️ **Активность:**
👟 Шаги в день: {user_data.get('steps', 'Не указано')}
🏋️ Спорт: {sport_names.get(user_data.get('sport_type'), 'Не указано')}
📅 Частота: {user_data.get('sport_freq', 'Не указано')} раз в неделю

📐 **Обмеры:**
📏 Талия: {user_data.get('waist', 'Не указано')} см
📏 Шея: {user_data.get('neck', 'Не указано')} см"""
    if user_data.get('hip'):
        text += f"\n📏 Бёдра: {user_data.get('hip')} см"
    text += f"""

🎯 **Цель:** {goal_names.get(user_data.get('goal'), 'Не указана')}

📊 **Результаты расчётов:**
🔥 Процент жира: {bodyfat}%"""
    return text

def get_kbju_explanation(goal: str, kbju: dict) -> str:
    """
    Дружелюбное объяснение КБЖУ и советы по каждой цели
    """
    explanations = {
        'healthy': f"""
🧘 Мы рассчитали твой примерный КБЖУ для поддержания здоровья!

🔥 Калории: {kbju['calories']} ккал
🥩 Белки: {kbju['protein']} г
🥑 Жиры: {kbju['fat']} г
🍞 Углеводы: {kbju['carbs']} г

🧘 **Совет:**
Старайся питаться разнообразно и регулярно.
— Следи за балансом белков, жиров и углеводов.
— Не забывай про овощи и воду.
— Главное — стабильность и удовольствие от процесса!

Ты молодец! 🌟
""",
        'athletic': f"""
🏋️ Мы рассчитали твой примерный КБЖУ для набора мышечной массы!

🔥 Калории: {kbju['calories']} ккал
🥩 Белки: {kbju['protein']} г
🥑 Жиры: {kbju['fat']} г
🍞 Углеводы: {kbju['carbs']} г

🏋️ **Совет:**
Эти значения помогут тебе расти и становиться сильнее.
— Белки — для восстановления и роста мышц.
— Углеводы — для энергии на тренировки.
— Не забывай про регулярные тренировки и отдых!

Вперёд к результату! 🚀
""",
        'lean': f"""
🔥 Мы рассчитали твой примерный КБЖУ для снижения процента жира!

🔥 Калории: {kbju['calories']} ккал
🥩 Белки: {kbju['protein']} г
🥑 Жиры: {kbju['fat']} г
🍞 Углеводы: {kbju['carbs']} г

🔥 **Совет:**
С таким КБЖУ ты сможешь снижать процент жира, сохраняя мышцы.
— Не пропускай приёмы пищи, чтобы не замедлять обмен веществ.
— Следи за самочувствием и уровнем энергии.
— Не забывай про физическую активность!

Ты на правильном пути! 💪
"""
    }
    return explanations.get(goal, "Нет данных по цели") 