#!/usr/bin/env python3
"""
Скрипт инициализации базы данных
"""

import sys
import os

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import engine, Base
from models.tables import User, UserRecord, UserFoodPreferences

def init_database():
    """Инициализация базы данных"""
    try:
        print("🔄 Создание таблиц базы данных...")
        
        # Создаем все таблицы
        Base.metadata.create_all(bind=engine)
        
        print("✅ База данных успешно создана!")
        print("📋 Созданные таблицы:")
        print("   - users")
        print("   - user_records")
        print("   - user_food_preferences")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка создания базы данных: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Инициализация базы данных...")
    success = init_database()
    
    if success:
        print("🎉 База данных готова к использованию!")
        sys.exit(0)
    else:
        print("💥 Ошибка инициализации!")
        sys.exit(1) 