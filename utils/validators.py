from datetime import datetime, date
import re
import logging

def validate_number(text: str, min_val: float = None, max_val: float = None) -> tuple[bool, float]:
    """
    Валидация числа
    """
    try:
        number = float(text.replace(',', '.'))
        if min_val is not None and number < min_val:
            return False, f"Значение должно быть не меньше {min_val}"
        if max_val is not None and number > max_val:
            return False, f"Значение должно быть не больше {max_val}"
        return True, number
    except ValueError:
        return False, "Введите корректное число"

def validate_date(text: str) -> tuple[bool, date]:
    """
    Валидация даты в формате ДД.ММ.ГГГГ
    """
    try:
        date_obj = datetime.strptime(text, "%d.%m.%Y").date()
        if date_obj > date.today():
            return False, "Дата не может быть в будущем"
        return True, date_obj
    except ValueError:
        return False, "Введите дату в формате ДД.ММ.ГГГГ"

def validate_name(name: str) -> bool:
    """Валидация имени"""
    logging.info(f"validate_name: input={name}")
    
    if not name or len(name.strip()) < 2:
        return False
    
    # Убираем лишние пробелы
    name = ' '.join(name.strip().split())
    
    # Проверяем минимальную и максимальную длину
    if len(name) < 3 or len(name) > 50:
        return False
    
    # Проверяем, что имя содержит только русские и английские буквы, пробелы и дефисы
    pattern = r'^[а-яёА-ЯЁa-zA-Z\s\-]+$'
    if not re.match(pattern, name):
        return False
    
    # Проверяем, что имя содержит минимум 2 слова (имя и фамилия)
    words = name.split()
    if len(words) < 2:
        return False
    
    # Проверяем, что каждое слово содержит минимум 2 буквы
    for word in words:
        if len(word) < 2:
            return False
    
    # Проверяем, что нет повторяющихся символов (например, "aaa")
    for word in words:
        if len(word) > 2 and len(set(word)) == 1:
            return False
    
    # Проверяем, что нет цифр и специальных символов
    if re.search(r'[0-9!@#$%^&*()_+=<>?/\\|]', name):
        return False
        
    logging.info(f"validate_name: result=True")
    return True

def validate_birthday(birthday: str) -> bool:
    """Валидация даты рождения"""
    try:
        # Убираем лишние пробелы
        birthday = birthday.strip()
        
        # Проверяем формат даты
        if not re.match(r'^\d{2}\.\d{2}\.\d{4}$', birthday):
            return False
        
        # Парсим дату в формате ДД.ММ.ГГГГ
        date_obj = datetime.strptime(birthday, '%d.%m.%Y')
        
        # Проверяем, что дата не в будущем
        now = datetime.now()
        if date_obj > now:
            return False
        
        # Проверяем, что возраст не больше 120 лет и не меньше 10 лет
        age = now.year - date_obj.year
        if now.month < date_obj.month or (now.month == date_obj.month and now.day < date_obj.day):
            age -= 1
            
        if age > 120 or age < 10:
            return False
            
        return True
    except ValueError:
        return False

def validate_height(height: str) -> bool:
    """Валидация роста"""
    try:
        height_val = int(height)
        return 100 <= height_val <= 250
    except ValueError:
        return False

def validate_weight(weight: str) -> bool:
    """Валидация веса"""
    try:
        weight_val = float(weight.replace(',', '.'))
        return 30 <= weight_val <= 300
    except ValueError:
        return False

def validate_sex(sex: str) -> bool:
    """Валидация пола"""
    return sex in ['male', 'female']

def validate_goal(goal: str) -> bool:
    """Валидация цели"""
    return goal in ['healthy', 'athletic', 'lean']

def validate_sport_type(sport_type: str) -> bool:
    """Валидация типа спорта"""
    valid_types = ['none', 'walking', 'running', 'strength', 'yoga', 'swimming', 'cycling', 'team']
    return sport_type in valid_types

def validate_sport_freq(freq: str) -> bool:
    """Валидация частоты спорта"""
    valid_freqs = ['0', '1', '2', '3', '4', '5', '6', 'daily']
    return freq in valid_freqs

def validate_steps(steps: str) -> bool:
    """Валидация количества шагов"""
    valid_steps = ['0-3000', '3000-5000', '5000-8000', '8000-10000', '10000+']
    return steps in valid_steps

# Универсальная функция для валидации измерений
def validate_measurement_range(value: str, min_val: float, max_val: float) -> bool:
    """Универсальная валидация измерений в заданном диапазоне"""
    try:
        measurement_val = float(value.replace(',', '.'))
        return min_val <= measurement_val <= max_val
    except ValueError:
        return False

# Конфигурация валидаторов для измерений
MEASUREMENT_VALIDATORS = {
    'waist': {'min': 50, 'max': 200},
    'neck': {'min': 20, 'max': 100},
    'hip': {'min': 50, 'max': 200},
    'chest': {'min': 60, 'max': 150},
    'bicep': {'min': 20, 'max': 60},
    'thigh': {'min': 40, 'max': 100},
    'wrist': {'min': 15, 'max': 25},
    'calf': {'min': 25, 'max': 50},
    'forearm': {'min': 20, 'max': 40},
    'abdomen': {'min': 60, 'max': 150}
}

# Универсальная функция для валидации измерений
def validate_measurement(measurement_type: str, value: str) -> bool:
    """Универсальная валидация измерений"""
    config = MEASUREMENT_VALIDATORS.get(measurement_type)
    if not config:
        return False
    return validate_measurement_range(value, config['min'], config['max'])

# Специальные функции для обратной совместимости
def validate_waist_measurement(measurement: str) -> bool:
    return validate_measurement('waist', measurement)

def validate_neck_measurement(measurement: str) -> bool:
    return validate_measurement('neck', measurement)

def validate_hip_measurement(measurement: str) -> bool:
    return validate_measurement('hip', measurement)

def validate_chest_measurement(measurement: str) -> bool:
    return validate_measurement('chest', measurement)

def validate_bicep_measurement(measurement: str) -> bool:
    return validate_measurement('bicep', measurement)

def validate_thigh_measurement(measurement: str) -> bool:
    return validate_measurement('thigh', measurement)

def validate_wrist_measurement(value: str) -> bool:
    return validate_measurement('wrist', value)

def validate_calf_measurement(value: str) -> bool:
    return validate_measurement('calf', value)

def validate_forearm_measurement(value: str) -> bool:
    return validate_measurement('forearm', value)

def validate_abdomen_measurement(value: str) -> bool:
    return validate_measurement('abdomen', value)

def validate_sleep_hours(sleep: str) -> bool:
    """Валидация часов сна"""
    try:
        sleep_val = float(sleep.replace(',', '.'))
        return 4 <= sleep_val <= 12
    except ValueError:
        return False

def validate_stress_level(stress: str) -> bool:
    """Валидация уровня стресса"""
    valid_levels = ['low', 'medium', 'high']
    return stress in valid_levels 