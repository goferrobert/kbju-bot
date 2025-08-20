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

# Универсальная функция для запросов измерений
def get_measurement_request(measurement_type: str) -> str:
    """Универсальная функция для запросов измерений"""
    measurement_config = {
        'waist': {
            'emoji': '📐',
            'name': 'окружность талии',
            'example': '85'
        },
        'neck': {
            'emoji': '📐',
            'name': 'окружность шеи',
            'example': '40'
        },
        'hip': {
            'emoji': '📐',
            'name': 'окружность бёдер',
            'example': '95'
        },
        'chest': {
            'emoji': '📐',
            'name': 'окружность груди',
            'example': '100'
        },
        'bicep': {
            'emoji': '💪',
            'name': 'окружность плеча',
            'example': '35'
        },
        'thigh': {
            'emoji': '🦵',
            'name': 'окружность бедра',
            'example': '60'
        },
        'wrist': {
            'emoji': '👋',
            'name': 'окружность запястья',
            'example': '18'
        },
        'calf': {
            'emoji': '🦵',
            'name': 'окружность голени',
            'example': '38'
        },
        'forearm': {
            'emoji': '💪',
            'name': 'окружность предплечья',
            'example': '30'
        },
        'abdomen': {
            'emoji': '📐',
            'name': 'окружность живота',
            'example': '85'
        }
    }
    
    config = measurement_config.get(measurement_type, {})
    emoji = config.get('emoji', '📐')
    name = config.get('name', measurement_type)
    example = config.get('example', '50')
    
    return f"""{emoji} Измерьте {name}

Введите значение в сантиметрах (например: {example})"""

# Специальные функции для обратной совместимости
def get_waist_request() -> str:
    return get_measurement_request('waist')

def get_neck_request() -> str:
    return get_measurement_request('neck')

def get_hip_request() -> str:
    return get_measurement_request('hip')

def get_chest_request() -> str:
    return get_measurement_request('chest')

def get_bicep_request() -> str:
    return get_measurement_request('bicep')

def get_thigh_request() -> str:
    return get_measurement_request('thigh')

def get_wrist_request() -> str:
    return get_measurement_request('wrist')

def get_calf_request() -> str:
    return get_measurement_request('calf')

def get_forearm_request() -> str:
    return get_measurement_request('forearm')

def get_abdomen_request() -> str:
    return get_measurement_request('abdomen')

def get_sleep_request() -> str:
    return """😴 Сколько часов вы спите в день?

Введите количество часов (например: 7.5)"""

def get_stress_request() -> str:
    return """😰 Какой у вас уровень стресса?

Выберите уровень:"""

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
• Персональный план питания под твои цели
• Корректировка программы тренировок
• Мониторинг прогресса и поддержка
• Ответы на все вопросы в реальном времени

**Что входит в консультацию:**
✅ Анализ твоих текущих показателей
✅ Составление индивидуального плана питания
✅ Рекомендации по тренировкам
✅ Поддержка и мотивация
✅ Корректировка плана по мере прогресса

**Стоимость: 5000₽/месяц**

💬 Нажми кнопку ниже, чтобы связаться с @dryuzefovna и получить персональную консультацию!"""

def get_validation_error(message: str) -> str:
    return f"❌ Ошибка: {message}\n\nПопробуйте еще раз."

def get_final_results_text(user_data: dict, bodyfat: float, kbju: dict) -> str:
    """Формирование финального текста с результатами"""
    text = f"""🎉 **Результаты расчета:**

📊 **Ваши данные:**
• Вес: {user_data.get('weight', 'N/A')} кг
• Рост: {user_data.get('height', 'N/A')} см
• Талия: {user_data.get('waist', 'N/A')} см
• Шея: {user_data.get('neck', 'N/A')} см"""

    if user_data.get('hip'):
        text += f"\n• Бёдра: {user_data['hip']} см"
    
    text += f"""

🔥 **Процент жира:** {bodyfat:.1f}%

📈 **Ваши КБЖУ:**
• Калории: {kbju['calories']} ккал
• Белки: {kbju['protein']} г
• Жиры: {kbju['fat']} г
• Углеводы: {kbju['carbs']} г

💡 **Рекомендации:**
• Старайтесь есть {kbju['protein']} г белка в день
• Пейте достаточно воды (2-3 литра)
• Следите за прогрессом каждые 2 недели
• Не забывайте про физическую активность"""

    return text

def get_kbju_explanation() -> str:
    return """📚 **Что такое КБЖУ?**

**К** - Калории (общая энергетическая ценность)
**Б** - Белки (строительный материал для мышц)
**Ж** - Жиры (источник энергии и гормонов)
**У** - Углеводы (основной источник энергии)

**Почему это важно?**
• Правильное соотношение КБЖУ помогает достичь целей
• Белок сохраняет мышечную массу
• Жиры важны для гормонального баланса
• Углеводы дают энергию для тренировок

**Как применять:**
1. Старайтесь набирать калории из правильных продуктов
2. Ешьте белок с каждым приемом пищи
3. Не бойтесь полезных жиров
4. Выбирайте сложные углеводы"""

def get_comprehensive_metrics_text(metrics: dict) -> str:
    """Текст с комплексными метриками"""
    basic = metrics.get('basic_metrics', {})
    metabolic = metrics.get('metabolic_metrics', {})
    classifications = metrics.get('classifications', {})
    
    text = f"""📊 **Комплексный анализ:**

