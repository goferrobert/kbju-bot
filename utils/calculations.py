import math
import logging

def calculate_bodyfat(user_data: dict):
    """
    Расчёт % жира по методу US Navy с корректировкой для женщин
    
    Формула US Navy может давать завышенные результаты для женщин с нормальным весом
    и хорошими пропорциями. Поэтому применяем корректировку на основе:
    1. BMI - для женщин с нормальным весом снижаем результат
    2. Соотношение талия/бедра - для хороших пропорций дополнительная корректировка
    
    ВНИМАНИЕ: Эта функция устарела. Используйте calculate_bodyfat_precise для точного расчета.
    """
    logging.info(f"calculate_bodyfat: input={user_data}")
    sex = user_data.get('sex')
    waist = user_data.get('waist')
    neck = user_data.get('neck')
    hip = user_data.get('hip')
    height = user_data.get('height')
    weight = user_data.get('weight')
    
    if sex == 'male':
        if not all([waist, neck, height]):
            return None
        bodyfat = 86.010 * math.log10(waist - neck) - 70.041 * math.log10(height) + 36.76
    else:  # female
        if not all([waist, neck, hip, height, weight]):
            return None
        
        # Основная формула US Navy
        bodyfat_navy = 163.205 * math.log10(waist + hip - neck) - 97.684 * math.log10(height) - 78.387
        
        # Альтернативный расчет по BMI и обхватам для корректировки
        height_m = height / 100
        bmi = weight / (height_m * height_m)
        
        # Расчет по соотношению обхватов
        waist_to_hip_ratio = waist / hip if hip > 0 else 0.8
        
        # Корректировка на основе BMI и соотношения обхватов
        # Для женщин с нормальным весом формула US Navy завышает результат
        if bmi < 18.5:  # Недостаточный вес
            correction = -8
        elif bmi < 22:  # Нормальный вес (нижняя граница)
            correction = -10
        elif bmi < 25:  # Нормальный вес (верхняя граница)
            correction = -7
        elif bmi < 30:  # Избыточный вес
            correction = -3
        else:  # Ожирение
            correction = 0
        
        # Дополнительная корректировка по соотношению талия/бедра
        # Хорошие пропорции указывают на более низкий процент жира
        if waist_to_hip_ratio < 0.75:  # Отличное соотношение
            correction += -5
        elif waist_to_hip_ratio < 0.8:  # Хорошее соотношение
            correction += -3
        elif waist_to_hip_ratio > 0.85:  # Высокое соотношение
            correction += 2
        
        # Применяем корректировку
        bodyfat = bodyfat_navy + correction
        
        # Ограничиваем результат разумными пределами
        bodyfat = max(12, min(45, bodyfat))  # Минимум 12%, максимум 45% для женщин
    
    logging.info(f"calculate_bodyfat: result={bodyfat}")
    return round(max(0, min(100, bodyfat)), 1)

def calculate_kbju(user_data: dict, bodyfat: float):
    """
    Расчёт КБЖУ по методу Katch-McArdle
    """
    logging.info(f"calculate_kbju: input={user_data}, bodyfat={bodyfat}")
    weight = user_data.get('weight')
    step_multiplier = user_data.get('step_multiplier', 1.2)  # значение по умолчанию
    sport_type = user_data.get('sport_type', 'none')
    goal = user_data.get('goal', 'healthy')
    
    if not weight or not bodyfat:
        return None
    
    # 1. LBM = вес * (1 - жир/100)
    lbm = weight * (1 - bodyfat / 100)
    
    # 2. BMR = 370 + 21.6 * LBM
    bmr = 370 + 21.6 * lbm
    
    # 3. Спортивный коэффициент
    sport_coefficients = {
        'none': 0,
        'walking': 200,
        'running': 400,
        'strength': 600,
        'yoga': 200,
        'swimming': 400,
        'cycling': 300,
        'team': 500
    }
    sport_calories = sport_coefficients.get(sport_type.lower(), 0)
    
    # 4. TDEE = BMR * шаговый множитель + спорт коэффициент
    tdee = bmr * step_multiplier + sport_calories
    
    # 5. По цели
    if goal == 'healthy':
        calories = tdee
    elif goal == 'athletic':
        calories = tdee * 1.05
    elif goal == 'lean':
        # Проверка ограничений для сушки
        if bodyfat < 7:  # для мужчин
            return None  # сушка запрещена
        calories = tdee * 0.90
    else:
        calories = tdee
    
    # Расчёт макронутриентов
    protein_g = min(2.2 * weight, calories * 0.3 / 4)  # белок ≤ 2.2 г/кг
    fat_g = calories * 0.25 / 9  # 25% жиры
    carbs_g = max(100, (calories - protein_g * 4 - fat_g * 9) / 4)  # углеводы ≥ 100 г
    
    logging.info(f"calculate_kbju: result={{'calories': round(calories), 'protein': round(protein_g), 'fat': round(fat_g), 'carbs': round(carbs_g)}}")
    return {
        'calories': round(calories),
        'protein': round(protein_g),
        'fat': round(fat_g),
        'carbs': round(carbs_g)
    }

