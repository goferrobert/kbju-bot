#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для создания тестовых данных
Используется для разработки и тестирования
"""

import sys
import os
from datetime import date, datetime, timedelta

# Добавляем корневую папку в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import SessionLocal
from crud.user_crud import create_user
from crud.record_crud import create_or_update_record
from utils.calculations import calculate_bodyfat_precise, calculate_comprehensive_metrics

def create_test_users():
    """Создание тестовых пользователей"""
    db = SessionLocal()
    
    # Тестовые пользователи
    test_users = [
        {
            'telegram_id': 123456789,
            'username': 'test_user_1',
            'first_name': 'Анна',
            'last_name': 'Иванова',
            'sex': 'female',
            'date_of_birth': date(1995, 5, 15)
        },
        {
            'telegram_id': 987654321,
            'username': 'test_user_2',
            'first_name': 'Михаил',
            'last_name': 'Петров',
            'sex': 'male',
            'date_of_birth': date(1990, 8, 22)
        },
        {
            'telegram_id': 555666777,
            'username': 'test_athlete',
            'first_name': 'Елена',
            'last_name': 'Спортсменка',
            'sex': 'female',
            'date_of_birth': date(1992, 3, 10)
        }
    ]
    
    created_users = []
    for user_data in test_users:
        user = create_user(
            db,
            user_data['telegram_id'],
            user_data['username'],
            user_data['first_name'],
            user_data['last_name'],
            user_data['sex'],
            user_data['date_of_birth']
        )
        if user:
            created_users.append(user)
            print(f"✅ Создан пользователь: {user.first_name} {user.last_name}")
        else:
            print(f"❌ Ошибка создания пользователя: {user_data['first_name']}")
    
    db.close()
    return created_users

def create_test_records():
    """Создание тестовых записей измерений"""
    db = SessionLocal()
    
    # Тестовые данные для разных типов пользователей
    test_records = [
        # Обычная женщина
        {
            'telegram_id': 123456789,
            'weight': 65.0,
            'height': 165,
            'waist': 75,
            'neck': 32,
            'hip': 95,
            'chest': 85,
            'bicep': 28,
            'thigh': 55,
            'wrist': 16,
            'calf': 35,
            'forearm': 25,
            'abdomen': 78,
            'sleep_hours': 7.5,
            'stress_level': 'medium',
            'steps': '8000-10000',
            'sport_type': 'walking',
            'sport_freq': '3',
            'goal': 'healthy'
        },
        # Спортсмен
        {
            'telegram_id': 987654321,
            'weight': 80.0,
            'height': 180,
            'waist': 85,
            'neck': 40,
            'hip': None,
            'chest': 110,
            'bicep': 35,
            'thigh': 60,
            'wrist': 18,
            'calf': 40,
            'forearm': 30,
            'abdomen': 88,
            'sleep_hours': 8.0,
            'stress_level': 'low',
            'steps': '10000+',
            'sport_type': 'strength',
            'sport_freq': '5',
            'goal': 'athletic'
        },
        # Спортсменка
        {
            'telegram_id': 555666777,
            'weight': 62.0,
            'height': 175,
            'waist': 62,
            'neck': 31,
            'hip': 93,
            'chest': 85,
            'bicep': 28,
            'thigh': 55,
            'wrist': 15,
            'calf': 35,
            'forearm': 24,
            'abdomen': 65,
            'sleep_hours': 8.5,
            'stress_level': 'low',
            'steps': '10000+',
            'sport_type': 'running',
            'sport_freq': '6',
            'goal': 'lean'
        }
    ]
    
    created_records = []
    for record_data in test_records:
        # Рассчитываем процент жира
        user_data = {
            'sex': 'female' if record_data['telegram_id'] in [123456789, 555666777] else 'male',
            'height': record_data['height'],
            'weight': record_data['weight'],
            'waist': record_data['waist'],
            'neck': record_data['neck'],
            'hip': record_data['hip'],
            'chest': record_data['chest'],
            'bicep': record_data['bicep'],
            'thigh': record_data['thigh'],
            'sport_type': record_data['sport_type'],
            'sport_freq': record_data['sport_freq']
        }
        
        bodyfat = calculate_bodyfat_precise(user_data)
        comprehensive_metrics = calculate_comprehensive_metrics(user_data, bodyfat) if bodyfat else None
        
        record = create_or_update_record(
            db,
            record_data['telegram_id'],
            date.today(),
            weight=record_data['weight'],
            waist=record_data['waist'],
            neck=record_data['neck'],
            hip=record_data['hip'],
            chest=record_data['chest'],
            bicep=record_data['bicep'],
            thigh=record_data['thigh'],
            wrist=record_data['wrist'],
            calf=record_data['calf'],
            forearm=record_data['forearm'],
            abdomen=record_data['abdomen'],
            sleep_hours=record_data['sleep_hours'],
            stress_level=record_data['stress_level'],
            steps=record_data['steps'],
            sport_type=record_data['sport_type'],
            sport_freq=record_data['sport_freq'],
            step_multiplier=1.3,
            height=record_data['height'],
            goal=record_data['goal'],
            bodyfat=bodyfat,
            bmi=comprehensive_metrics['basic_metrics']['bmi'] if comprehensive_metrics else None,
            lbm=comprehensive_metrics['basic_metrics']['lbm'] if comprehensive_metrics else None,
            whr=comprehensive_metrics['basic_metrics']['whr'] if comprehensive_metrics else None,
            bmr=comprehensive_metrics['metabolic_metrics']['bmr'] if comprehensive_metrics else None,
            tdee=comprehensive_metrics['metabolic_metrics']['tdee'] if comprehensive_metrics else None,
            metabolic_age=comprehensive_metrics['metabolic_metrics']['metabolic_age'] if comprehensive_metrics else None,
            body_type=comprehensive_metrics['classifications']['body_type'] if comprehensive_metrics else None,
            bodyfat_category=comprehensive_metrics['classifications']['bodyfat_category'] if comprehensive_metrics else None
        )
        
        if record:
            created_records.append(record)
            print(f"✅ Создана запись для пользователя {record_data['telegram_id']}: вес {record_data['weight']} кг, жир {bodyfat:.1f}%")
        else:
            print(f"❌ Ошибка создания записи для пользователя {record_data['telegram_id']}")
    
    db.close()
    return created_records

def main():
    """Основная функция"""
    print("🧪 Создание тестовых данных...")
    
    try:
        # Создаем тестовых пользователей
        users = create_test_users()
        print(f"📊 Создано пользователей: {len(users)}")
        
        # Создаем тестовые записи
        records = create_test_records()
        print(f"📝 Создано записей: {len(records)}")
        
        print("✅ Тестовые данные успешно созданы!")
        print("\n📋 Созданные тестовые пользователи:")
        print("• ID 123456789 - Анна Иванова (обычная женщина)")
        print("• ID 987654321 - Михаил Петров (спортсмен)")
        print("• ID 555666777 - Елена Спортсменка (спортсменка)")
        
    except Exception as e:
        print(f"❌ Ошибка при создании тестовых данных: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
