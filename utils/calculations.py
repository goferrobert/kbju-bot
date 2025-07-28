import math
import logging

def calculate_bodyfat(user_data: dict):
    """
    Расчёт % жира по методу US Navy
    """
    logging.info(f"calculate_bodyfat: input={user_data}")
    sex = user_data.get('sex')
    waist = user_data.get('waist')
    neck = user_data.get('neck')
    hip = user_data.get('hip')
    height = user_data.get('height')
    
    if sex == 'male':
        if not all([waist, neck, height]):
            return None
        bodyfat = 86.010 * math.log10(waist - neck) - 70.041 * math.log10(height) + 36.76
    else:  # female
        if not all([waist, neck, hip, height]):
            return None
        bodyfat = 163.205 * math.log10(waist + hip - neck) - 97.684 * math.log10(height) - 78.387
    
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
    if steps == "10000+":
        return 1.5
    elif steps == "8000-10000":
        return 1.4
    elif steps == "5000-8000":
        return 1.3
    elif steps == "3000-5000":
        return 1.2
    else:  # 0-3000
        return 1.1 