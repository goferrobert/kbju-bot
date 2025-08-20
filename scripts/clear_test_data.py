#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для очистки тестовых данных
Используется для разработки и тестирования
"""

import sys
import os
from datetime import date

# Добавляем корневую папку в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import SessionLocal
from crud.user_crud import delete_user
from crud.record_crud import delete_user_records

def clear_test_data():
    """Очистка тестовых данных"""
    db = SessionLocal()
    
    # ID тестовых пользователей
    test_user_ids = [123456789, 987654321, 555666777]
    
    deleted_records = 0
    deleted_users = 0
    
    for user_id in test_user_ids:
        try:
            # Удаляем записи пользователя
            records_deleted = delete_user_records(db, user_id)
            deleted_records += records_deleted
            print(f"🗑️ Удалено записей для пользователя {user_id}: {records_deleted}")
            
            # Удаляем пользователя
            if delete_user(db, user_id):
                deleted_users += 1
                print(f"🗑️ Удален пользователь {user_id}")
            else:
                print(f"⚠️ Пользователь {user_id} не найден или уже удален")
                
        except Exception as e:
            print(f"❌ Ошибка при удалении данных пользователя {user_id}: {e}")
    
    db.close()
    return deleted_users, deleted_records

def clear_all_data():
    """Очистка всех данных (ОПАСНО!)"""
    db = SessionLocal()
    
    try:
        # Удаляем все записи
        db.execute("DELETE FROM user_records")
        records_deleted = db.execute("SELECT COUNT(*) FROM user_records").scalar()
        
        # Удаляем всех пользователей
        db.execute("DELETE FROM users")
        users_deleted = db.execute("SELECT COUNT(*) FROM users").scalar()
        
        # Удаляем предпочтения в еде
        db.execute("DELETE FROM user_food_preferences")
        
        db.commit()
        
        print(f"🗑️ Удалено всех записей: {records_deleted}")
        print(f"🗑️ Удалено всех пользователей: {users_deleted}")
        print("🗑️ Удалены все предпочтения в еде")
        
    except Exception as e:
        print(f"❌ Ошибка при очистке всех данных: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """Основная функция"""
    print("🧹 Очистка тестовых данных...")
    
    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        # Очистка всех данных
        confirm = input("⚠️ ВНИМАНИЕ! Это удалит ВСЕ данные! Введите 'YES' для подтверждения: ")
        if confirm == "YES":
            clear_all_data()
            print("✅ Все данные успешно удалены!")
        else:
            print("❌ Операция отменена")
            return 1
    else:
        # Очистка только тестовых данных
        deleted_users, deleted_records = clear_test_data()
        print(f"✅ Удалено пользователей: {deleted_users}")
        print(f"✅ Удалено записей: {deleted_records}")
    
    return 0

if __name__ == "__main__":
    exit(main())
