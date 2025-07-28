#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для создания тестовых данных в базе данных
Используется для проверки функции "Прогресс"
"""

import sys
import os
from datetime import date, timedelta
from sqlalchemy.orm import Session

# Добавляем путь к корневой папке проекта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import SessionLocal, engine
from models.tables import User, UserRecord
from crud.user_crud import create_user, get_user
from crud.record_crud import create_or_update_record

def create_test_user():
    """Создает тестового пользователя"""
    db = SessionLocal()
    
    # Проверяем, есть ли уже пользователь с ID 285835433
    existing_user = get_user(db, 285835433)
    
    if not existing_user:
        # Создаем тестового пользователя
        user = create_user(
            db,
            telegram_id=285835433,
            username="test_user",
            first_name="Тестовый",
            last_name="Пользователь",
            sex="male",
            date_of_birth=date(1990, 1, 1)
        )
        print(f"✅ Создан тестовый пользователь: {user.first_name} {user.last_name}")
    else:
        print(f"✅ Пользователь уже существует: {existing_user.first_name} {existing_user.last_name}")
    
    db.close()
    return existing_user or user

def create_test_records():
    """Создает тестовые записи измерений"""
    db = SessionLocal()
    
    # Получаем пользователя
    user = get_user(db, 285835433)
    if not user:
        print("❌ Пользователь не найден!")
        db.close()
        return
    
    # Создаем тестовые записи за последние 3 месяца
    test_records = [
        # Начальные данные (3 месяца назад)
        {
            'date': date.today() - timedelta(days=90),
            'weight': 85.0,
            'waist': 95.0,
            'neck': 42.0,
            'height': 180,
            'goal': 'lean',
            'steps': '8000-10000',
            'sport_type': 'running',
            'sport_freq': '3',
            'step_multiplier': 1.2,
            'bodyfat': 22.5
        },
        # Через месяц
        {
            'date': date.today() - timedelta(days=60),
            'weight': 82.0,
            'waist': 92.0,
            'neck': 41.5,
            'height': 180,
            'goal': 'lean',
            'steps': '8000-10000',
            'sport_type': 'running',
            'sport_freq': '4',
            'step_multiplier': 1.2,
            'bodyfat': 21.0
        },
        # Через 2 месяца
        {
            'date': date.today() - timedelta(days=30),
            'weight': 79.0,
            'waist': 89.0,
            'neck': 41.0,
            'height': 180,
            'goal': 'lean',
            'steps': '8000-10000',
            'sport_type': 'running',
            'sport_freq': '5',
            'step_multiplier': 1.2,
            'bodyfat': 19.5
        },
        # Текущие данные
        {
            'date': date.today(),
            'weight': 76.0,
            'waist': 86.0,
            'neck': 40.5,
            'height': 180,
            'goal': 'lean',
            'steps': '8000-10000',
            'sport_type': 'running',
            'sport_freq': '5',
            'step_multiplier': 1.2,
            'bodyfat': 18.0
        }
    ]
    
    created_count = 0
    for record_data in test_records:
        # Проверяем, есть ли уже запись на эту дату
        existing_record = db.query(UserRecord).filter(
            UserRecord.telegram_id == 285835433,
            UserRecord.date == record_data['date']
        ).first()
        
        if not existing_record:
            # Создаем новую запись
            new_record = create_or_update_record(
                db,
                285835433,
                record_data['date'],
                weight=record_data['weight'],
                waist=record_data['waist'],
                neck=record_data['neck'],
                height=record_data['height'],
                goal=record_data['goal'],
                steps=record_data['steps'],
                sport_type=record_data['sport_type'],
                sport_freq=record_data['sport_freq'],
                step_multiplier=record_data['step_multiplier'],
                bodyfat=record_data['bodyfat']
            )
            if new_record:
                created_count += 1
                print(f"✅ Создана запись на {record_data['date']}: вес {record_data['weight']} кг, жир {record_data['bodyfat']:.1f}%")
            else:
                print(f"❌ Ошибка создания записи на {record_data['date']}")
        else:
            print(f"⚠️ Запись на {record_data['date']} уже существует")
    
    db.close()
    print(f"\n📊 Создано {created_count} новых записей")

def main():
    """Основная функция"""
    print("🚀 Создание тестовых данных для проверки прогресса...")
    print("=" * 50)
    
    # Создаем пользователя
    user = create_test_user()
    
    # Создаем записи
    create_test_records()
    
    print("\n" + "=" * 50)
    print("✅ Тестовые данные созданы!")
    print("📱 Теперь можете проверить функцию 'Прогресс' в боте")
    print("📊 Ожидаемый результат: сброс 9 кг за 3 месяца")

if __name__ == "__main__":
    main() 