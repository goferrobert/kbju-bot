from aiogram.dispatcher.filters.state import State, StatesGroup

class UserInfoStates(StatesGroup):
    name = State()
    birthday = State()
    sex = State()
    height = State()
    weight = State()
    steps = State()
    sport = State()
    frequency = State()
    goal = State()

class MeasurementsStates(StatesGroup):
    waist = State()
    neck = State()
    hip = State()
    chest = State()
    bicep = State()
    thigh = State()
    wrist = State()      # новое
    calf = State()       # новое
    forearm = State()    # новое
    abdomen = State()    # новое
    sleep_hours = State() # новое
    stress_level = State() # новое
    weight = State()
    steps = State()
    sport_type = State()
    sport_freq = State()

class FoodPreferencesStates(StatesGroup):
    likes = State()
    dislikes = State()

class FoodStates(StatesGroup):
    likes = State()
    dislikes = State() 