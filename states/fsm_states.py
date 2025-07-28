from aiogram.dispatcher.filters.state import State, StatesGroup

class UserInfoStates(StatesGroup):
    """Состояния для сбора информации о пользователе"""
    name = State()
    birthday = State()
    sex = State()
    height = State()
    weight = State()
    steps = State()
    sport_type = State()
    sport_freq = State()
    waist = State()
    neck = State()
    hip = State()
    goal = State()

class MeasurementsStates(StatesGroup):
    """Состояния для новых измерений"""
    waist = State()
    neck = State()
    hip = State()
    weight = State()
    steps = State()
    sport_type = State()
    sport_freq = State()

class GoalStates(StatesGroup):
    """Состояния для изменения цели"""
    goal = State()

class FoodStates(StatesGroup):
    """Состояния для пищевых предпочтений"""
    likes = State()
    dislikes = State() 