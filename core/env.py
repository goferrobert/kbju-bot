import os
from dotenv import load_dotenv

# Автоматически подхватываем .env / dev.env / prod.env
env_file = "prod.env" if os.getenv("IS_PROD", "false").lower() == "true" else "dev.env"
load_dotenv(env_file)

# Флаги окружения
IS_PROD = os.getenv("IS_PROD", "false").lower() == "true"
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "secret")

# Настройки базы данных
DB_URL = os.getenv("DB_URL", "sqlite:///fitness_bot.db")

# Настройки логирования
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_DIR = os.getenv("LOG_DIR", "logs")

# Настройки уведомлений
NOTIFICATION_INTERVAL = int(os.getenv("NOTIFICATION_INTERVAL", "3600"))  # секунды

# Ограничения для валидации
MIN_AGE = int(os.getenv("MIN_AGE", "12"))
MAX_AGE = int(os.getenv("MAX_AGE", "100"))
MIN_HEIGHT = float(os.getenv("MIN_HEIGHT", "100"))
MAX_HEIGHT = float(os.getenv("MAX_HEIGHT", "250"))
MIN_WEIGHT = float(os.getenv("MIN_WEIGHT", "30"))
MAX_WEIGHT = float(os.getenv("MAX_WEIGHT", "300"))
MIN_STEPS = int(os.getenv("MIN_STEPS", "0"))
MAX_STEPS = int(os.getenv("MAX_STEPS", "100000"))
STEPS_GOAL = int(os.getenv("STEPS_GOAL", "10000"))
MIN_TRAINING_FREQUENCY = int(os.getenv("MIN_TRAINING_FREQUENCY", "0"))
MAX_TRAINING_FREQUENCY = int(os.getenv("MAX_TRAINING_FREQUENCY", "7"))
MIN_TRAINING_DURATION = int(os.getenv("MIN_TRAINING_DURATION", "15"))
MAX_TRAINING_DURATION = int(os.getenv("MAX_TRAINING_DURATION", "180"))

# Настройки сообщений
MESSAGE_TIMEOUT = int(os.getenv("MESSAGE_TIMEOUT", "300"))
MAX_MESSAGE_LENGTH = int(os.getenv("MAX_MESSAGE_LENGTH", "4096"))

# Настройки кэширования
CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))
CACHE_MAX_SIZE = int(os.getenv("CACHE_MAX_SIZE", "1000"))
