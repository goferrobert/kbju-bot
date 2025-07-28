# -*- coding: utf-8 -*-
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv
import os

# Загружаем переменные окружения
load_dotenv()

# Проверяем наличие токена
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    print("❌ ОШИБКА: Не найден токен бота!")
    print("Создайте файл .env в корне проекта и добавьте:")
    print("BOT_TOKEN=ваш_токен_бота")
    exit(1)

# Централизованная настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Импорт и регистрация обработчиков
from handlers.start_handlers import register_start_handlers
from handlers.user_info_handlers import register_user_info_handlers
from handlers.menu_handlers import register_menu_handlers
from handlers.measurements_handlers import register_measurements_handlers
from handlers.food_handlers import register_food_handlers

async def main():
    """Основная функция"""
    logger.info("Запуск бота...")
    
    # Создаем таблицы базы данных
    from models.database import engine
    from models.tables import Base
    Base.metadata.create_all(bind=engine)
    logger.info("База данных инициализирована")
    
    # Регистрация обработчиков
    register_start_handlers(dp)
    register_user_info_handlers(dp)
    register_menu_handlers(dp)
    register_measurements_handlers(dp)
    register_food_handlers(dp)
    
    logger.info("Бот запущен!")
    
    try:
        # Удаляем webhook и pending updates для избежания конфликтов
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling()
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main()) 