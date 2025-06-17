from datetime import datetime
from typing import Any, Dict, List, Optional, Union
import re

class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass

def validate_name(name: str) -> str:
    """
    Validate user's name.
    
    Args:
        name: User's name
    
    Returns:
        Validated name
    
    Raises:
        ValidationError: If name is invalid
    """
    if not name or len(name.strip()) < 2:
        raise ValidationError("Имя должно содержать минимум 2 символа")
    
    # Remove extra spaces and capitalize
    name = ' '.join(name.strip().split())
    return name

def validate_birth_date(birth_date: str) -> datetime:
    """
    Validate birth date.
    
    Args:
        birth_date: Birth date in DD.MM.YYYY format
    
    Returns:
        datetime object
    
    Raises:
        ValidationError: If date is invalid
    """
    try:
        date = datetime.strptime(birth_date, '%d.%m.%Y')
        if date > datetime.now():
            raise ValidationError("Дата рождения не может быть в будущем")
        
        # Check if age is between 12 and 100 years
        age = (datetime.now() - date).days / 365.25
        if age < 12 or age > 100:
            raise ValidationError("Возраст должен быть от 12 до 100 лет")
        
        return date
    except ValueError:
        raise ValidationError("Неверный формат даты. Используйте ДД.ММ.ГГГГ")

def validate_gender(gender: str) -> str:
    """
    Validate gender.
    
    Args:
        gender: Gender string
    
    Returns:
        Validated gender ('male' or 'female')
    
    Raises:
        ValidationError: If gender is invalid
    """
    gender = gender.lower().strip()
    if gender in ['мужской', 'male', 'м']:
        return 'male'
    elif gender in ['женский', 'female', 'ж']:
        return 'female'
    else:
        raise ValidationError("Укажите пол: мужской или женский")

def validate_height(height: Union[str, float]) -> float:
    """
    Validate height.
    
    Args:
        height: Height in cm
    
    Returns:
        Validated height as float
    
    Raises:
        ValidationError: If height is invalid
    """
    try:
        height = float(height)
        if height < 100 or height > 250:
            raise ValidationError("Рост должен быть от 100 до 250 см")
        return round(height, 1)
    except ValueError:
        raise ValidationError("Рост должен быть числом")

def validate_weight(weight: Union[str, float]) -> float:
    """
    Validate weight.
    
    Args:
        weight: Weight in kg
    
    Returns:
        Validated weight as float
    
    Raises:
        ValidationError: If weight is invalid
    """
    try:
        weight = float(weight)
        if weight < 30 or weight > 300:
            raise ValidationError("Вес должен быть от 30 до 300 кг")
        return round(weight, 1)
    except ValueError:
        raise ValidationError("Вес должен быть числом")

def validate_measurement(measurement: Union[str, float], name: str) -> float:
    """
    Validate body measurement.
    
    Args:
        measurement: Measurement in cm
        name: Measurement name for error message
    
    Returns:
        Validated measurement as float
    
    Raises:
        ValidationError: If measurement is invalid
    """
    try:
        measurement = float(measurement)
        if measurement < 10 or measurement > 200:
            raise ValidationError(f"{name} должен быть от 10 до 200 см")
        return round(measurement, 1)
    except ValueError:
        raise ValidationError(f"{name} должен быть числом")

def validate_steps(steps: Union[str, int]) -> int:
    """
    Validate daily steps.
    
    Args:
        steps: Number of steps
    
    Returns:
        Validated steps as integer
    
    Raises:
        ValidationError: If steps is invalid
    """
    try:
        steps = int(steps)
        if steps < 0 or steps > 100000:
            raise ValidationError("Количество шагов должно быть от 0 до 100000")
        return steps
    except ValueError:
        raise ValidationError("Количество шагов должно быть целым числом")

def validate_activity_level(level: str) -> str:
    """
    Validate activity level.
    
    Args:
        level: Activity level string
    
    Returns:
        Validated activity level
    
    Raises:
        ValidationError: If level is invalid
    """
    valid_levels = {
        'sedentary': ['сидячий', 'малоподвижный', '1'],
        'light': ['легкий', 'легкая', '2'],
        'moderate': ['умеренный', 'умеренная', '3'],
        'active': ['активный', 'активная', '4'],
        'very_active': ['очень активный', 'очень активная', '5']
    }
    
    level = level.lower().strip()
    for key, values in valid_levels.items():
        if level in values:
            return key
    
    raise ValidationError("Укажите уровень активности от 1 до 5")

def validate_training_type(training_type: str) -> str:
    """
    Validate training type.
    
    Args:
        training_type: Training type string
    
    Returns:
        Validated training type
    
    Raises:
        ValidationError: If type is invalid
    """
    valid_types = {
        'weight': ['силовой', '1'],
        'cardio': ['кардио', '2'],
        'functional': ['функциональный', '3'],
        'mixed': ['смешанный', '4']
    }
    
    training_type = training_type.lower().strip()
    for key, values in valid_types.items():
        if training_type in values:
            return key
    
    raise ValidationError("Укажите тип тренировок от 1 до 4")