**Основные показатели:**
• BMI: {basic.get('bmi', 'N/A')}
• Соотношение талия/бедра: {basic.get('whr', 'N/A')}
• Мышечная масса: {basic.get('lbm', 'N/A')} кг
• Индекс мышечной массы: {basic.get('ffmi', 'N/A')}

**Метаболические показатели:**
• Базовый обмен веществ: {metabolic.get('bmr', 'N/A')} ккал
• Общий расход энергии: {metabolic.get('tdee', 'N/A')} ккал
• Метаболический возраст: {metabolic.get('metabolic_age', 'N/A')} лет

**Классификация:**
• Тип телосложения: {classifications.get('body_type', 'N/A')}
• Категория по жиру: {classifications.get('bodyfat_category', 'N/A')}"""

    return text

def get_metabolic_analysis_text(metrics: dict) -> str:
    """Текст с анализом метаболизма"""
    metabolic = metrics.get('metabolic_metrics', {})
    targets = metrics.get('targets', {})
    
    text = f"""🔥 **Анализ метаболизма:**

**Ваш метаболизм:**
• Базовый обмен веществ: {metabolic.get('bmr', 'N/A')} ккал/день
• Общий расход энергии: {metabolic.get('tdee', 'N/A')} ккал/день
• Метаболический возраст: {metabolic.get('metabolic_age', 'N/A')} лет

**Рекомендации по калориям:**
• Для поддержания веса: {metabolic.get('tdee', 'N/A')} ккал
• Для снижения веса: {targets.get('target_calories', 'N/A')} ккал
• Для набора массы: {int(metabolic.get('tdee', 0) * 1.1)} ккал

**Советы для ускорения метаболизма:**
• Ешьте каждые 3-4 часа
• Пейте холодную воду
• Занимайтесь силовыми тренировками
• Высыпайтесь (7-9 часов)
• Ешьте достаточно белка"""

    return text

def get_body_composition_text(metrics: dict) -> str:
    """Текст с анализом состава тела"""
    basic = metrics.get('basic_metrics', {})
    targets = metrics.get('targets', {})
    
    ideal_weights = targets.get('ideal_weights', {})
    target_bodyfat = targets.get('target_bodyfat', {})
    
    text = f"""🏗️ **Анализ состава тела:**

**Текущие показатели:**
• Мышечная масса: {basic.get('lbm', 'N/A')} кг
• Индекс мышечной массы: {basic.get('ffmi', 'N/A')}
• Соотношение талия/бедра: {basic.get('whr', 'N/A')}

**Идеальный вес (разные формулы):**
• Формула Брока: {ideal_weights.get('broca', 'N/A')} кг
• Формула Лоренца: {ideal_weights.get('lorenz', 'N/A')} кг
• Формула Девина: {ideal_weights.get('devine', 'N/A')} кг
• Среднее значение: {ideal_weights.get('average', 'N/A')} кг

**Целевой процент жира:**
• Минимальный: {target_bodyfat.get('min', 'N/A')}%
• Оптимальный: {target_bodyfat.get('optimal', 'N/A')}%
• Максимальный: {target_bodyfat.get('max', 'N/A')}%

**Рекомендации:**
• Фокусируйтесь на сохранении мышечной массы
• Постепенно снижайте процент жира
• Регулярно делайте замеры
• Тренируйтесь с отягощениями"""

    return text

def get_safety_warnings_text(safety_data: dict) -> str:
    """Текст с предупреждениями безопасности"""
    if not safety_data.get('warnings'):
        return ""
    
    text = "⚠️ **ВНИМАНИЕ! Важные предупреждения:**\n\n"
    
    for warning in safety_data['warnings']:
        text += f"• {warning}\n"
    
    if safety_data.get('recommendations'):
        text += "\n**Рекомендации:**\n"
        for rec in safety_data['recommendations']:
            text += f"• {rec}\n"
    
    return text

def get_adaptive_recommendations_text(adaptive_data: dict) -> str:
    """Текст с адаптивными рекомендациями"""
    text = f"""🎯 **Персональные рекомендации:**

**Приоритет:** {adaptive_data.get('priority', 'N/A')}

**Сообщение:** {adaptive_data.get('message', 'N/A')}

**Рекомендации по питанию:**
• Калории: {adaptive_data.get('calories', 'N/A')}
• Белок: {adaptive_data.get('protein', 'N/A')}

**Важно помнить:** {adaptive_data.get('caution', 'N/A')}"""

    return text

def get_kbju_text(kbju: dict) -> str:
    """Текст с КБЖУ для обратной совместимости"""
    return f"""🍽 Ваши КБЖУ:

🔥 Калории: {kbju['calories']} ккал
🥩 Белки: {kbju['protein']} г
🥑 Жиры: {kbju['fat']} г
🍞 Углеводы: {kbju['carbs']} г"""

def get_food_preferences_text() -> str:
    """Текст для предпочтений в еде для обратной совместимости"""
    return """🍽 Предпочтения в еде

Расскажите о ваших пищевых предпочтениях:

✅ Что вы любите есть?
❌ Что не любите или не можете есть?

Введите ваши предпочтения:""" 