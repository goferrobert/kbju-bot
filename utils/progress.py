import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import os
from typing import List, Dict
from models.tables import UserRecord

def select_records_for_graph(records: List[UserRecord], max_points: int = 7) -> List[UserRecord]:
    """
    Умный отбор записей для графика:
    - Всегда включает первый и последний замер
    - Максимум max_points точек
    - Если записей <= max_points, возвращает все
    - Если записей > max_points, выбирает ключевые точки
    """
    if len(records) <= max_points:
        return sorted(records, key=lambda x: x.date)
    
    # Сортируем записи по дате
    sorted_records = sorted(records, key=lambda x: x.date)
    
    # Всегда включаем первый и последний
    first_record = sorted_records[0]
    last_record = sorted_records[-1]
    
    # Если у нас только 2 записи, возвращаем их
    if len(sorted_records) == 2:
        return [first_record, last_record]
    
    # Выбираем промежуточные точки
    remaining_slots = max_points - 2  # 2 уже заняты (первый и последний)
    
    if remaining_slots <= 0:
        return [first_record, last_record]
    
    # Выбираем промежуточные записи равномерно
    middle_records = sorted_records[1:-1]  # Исключаем первый и последний
    
    if len(middle_records) <= remaining_slots:
        # Если промежуточных записей меньше или равно оставшимся слотам
        selected_middle = middle_records
    else:
        # Выбираем равномерно распределенные точки
        step = len(middle_records) / (remaining_slots + 1)
        selected_indices = [int(i * step) for i in range(1, remaining_slots + 1)]
        selected_middle = [middle_records[i] for i in selected_indices if i < len(middle_records)]
    
    # Собираем финальный список
    result = [first_record] + selected_middle + [last_record]
    
    # Убираем дубликаты и сортируем
    unique_records = []
    seen_dates = set()
    for record in result:
        if record.date not in seen_dates:
            unique_records.append(record)
            seen_dates.add(record.date)
    
    return sorted(unique_records, key=lambda x: x.date)

def get_motivational_message(records) -> str:
    """
    Генерирует мотивационное сообщение на основе прогресса пользователя
    """
    if len(records) < 2:
        return "📊 Пока недостаточно данных для анализа прогресса. Продолжай вносить замеры!"
    
    # Сортируем записи по дате (старые -> новые)
    sorted_records = sorted(records, key=lambda x: x.date)
    
    first_record = sorted_records[0]  # Самая старая запись
    last_record = sorted_records[-1]  # Самая новая запись
    
    weight_change = last_record.weight - first_record.weight
    days_between = (last_record.date - first_record.date).days
    
    # Рассчитываем изменения обмеров
    waist_change = last_record.waist - first_record.waist if last_record.waist and first_record.waist else 0
    neck_change = last_record.neck - first_record.neck if last_record.neck and first_record.neck else 0
    
    # Форматируем даты для отображения
    start_date = first_record.date.strftime('%d.%m.%Y')
    end_date = last_record.date.strftime('%d.%m.%Y')
    
    # Генерируем мотивационное сообщение
    if weight_change < -2:  # Сброс веса
        if days_between <= 30:
            return f"🎉 **Отличный результат!**\n\nЗа {days_between} дней ты сбросил {abs(weight_change):.1f} кг!\n\nПериод: {start_date} - {end_date}\n\nПродолжай в том же духе! 💪"
        elif days_between <= 90:
            return f"🔥 **Потрясающий прогресс!**\n\nЗа {days_between} дней ты сбросил {abs(weight_change):.1f} кг!\n\nПериод: {start_date} - {end_date}\n\nТы на правильном пути! 🚀"
        else:
            return f"🌟 **Невероятный результат!**\n\nЗа {days_between} дней ты сбросил {abs(weight_change):.1f} кг!\n\nПериод: {start_date} - {end_date}\n\nТы настоящий герой! 👑"
    
    elif weight_change > 2:  # Набор веса
        if days_between <= 30:
            return f"💪 **Хорошая работа!**\n\nЗа {days_between} дней ты набрал {weight_change:.1f} кг!\n\nПериод: {start_date} - {end_date}\n\nНаращиваешь мышцы! 🏋️"
        elif days_between <= 90:
            return f"🏋️ **Отличный прогресс!**\n\nЗа {days_between} дней ты набрал {weight_change:.1f} кг!\n\nПериод: {start_date} - {end_date}\n\nСтановишься сильнее! 💪"
        else:
            return f"🎯 **Потрясающие результаты!**\n\nЗа {days_between} дней ты набрал {weight_change:.1f} кг!\n\nПериод: {start_date} - {end_date}\n\nТы настоящий атлет! 🏆"
    
    else:  # Стабильный вес
        if waist_change < -3 or neck_change < -2:
            return f"🎯 **Отличная работа!**\n\nВес стабилен, но обмеры уменьшились!\n\nПериод: {start_date} - {end_date}\n\nТы теряешь жир и наращиваешь мышцы! 💪"
        else:
            return f"✅ **Стабильный прогресс!**\n\nТвой вес стабилен уже {days_between} дней.\n\nПериод: {start_date} - {end_date}\n\nПродолжай поддерживать здоровый образ жизни! 🌟"