def validate_training_intensity(intensity: str) -> str:
    """
    Validate training intensity.
    
    Args:
        intensity: Intensity string
    
    Returns:
        Validated intensity
    
    Raises:
        ValidationError: If intensity is invalid
    """
    valid_intensities = {
        'low': ['низкая', '1'],
        'medium': ['средняя', '2'],
        'high': ['высокая', '3']
    }
    
    intensity = intensity.lower().strip()
    for key, values in valid_intensities.items():
        if intensity in values:
            return key
    
    raise ValidationError("Укажите интенсивность от 1 до 3")

def validate_training_duration(duration: str) -> str:
    """
    Validate training duration.
    
    Args:
        duration: Duration string
    
    Returns:
        Validated duration
    
    Raises:
        ValidationError: If duration is invalid
    """
    valid_durations = {
        'short': ['короткая', '1'],
        'medium': ['средняя', '2'],
        'long': ['длительная', '3']
    }
    
    duration = duration.lower().strip()
    for key, values in valid_durations.items():
        if duration in values:
            return key
    
    raise ValidationError("Укажите длительность от 1 до 3")

def validate_time(time: str) -> datetime:
    """
    Validate time string.
    
    Args:
        time: Time in HH:MM format
    
    Returns:
        datetime object with time
    
    Raises:
        ValidationError: If time is invalid
    """
    try:
        time = datetime.strptime(time, '%H:%M').time()
        return datetime.combine(datetime.now().date(), time)
    except ValueError:
        raise ValidationError("Неверный формат времени. Используйте ЧЧ:ММ")

def validate_goal(goal: str) -> str:
    """
    Validate user goal.
    
    Args:
        goal: Goal string
    
    Returns:
        Validated goal
    
    Raises:
        ValidationError: If goal is invalid
    """
    valid_goals = {
        'weight_loss': ['похудение', '1'],
        'maintenance': ['поддержание', '2'],
        'muscle_gain': ['набор массы', '3']
    }
    
    goal = goal.lower().strip()
    for key, values in valid_goals.items():
        if goal in values:
            return key
    
    raise ValidationError("Укажите цель от 1 до 3")

def validate_body_type(body_type: str) -> str:
    """
    Validate body type.
    
    Args:
        body_type: Body type string
    
    Returns:
        Validated body type
    
    Raises:
        ValidationError: If body type is invalid
    """
    valid_types = {
        'athletic': ['атлетическое', '1'],
        'slim': ['худощавое', '2'],
        'healthy': ['здоровое', '3']
    }
    
    body_type = body_type.lower().strip()
    for key, values in valid_types.items():
        if body_type in values:
            return key
    
    raise ValidationError("Укажите тип телосложения от 1 до 3")

def validate_work_type(work_type: str) -> str:
    """
    Validate work type.
    
    Args:
        work_type: Work type string
    
    Returns:
        Validated work type
    
    Raises:
        ValidationError: If work type is invalid
    """
    valid_types = {
        'sedentary': ['сидячая', '1'],
        'standing': ['стоячая', '2'],
        'moderate': ['умеренная', '3'],
        'heavy': ['тяжелая', '4']
    }
    
    work_type = work_type.lower().strip()
    for key, values in valid_types.items():
        if work_type in values:
            return key
    
    raise ValidationError("Укажите тип работы от 1 до 4")

def validate_diseases(diseases: List[str]) -> List[str]:
    """
    Validate list of diseases.
    
    Args:
        diseases: List of disease names
    
    Returns:
        Validated list of diseases
    
    Raises:
        ValidationError: If diseases list is invalid
    """
    if not diseases:
        return []
    
    # Remove duplicates and empty strings
    diseases = list(set(disease.strip() for disease in diseases if disease.strip()))
    
    # Validate each disease name
    for disease in diseases:
        if len(disease) < 3:
            raise ValidationError("Название заболевания должно содержать минимум 3 символа")
        if not re.match(r'^[а-яА-ЯёЁ\s-]+$', disease):
            raise ValidationError("Название заболевания должно содержать только русские буквы")
    
    return diseases

def validate_allergies(allergies: List[str]) -> List[str]:
    """
    Validate list of allergies.
    
    Args:
        allergies: List of allergy names
    
    Returns:
        Validated list of allergies
    
    Raises:
        ValidationError: If allergies list is invalid
    """
    if not allergies:
        return []
    
    # Remove duplicates and empty strings
    allergies = list(set(allergy.strip() for allergy in allergies if allergy.strip()))
    
    # Validate each allergy name
    for allergy in allergies:
        if len(allergy) < 3:
            raise ValidationError("Название аллергии должно содержать минимум 3 символа")
        if not re.match(r'^[а-яА-ЯёЁ\s-]+$', allergy):
            raise ValidationError("Название аллергии должно содержать только русские буквы")
    
    return allergies

def validate_food_preferences(preferences: List[str]) -> List[str]:
    """
    Validate list of food preferences.
    
    Args:
        preferences: List of food preference names
    
    Returns:
        Validated list of preferences
    
    Raises:
        ValidationError: If preferences list is invalid
    """
    if not preferences:
        return []
    
    # Remove duplicates and empty strings
    preferences = list(set(pref.strip() for pref in preferences if pref.strip()))
    
    # Validate each preference name
    for pref in preferences:
        if len(pref) < 3:
            raise ValidationError("Название предпочтения должно содержать минимум 3 символа")
        if not re.match(r'^[а-яА-ЯёЁ\s-]+$', pref):
            raise ValidationError("Название предпочтения должно содержать только русские буквы")
    
    return preferences 