def calculate_step_multiplier(steps: str):
    """
    Расчёт множителя активности по шагам
    """
    logging.info(f"calculate_step_multiplier: steps={steps}")
    if steps == "10000+" or steps == "10000_plus":
        return 1.5
    elif steps == "8000-10000" or steps == "8000_10000":
        return 1.4
    elif steps == "5000-8000" or steps == "5000_8000":
        return 1.3
    elif steps == "3000-5000" or steps == "3000_5000":
        return 1.2
    elif steps == "0-3000" or steps == "0_3000":
        return 1.1
    else:  # значение по умолчанию
        return 1.2

def calculate_bodyfat_precise(user_data: dict) -> float:
    """
    Точный расчет процента жира с учетом спортивной подготовки и типа телосложения
    
    Использует комбинацию методов:
    1. US Navy метод (базовый)
    2. Корректировка по BMI
    3. Учет спортивной подготовки
    4. Анализ мышечной массы по новым замерам
    5. Тип телосложения
    """
    logging.info(f"calculate_bodyfat_precise: input={user_data}")
    
    sex = user_data.get('sex')
    waist = user_data.get('waist')
    neck = user_data.get('neck')
    hip = user_data.get('hip')
    height = user_data.get('height')
    weight = user_data.get('weight')
    
    # Извлекаем дополнительные переменные
    sport_type = user_data.get('sport_type', 'none')
    sport_freq = user_data.get('sport_freq', '0')
    chest = user_data.get('chest')
    bicep = user_data.get('bicep')
    thigh = user_data.get('thigh')
    
    # Базовый расчет по US Navy
    if sex == 'male':
        if not all([waist, neck, height]):
            return None
        bodyfat_navy = 86.010 * math.log10(waist - neck) - 70.041 * math.log10(height) + 36.76
    else:  # female
        if not all([waist, neck, hip, height]):
            return None
        bodyfat_navy = 163.205 * math.log10(waist + hip - neck) - 97.684 * math.log10(height) - 78.387
    
    # Корректировка по BMI
    height_m = height / 100
    bmi = weight / (height_m * height_m)
    
    bmi_correction = 0
    if sex == 'female':
        if bmi < 18.5:  # Недостаточный вес
            bmi_correction = -8
        elif bmi < 22:  # Нормальный вес (нижняя граница)
            bmi_correction = -10
        elif bmi < 25:  # Нормальный вес (верхняя граница)
            bmi_correction = -7
        elif bmi < 30:  # Избыточный вес
            bmi_correction = -3
        else:  # Ожирение
            bmi_correction = 0
    else:  # male
        if bmi < 18.5:
            bmi_correction = -5
        elif bmi < 22:
            bmi_correction = -7
        elif bmi < 25:
            bmi_correction = -4
        elif bmi < 30:
            bmi_correction = -1
        else:
            bmi_correction = 0
    
    # Корректировка по спортивной подготовке
    sport_correction = 0
    if sport_type in ['strength', 'running', 'swimming']:
        if sport_freq == '3':
            sport_correction = -3
        elif sport_freq == '4':
            sport_correction = -5
        elif sport_freq == '5':
            sport_correction = -7
        elif sport_freq == '6':
            sport_correction = -9
    elif sport_type in ['walking', 'yoga', 'cycling']:
        if sport_freq in ['3', '4', '5']:
            sport_correction = -2
    
    # Корректировка по новым замерам (если доступны)
    measurement_correction = 0
    if all([chest, bicep, thigh]):
        # Анализ мышечной массы по замерам
        if sex == 'male':
            # Для мужчин: анализ соотношения замеров
            chest_to_waist = chest / waist if waist > 0 else 1.1
            bicep_to_neck = bicep / neck if neck > 0 else 0.6
            thigh_to_waist = thigh / waist if waist > 0 else 0.7
            
            if chest_to_waist > 1.15 and bicep_to_neck > 0.65:
                measurement_correction = -4  # Хорошая мышечная масса
            elif chest_to_waist > 1.1 and bicep_to_neck > 0.6:
                measurement_correction = -2
        else:  # female
            # Для женщин: анализ пропорций
            waist_to_hip = waist / hip if hip > 0 else 0.8
            chest_to_waist = chest / waist if waist > 0 else 1.0
            
            if waist_to_hip < 0.75 and chest_to_waist > 1.0:
                measurement_correction = -5  # Отличные пропорции
            elif waist_to_hip < 0.8 and chest_to_waist > 0.95:
                measurement_correction = -3
            elif waist_to_hip > 0.85:
                measurement_correction = 2
    
    # Применяем все корректировки
    bodyfat = bodyfat_navy + bmi_correction + sport_correction + measurement_correction
    
    # Ограничиваем результат разумными пределами
    if sex == 'female':
        bodyfat = max(12, min(45, bodyfat))  # 12-45% для женщин
    else:
        bodyfat = max(5, min(40, bodyfat))   # 5-40% для мужчин
    
    logging.info(f"calculate_bodyfat_precise: result={bodyfat}")
    return round(bodyfat, 1) 

