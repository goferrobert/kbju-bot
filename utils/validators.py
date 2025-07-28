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
        height_val = int(height.strip())
        return 100 <= height_val <= 250
    except ValueError:
        return False

def validate_weight(weight: str) -> bool:
    """Валидация веса"""
    try:
        weight_val = float(weight.strip())
        return 30 <= weight_val <= 300
    except ValueError:
        return False

def validate_steps(text: str) -> tuple[bool, int]:
    """
    Валидация шагов
    """
    success, value = validate_number(text, 0, 50000)
    if success:
        return True, int(value)
    return False, value

def validate_measurement(measurement: str) -> bool:
    """Валидация обмеров (талия, шея, бедра)"""
    try:
        measurement_val = float(measurement.strip())
        # Более точные диапазоны для разных измерений
        return 20 <= measurement_val <= 200
    except ValueError:
        return False

def validate_waist_measurement(measurement: str) -> bool:
    """Валидация обхвата талии"""
    try:
        measurement_val = float(measurement.strip())
        return 50 <= measurement_val <= 200
    except ValueError:
        return False

def validate_neck_measurement(measurement: str) -> bool:
    """Валидация обхвата шеи"""
    try:
        measurement_val = float(measurement.strip())
        return 20 <= measurement_val <= 100
    except ValueError:
        return False

def validate_hip_measurement(measurement: str) -> bool:
    """Валидация обхвата бедер"""
    try:
        measurement_val = float(measurement.strip())
        return 50 <= measurement_val <= 200
    except ValueError:
        return False 