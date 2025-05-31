import os
from dotenv import load_dotenv

# Автоматически подхватываем .env / dev.env / prod.env
env_file = "prod.env" if os.getenv("IS_PROD", "false").lower() == "true" else "dev.env"
load_dotenv(env_file)

# Флаги окружения
IS_PROD = os.getenv("IS_PROD", "false").lower() == "true"
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "secret")