def calculate_bmi(weight: float, height: int) -> float:
    """
    Расчет индекса массы тела (BMI)
    """
    height_m = height / 100
    bmi = weight / (height_m * height_m)
    return round(bmi, 1)

def calculate_whr(waist: float, hip: float) -> float:
    """
    Расчет соотношения талии к бедрам (Waist-to-Hip Ratio)
    """
    if hip > 0:
        return round(waist / hip, 2)
    return None

def calculate_lbm(weight: float, bodyfat: float) -> float:
    """
    Расчет мышечной массы (Lean Body Mass)
    """
    lbm = weight * (1 - bodyfat / 100)
    return round(lbm, 1)

def calculate_ffmi(weight: float, height: int, bodyfat: float) -> float:
    """
    Расчет индекса мышечной массы (Fat-Free Mass Index)
    """
    height_m = height / 100
    lbm = weight * (1 - bodyfat / 100)
    ffmi = lbm / (height_m * height_m)
    return round(ffmi, 1)

def calculate_bmr(weight: float, height: int, age: int, sex: str) -> int:
    """
    Расчет базового обмена веществ (BMR) по формуле Миффлина-Сан Жеора
    """
    height_cm = height
    if sex == 'male':
        bmr = 10 * weight + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height_cm - 5 * age - 161
    return round(bmr)

def calculate_tdee(bmr: int, step_multiplier: float, sport_type: str, sport_freq: str) -> int:
    """
    Расчет общего дневного расхода энергии (TDEE)
    """
    # Спортивные коэффициенты
    sport_coefficients = {
        'none': 0,
        'walking': 200,
        'running': 400,
        'strength': 600,
        'yoga': 200,
        'swimming': 400,
        'cycling': 300,
        'team': 500
    }
    sport_calories = sport_coefficients.get(sport_type.lower(), 0)
    
    # Частота спорта влияет на общий расход
    freq_multiplier = {
        '1': 0.3,
        '2': 0.5,
        '3': 0.7,
        '4': 0.8,
        '5': 0.9,
        '6': 1.0
    }
    sport_multiplier = freq_multiplier.get(sport_freq, 0.5)
    
    tdee = bmr * step_multiplier + sport_calories * sport_multiplier
    return round(tdee)

