from enum import Enum, auto

class UserStates(Enum):
    # Основные данные
    WAITING_FOR_NAME = auto()
    WAITING_FOR_BIRTH_DATE = auto()
    WAITING_FOR_HEIGHT = auto()
    WAITING_FOR_SEX = auto()
    WAITING_FOR_WEIGHT = auto()
    WAITING_FOR_ACTIVITY = auto()

    # Обмеры
    WAITING_FOR_WAIST = auto()
    WAITING_FOR_NECK = auto()
    WAITING_FOR_HIP = auto()

    # Оценка состояния
    WAITING_FOR_GOAL = auto()
    WAITING_FOR_BODY_FAT = auto()
    WAITING_FOR_KBJU = auto()

    # Предпочтения
    WAITING_FOR_PREFERENCES_TYPE = auto()
    WAITING_FOR_PREFERENCES_ITEM = auto()

    # Воронка
    WAITING_FOR_FUNNEL_STEP = auto()
    WAITING_FOR_FUNNEL_ANSWER = auto()

    # Обновление данных
    WAITING_FOR_UPDATE_WEIGHT = auto()
    WAITING_FOR_UPDATE_ACTIVITY = auto()
    WAITING_FOR_UPDATE_WAIST = auto()
    WAITING_FOR_UPDATE_NECK = auto()
    WAITING_FOR_UPDATE_HIP = auto()

    # Спорт
    WAITING_FOR_SPORT_TYPE = auto()
    WAITING_FOR_SPORT_FREQ = auto()

    # Шаги
    WAITING_FOR_STEP_LEVEL = auto() 