def create_progress_graph(records) -> str:
    """
    Создает простой и понятный график прогресса на основе записей пользователя
    Возвращает путь к сохраненному файлу
    """
    if len(records) < 2:
        return None
    
    # Используем умный отбор записей для графика
    selected_records = select_records_for_graph(records, max_points=7)
    
    # Подготавливаем данные
    dates = [record.date for record in selected_records]
    weights = [record.weight for record in selected_records]
    
    # Создаем график с увеличенным размером для мобильных устройств
    plt.figure(figsize=(14, 8))
    
    # График веса
    plt.plot(dates, weights, 'b-o', linewidth=4, markersize=12, markerfacecolor='white', markeredgewidth=3, markeredgecolor='blue')
    plt.title('Ваш прогресс веса', fontsize=20, fontweight='bold', pad=25)
    plt.ylabel('Вес (кг)', fontsize=16, fontweight='bold')
    plt.xlabel('', fontsize=16, fontweight='bold')  # Убираем подпись оси X
    plt.grid(True, alpha=0.3, linestyle='--')
    
    # Убираем все метки с оси X
    plt.xticks([])
    
    # Добавляем точки с крупными подписями веса и маленькими датами
    for i, (date, weight) in enumerate(zip(dates, weights)):
        # Форматируем дату в стиле DD.MM.YY
        date_str = date.strftime('%d.%m.%y')
        
        # Подпись веса (крупная)
        plt.annotate(f'{weight:.1f} кг', (date, weight), 
                    textcoords="offset points", 
                    xytext=(0,20), 
                    ha='center', 
                    fontsize=14,
                    fontweight='bold',
                    bbox=dict(boxstyle="round,pad=0.5", facecolor="white", alpha=0.9, edgecolor="blue", linewidth=2))
        
        # Маленькая дата под значением веса
        plt.annotate(date_str, (date, weight), 
                    textcoords="offset points", 
                    xytext=(0,-35), 
                    ha='center', 
                    fontsize=10,
                    fontweight='normal',
                    color='gray')
    
    # Настраиваем отступы для лучшего отображения на мобильных
    plt.tight_layout(pad=2.0)
    
    # Создаем папку data, если её нет
    os.makedirs('data', exist_ok=True)
    
    # Сохраняем график с высоким разрешением для мобильных устройств
    filename = f'progress_graph_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
    filepath = os.path.join('data', filename)
    
    plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return filepath

def calculate_progress_changes(records):
    """
    Рассчитывает изменения между первой и последней записью
    """
    if len(records) < 2:
        return {
            'weight_change': 0,
            'bodyfat_change': 0,
            'measurements_change': {}
        }
    
    # Сортируем записи по дате (старые -> новые)
    sorted_records = sorted(records, key=lambda x: x.date)
    first_record = sorted_records[0]  # Самая старая запись
    last_record = sorted_records[-1]  # Самая новая запись
    
    weight_change = last_record.weight - first_record.weight
    bodyfat_change = (last_record.bodyfat or 0) - (first_record.bodyfat or 0)
    
    measurements_change = {
        'Талия': last_record.waist - first_record.waist,
        'Шея': last_record.neck - first_record.neck
    }
    
    if last_record.hip and first_record.hip:
        measurements_change['Бёдра'] = last_record.hip - first_record.hip
    
    return {
        'weight_change': weight_change,
        'bodyfat_change': bodyfat_change,
        'measurements_change': measurements_change
    } 