def get_body_type(bmi: float, whr: float, ffmi: float, sex: str) -> str:
    """
    Определение типа телосложения
    """
    if sex == 'male':
        if bmi < 18.5 and ffmi < 18:
            return "эктоморф"
        elif bmi > 25 and ffmi > 22:
            return "эндоморф"
        else:
            return "мезоморф"
    else:  # female
        if bmi < 18.5 and ffmi < 15:
            return "эктоморф"
        elif bmi > 25 and ffmi > 18:
            return "эндоморф"
        else:
            return "мезоморф"

def get_metabolic_age(bmr: int, age: int, sex: str) -> int:
    """
    Расчет метаболического возраста
    """
    # Средние значения BMR по возрастам (приблизительно)
    avg_bmr_by_age = {
        'male': {
            20: 1800, 25: 1750, 30: 1700, 35: 1650, 40: 1600,
            45: 1550, 50: 1500, 55: 1450, 60: 1400, 65: 1350
        },
        'female': {
            20: 1500, 25: 1450, 30: 1400, 35: 1350, 40: 1300,
            45: 1250, 50: 1200, 55: 1150, 60: 1100, 65: 1050
        }
    }
    
    avg_bmr = avg_bmr_by_age[sex]
    closest_age = min(avg_bmr.keys(), key=lambda x: abs(avg_bmr[x] - bmr))
    return closest_age

def get_bodyfat_category(bodyfat: float, sex: str) -> str:
    """
    Определение категории по проценту жира
    """
    if sex == 'male':
        if bodyfat < 10:
            return "спортивная"
        elif bodyfat < 15:
            return "фитнес"
        elif bodyfat < 20:
            return "средняя"
        else:
            return "высокая"
    else:  # female
        if bodyfat < 18:
            return "спортивная"
        elif bodyfat < 25:
            return "фитнес"
        elif bodyfat < 32:
            return "средняя"
        else:
            return "высокая"

def calculate_ideal_weight(height: int, sex: str, body_type: str) -> dict:
    """
    Расчет идеального веса по разным формулам
    """
    height_m = height / 100
    
    # Формула Брока
    broca = height - 100
    if sex == 'female':
        broca *= 0.9
    
    # Формула Лоренца
    if sex == 'male':
        lorenz = height - 100 - (height - 150) / 4
    else:
        lorenz = height - 100 - (height - 150) / 2
    
    # Формула Девина
    if sex == 'male':
        devine = 50 + 2.3 * (height_m * 100 - 152.4)
    else:
        devine = 45.5 + 2.3 * (height_m * 100 - 152.4)
    
    # Корректировка по типу телосложения
    if body_type == "эктоморф":
        broca *= 0.9
        lorenz *= 0.9
        devine *= 0.9
    elif body_type == "эндоморф":
        broca *= 1.1
        lorenz *= 1.1
        devine *= 1.1
    
    return {
        'broca': round(broca, 1),
        'lorenz': round(lorenz, 1),
        'devine': round(devine, 1),
        'average': round((broca + lorenz + devine) / 3, 1)
    }

def get_target_bodyfat(goal: str, sex: str) -> dict:
    """
    Определение целевого процента жира для разных целей
    """
    if sex == 'male':
        targets = {
            'healthy': {'min': 10, 'max': 20, 'optimal': 15},
            'athletic': {'min': 6, 'max': 15, 'optimal': 10},
            'lean': {'min': 8, 'max': 12, 'optimal': 10}
        }
    else:  # female
        targets = {
            'healthy': {'min': 18, 'max': 28, 'optimal': 23},
            'athletic': {'min': 14, 'max': 22, 'optimal': 18},
            'lean': {'min': 16, 'max': 20, 'optimal': 18}
        }
    
    return targets.get(goal, targets['healthy'])

