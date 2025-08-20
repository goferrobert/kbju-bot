#!/usr/bin/env python3
"""
Скрипт миграции базы данных для добавления новых полей
"""

import sqlite3
import os
import sys

def migrate_database():
    """Миграция базы данных"""
    db_path = "kbju_bot.db"
    
    if not os.path.exists(db_path):
        print("❌ База данных не найдена!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 Начинаю миграцию базы данных...")
        
        # Получаем информацию о существующих колонках
        cursor.execute("PRAGMA table_info(user_records)")
        existing_columns = [column[1] for column in cursor.fetchall()]
        
        print(f"📋 Существующие колонки: {existing_columns}")
        
        # Список новых колонок для добавления
        new_columns = [
            ("wrist", "FLOAT"),
            ("calf", "FLOAT"),
            ("forearm", "FLOAT"),
            ("abdomen", "FLOAT"),
            ("sleep_hours", "FLOAT"),
            ("stress_level", "VARCHAR"),
            ("bmi", "FLOAT"),
            ("lbm", "FLOAT"),
            ("whr", "FLOAT"),
            ("bmr", "INTEGER"),
            ("tdee", "INTEGER"),
            ("metabolic_age", "INTEGER"),
            ("body_type", "VARCHAR"),
            ("bodyfat_category", "VARCHAR")
        ]
        
        # Добавляем новые колонки
        for column_name, column_type in new_columns:
            if column_name not in existing_columns:
                try:
                    cursor.execute(f"ALTER TABLE user_records ADD COLUMN {column_name} {column_type}")
                    print(f"✅ Добавлена колонка: {column_name}")
                except sqlite3.OperationalError as e:
                    print(f"⚠️ Колонка {column_name} уже существует: {e}")
            else:
                print(f"ℹ️ Колонка {column_name} уже существует")
        
        # Проверяем результат
        cursor.execute("PRAGMA table_info(user_records)")
        final_columns = [column[1] for column in cursor.fetchall()]
        print(f"📋 Финальные колонки: {final_columns}")
        
        conn.commit()
        conn.close()
        
        print("✅ Миграция завершена успешно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка миграции: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Запуск миграции базы данных...")
    success = migrate_database()
    
    if success:
        print("🎉 Миграция прошла успешно!")
        sys.exit(0)
    else:
        print("💥 Миграция завершилась с ошибками!")
        sys.exit(1) 