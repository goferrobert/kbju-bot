from datetime import datetime, date
from app.core.errors import ValidationError

def validate_name(name: str) -> tuple[str, str]:
    """
    Валидация имени пользователя
    Returns:
        tuple: (first_name, last_name)
    """
    if not name or len(name.strip()) < 2:
        raise ValidationError("Имя должно содержать минимум 2 символа")
    if len(name) > 100:
        raise ValidationError("Имя слишком длинное (максимум 100 символов)")
    if not all(c.isalpha() or c.isspace() or c in "-' " for c in name):
        raise ValidationError("Имя может содержать только буквы, пробелы, дефисы и апострофы")
    parts = name.strip().split()
    if len(parts) == 1:
        first_name = parts[0]
        last_name = parts[0]
    else:
        first_name = parts[0]
        last_name = " ".join(parts[1:])
    if len(first_name) < 2 or len(last_name) < 2:
        raise ValidationError("Имя и фамилия должны содержать минимум 2 символа")
    return first_name, last_name

def validate_birthday(birthday_str: str) -> date:
    """
    Валидация даты рождения
    Returns:
        date: Объект даты
    """
    try:
        birthday = datetime.strptime(birthday_str.strip(), "%d.%m.%Y").date()
    except ValueError:
        raise ValidationError("Неверный формат даты. Используйте формат ДД.ММ.ГГГГ")
    
    today = date.today()
    age = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))
    
    if age < 12:
        raise ValidationError("Извините, но бот доступен только для пользователей старше 12 лет")
    if age > 100:
        raise ValidationError("Пожалуйста, проверьте правильность введенной даты")
    
    return birthday

def validate_height(height_str: str) -> int:
    """
    Валидация роста
    Returns:
        int: Рост в сантиметрах
    """
    try:
        height = int(height_str.strip())
    except ValueError:
        raise ValidationError("Рост должен быть целым числом")
    
    if not (100 <= height <= 250):
        raise ValidationError("Рост должен быть от 100 до 250 см")
    
    return height

def validate_measurement(value: str, min_val: float, max_val: float, name: str) -> float:
    """
    Валидация измерений (талия, шея, бедра)
    Returns:
        float: Значение измерения
    """
    try:
        measurement = float(value.strip())
    except ValueError:
        raise ValidationError(f"{name} должен быть числом")
    
    if not (min_val <= measurement <= max_val):
        raise ValidationError(f"{name} должен быть от {min_val} до {max_val} см")
    
    return measurement

def validate_sex(sex: str) -> str:
    """
    Валидация пола
    Returns:
        str: Валидное значение пола
    """
    valid_sexes = ["мужской", "женский"]
    if sex not in valid_sexes:
        raise ValidationError("Неверное значение пола")
    return sex 