def safety_checks(user_data: dict, calculated_metrics: dict) -> dict:
    """
    Проверки безопасности для разных категорий пользователей
    """
    weight = user_data.get('weight')
    height = user_data.get('height')
    sex = user_data.get('sex')
    bodyfat = calculated_metrics.get('bodyfat')
    bmi = calculated_metrics.get('bmi')
    
    warnings = []
    recommendations = []
    is_dangerous = False
    
    # 1. Критически низкий вес
    if weight and height:
        height_m = height / 100
        min_safe_weight = 18.5 * height_m * height_m
        
        if weight < min_safe_weight:
            is_dangerous = True
            warnings.append("⚠️ КРИТИЧЕСКИ НИЗКИЙ ВЕС! Немедленно обратитесь к врачу!")
            recommendations.append("❌ НЕ РЕКОМЕНДУЕТСЯ дефицит калорий")
            recommendations.append("✅ Увеличьте потребление калорий")
            recommendations.append("🏥 Обязательная консультация с диетологом")
    
    # 2. Критически низкий процент жира
    if bodyfat:
        min_safe_bodyfat = 5 if sex == 'male' else 12
        
        if bodyfat < min_safe_bodyfat:
            is_dangerous = True
            warnings.append("⚠️ КРИТИЧЕСКИ НИЗКИЙ ПРОЦЕНТ ЖИРА!")
            warnings.append("Это опасно для здоровья!")
            recommendations.append("❌ НЕ РЕКОМЕНДУЕТСЯ дальнейшее снижение жира")
            recommendations.append("✅ Поддерживайте текущий уровень")
            recommendations.append("🏥 Консультация с врачом")
    
    # 3. Признаки РПП
    rpp_indicators = []
    if bodyfat and bodyfat < 15 and sex == 'female':
        rpp_indicators.append("Низкий процент жира у женщины")
    if weight and height and bmi < 18.5:
        rpp_indicators.append("Низкий BMI")
    if len(rpp_indicators) >= 2:
        warnings.append("⚠️ ВНИМАНИЕ: Возможные признаки расстройства пищевого поведения")
        recommendations.append("🏥 Рекомендуется консультация с психологом")
        recommendations.append("💙 Помните: здоровье важнее цифр на весах")
    
    # 4. Экстремально высокий вес
    if weight and height:
        max_safe_weight = 40 * height_m * height_m  # BMI 40
        
        if weight > max_safe_weight:
            warnings.append("⚠️ Экстремально высокий вес")
            recommendations.append("🏥 Обязательная консультация с врачом")
            recommendations.append("✅ Постепенное снижение веса под контролем")
    
    # 5. Небезопасные рекомендации
    if calculated_metrics.get('target_calories'):
        target_calories = calculated_metrics['target_calories']
        bmr = calculated_metrics.get('bmr', 1200)
        
        if target_calories < bmr * 0.8:  # Дефицит более 20%
            warnings.append("⚠️ Слишком агрессивный дефицит калорий")
            recommendations.append("❌ НЕ РЕКОМЕНДУЕТСЯ дефицит более 20%")
            recommendations.append("✅ Безопасный дефицит: 10-15%")
    
    return {
        'is_dangerous': is_dangerous,
        'warnings': warnings,
        'recommendations': recommendations
    }

