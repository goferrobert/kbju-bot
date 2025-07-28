#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для очистки тестовых данных из базы данных
"""

import sys
import os
from datetime import date, timedelta

# Добавляем путь к корневой папке проекта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import SessionLocal
from models.tables import User, UserRecord
from crud.user_crud import get_user

def clear_test_records():
    """Удаляет тестовые записи измерений"""
    db = SessionLocal()
    
    # Получаем пользователя
    user = get_user(db, 285835433)
    if not user:
        print("❌ Тестовый пользователь не найден!")
        db.close()
        return
    
    # Удаляем записи за последние 3 месяца
    test_dates = [
        date.today() - timedelta(days=90),
        date.today() - timedelta(days=60),
        date.today() - timedelta(days=30),
        date.today()
    ]
    
    deleted_count = 0
    for test_date in test_dates:
        # Находим и удаляем записи на эти даты
        records = db.query(UserRecord).filter(
            UserRecord.telegram_id == 285835433,
            UserRecord.date == test_date
        ).all()
        
        for record in records:
            db.delete(record)
            deleted_count += 1
            print(f"🗑️ Удалена запись на {test_date}: вес {record.weight} кг")
    
    db.commit()
    db.close()
    print(f"\n📊 Удалено {deleted_count} записей")

def clear_test_user():
    """Удаляет тестового пользователя и все его записи"""
    db = SessionLocal()
    
    # Получаем пользователя
    user = get_user(db, 285835433)
    if not user:
        print("❌ Тестовый пользователь не найден!")
        db.close()
        return
    
    # Удаляем все записи пользователя
    records = db.query(UserRecord).filter(UserRecord.telegram_id == 285835433).all()
    for record in records:
        db.delete(record)
    
    # Удаляем пользователя
    db.delete(user)
    db.commit()
    db.close()
    
    print(f"🗑️ Удален тестовый пользователь и {len(records)} записей")

def main():
    """Основная функция"""
    print("🧹 Очистка тестовых данных...")
    print("=" * 50)
    
    choice = input("Выберите действие:\n1. Удалить только тестовые записи\n2. Удалить тестового пользователя полностью\nВведите 1 или 2: ")
    
    if choice == "1":
        clear_test_records()
    elif choice == "2":
        clear_test_user()
    else:
        print("❌ Неверный выбор!")
        return
    
    print("\n" + "=" * 50)
    print("✅ Очистка завершена!")

if __name__ == "__main__":
    main() 