def get_adaptive_recommendations(user_data: dict, calculated_metrics: dict) -> dict:
    """
    Адаптивные рекомендации для разных категорий пользователей
    """
    weight = user_data.get('weight')
    height = user_data.get('height')
    sex = user_data.get('sex')
    bodyfat = calculated_metrics.get('bodyfat')
    bmi = calculated_metrics.get('bmi')
    
    # Определяем категорию пользователя
    user_category = "normal"
    
    if bmi < 18.5:
        user_category = "underweight"
    elif bmi > 30:
        user_category = "obese"
    elif bodyfat and bodyfat < (8 if sex == 'male' else 15):
        user_category = "athlete"
    elif bodyfat and bodyfat > (25 if sex == 'male' else 35):
        user_category = "high_bodyfat"
    
    recommendations = {
        "underweight": {
            "priority": "weight_gain",
            "message": "Ваш вес ниже нормы. Рекомендуется набрать вес для здоровья.",
            "calories": "профицит 10-15%",
            "protein": "1.6-2.0 г/кг",
            "caution": "Избегайте дефицита калорий!"
        },
        "athlete": {
            "priority": "maintenance",
            "message": "У вас отличная физическая форма! Поддерживайте текущий уровень.",
            "calories": "поддержание веса",
            "protein": "2.0-2.2 г/кг",
            "caution": "Не снижайте процент жира ниже безопасного минимума"
        },
        "high_bodyfat": {
            "priority": "gradual_loss",
            "message": "Рекомендуется постепенное снижение веса для здоровья.",
            "calories": "дефицит 10-15%",
            "protein": "1.8-2.0 г/кг",
            "caution": "Не более 0.5-1 кг в неделю"
        },
        "obese": {
            "priority": "medical_supervision",
            "message": "Рекомендуется консультация с врачом для безопасного снижения веса.",
            "calories": "под контролем врача",
            "protein": "1.6-1.8 г/кг",
            "caution": "Обязательная консультация с врачом!"
        },
        "normal": {
            "priority": "health_optimization",
            "message": "Ваши показатели в норме. Оптимизируйте питание для здоровья.",
            "calories": "поддержание или небольшой дефицит",
            "protein": "1.6-1.8 г/кг",
            "caution": "Сосредоточьтесь на качестве питания"
        }
    }
    
    return recommendations.get(user_category, recommendations["normal"])

def calculate_comprehensive_metrics(user_data: dict, bodyfat: float) -> dict:
    """
    Комплексный расчет всех метрик
    """
    weight = user_data.get('weight')
    height = user_data.get('height')
    waist = user_data.get('waist')
    hip = user_data.get('hip')
    sex = user_data.get('sex')
    age = user_data.get('age', 30)  # по умолчанию 30 лет
    step_multiplier = user_data.get('step_multiplier', 1.2)
    sport_type = user_data.get('sport_type', 'none')
    sport_freq = user_data.get('sport_freq', '1')
    goal = user_data.get('goal', 'healthy')
    
    if not all([weight, height, bodyfat]):
        return None
    
    # Базовые расчеты
    bmi = calculate_bmi(weight, height)
    whr = calculate_whr(waist, hip) if waist and hip else None
    lbm = calculate_lbm(weight, bodyfat)
    ffmi = calculate_ffmi(weight, height, bodyfat)
    
    # Метаболические расчеты
    bmr = calculate_bmr(weight, height, age, sex)
    tdee = calculate_tdee(bmr, step_multiplier, sport_type, sport_freq)
    
    # Классификации
    body_type = get_body_type(bmi, whr, ffmi, sex) if whr else "не определен"
    metabolic_age = get_metabolic_age(bmr, age, sex)
    bodyfat_category = get_bodyfat_category(bodyfat, sex)
    
    # Целевые параметры
    ideal_weights = calculate_ideal_weight(height, sex, body_type)
    target_bodyfat = get_target_bodyfat(goal, sex)
    
    # Рекомендации по калориям для достижения цели
    if goal == 'lean':
        target_calories = tdee * 0.85  # дефицит 15%
    elif goal == 'athletic':
        target_calories = tdee * 1.05  # профицит 5%
    else:
        target_calories = tdee
    
    return {
        'basic_metrics': {
            'bmi': bmi,
            'whr': whr,
            'lbm': lbm,
            'ffmi': ffmi
        },
        'metabolic_metrics': {
            'bmr': bmr,
            'tdee': tdee,
            'metabolic_age': metabolic_age
        },
        'classifications': {
            'body_type': body_type,
            'bodyfat_category': bodyfat_category
        },
        'targets': {
            'ideal_weights': ideal_weights,
            'target_bodyfat': target_bodyfat,
            'target_calories': round(target_calories)
        }
    } 