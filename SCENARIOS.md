# 📋 Сценарии работы бота

## 🎯 **Общая архитектура**

Проект использует **единую архитектуру aiogram 2.x** с базой данных SQLite.

## 📊 **Структура базы данных**

### Таблица `users`:
- `telegram_id` (Primary Key) - ID пользователя в Telegram
- `username` - username пользователя
- `first_name` - имя пользователя
- `last_name` - фамилия пользователя
- `sex` - пол ('male' / 'female')
- `date_of_birth` - дата рождения
- `created_at` - дата создания записи

### Таблица `user_records`:
- `id` (Primary Key) - уникальный ID записи
- `telegram_id` (Foreign Key) - ссылка на пользователя
- `date` - дата записи
- `weight` - вес (кг)
- `waist` - обхват талии (см)
- `neck` - обхват шеи (см)
- `hip` - обхват бедер (см, только для женщин)
- `height` - рост (см)
- `goal` - цель ('maintain', 'weight_loss', 'weight_gain')
- `steps` - уровень активности (строка)
- `sport_type` - тип спорта
- `sport_freq` - частота тренировок
- `step_multiplier` - множитель активности
- `bodyfat` - процент жира

## 🔄 **Сценарий "Первое касание"**

**Файл:** `handlers/start_handlers.py`

### Процесс:
1. **Проверка существования пользователя**
   - Если пользователь уже существует → показываем главное меню
   - Если пользователя нет → начинаем регистрацию

2. **Сбор данных пользователя:**
   - Имя
   - Дата рождения
   - Пол
   - Рост
   - Вес
   - Обхват талии
   - Обхват шеи
   - Обхват бедер (только для женщин)
   - Уровень активности (шаги)
   - Тип спорта
   - Частота тренировок
   - Цель

3. **Сохранение в БД:**
   ```python
   # Создаем пользователя
   user = User(
       telegram_id=message.from_user.id,
       username=message.from_user.username,
       first_name=name,
       sex=sex,
       date_of_birth=birth_date,
       height=height
   )
   db.add(user)
   db.commit()
   
   # Создаем первую запись
   record = UserRecord(
       telegram_id=message.from_user.id,
       date=date.today(),
       weight=weight,
       waist=waist,
       neck=neck,
       hip=hip,
       height=height,
       goal=goal,
       steps=steps,
       sport_type=sport_type,
       sport_freq=sport_freq
   )
   db.add(record)
   db.commit()
   ```

## 📝 **Сценарий "Новые замеры"**

**Файл:** `handlers/measurements_handlers.py`

### Процесс:
1. **Проверка существования пользователя**
   - Если пользователя нет → показываем ошибку
   - Если пользователь есть → начинаем измерения

2. **Сбор новых данных:**
   - Обхват талии
   - Обхват шеи
   - Обхват бедер (только для женщин)
   - Вес
   - Уровень активности (шаги)
   - Тип спорта
   - Частота тренировок

3. **Сохранение в БД:**
   ```python
   # Используем create_or_update_record для умного сохранения
   create_or_update_record(
       db,
       message.from_user.id,
       date.today(),
       weight=weight,
       waist=waist,
       neck=neck,
       hip=hip,
       steps=steps,
       sport_type=sport_type,
       sport_freq=sport_freq,
       step_multiplier=step_multiplier,
       height=latest_record.height,  # Берем из последней записи
       goal=latest_record.goal       # Берем из последней записи
   )
   ```

## 🔄 **Логика create_or_update_record**

```python
def create_or_update_record(db: Session, telegram_id: int, record_date: date, **kwargs):
    # Проверяем, есть ли запись на эту дату
    existing_record = db.query(UserRecord).filter(
        and_(UserRecord.telegram_id == telegram_id, UserRecord.date == record_date)
    ).first()
    
    if existing_record:
        # UPDATE если ввод в тот же день
        for key, value in kwargs.items():
            if hasattr(existing_record, key) and value is not None:
                setattr(existing_record, key, value)
        db.commit()
        return existing_record
    else:
        # INSERT если ввод в другой день
        new_record = UserRecord(
            telegram_id=telegram_id,
            date=record_date,
            **filtered_kwargs
        )
        db.add(new_record)
        db.commit()
        return new_record
```

## ✅ **Совместимость сценариев**

### **Что одинаково:**
- ✅ Оба используют **одну базу данных**
- ✅ Оба используют **одни модели** (`models/tables.py`)
- ✅ Оба используют **одну архитектуру** (aiogram 2.x)
- ✅ Оба сохраняют данные в таблицу `user_records`
- ✅ Оба используют поле `telegram_id` для связи

### **Что различается:**
- 🔄 **Первое касание** создает нового пользователя + первую запись
- 🔄 **Новые замеры** создают только новую запись для существующего пользователя
- 🔄 **Первое касание** собирает полную анкету
- 🔄 **Новые замеры** собирают только измерения

## 🛡️ **Защита от конфликтов**

1. **Проверка существования пользователя** перед началом измерений
2. **Умное сохранение** - обновление записи за тот же день или создание новой
3. **Валидация данных** на каждом этапе
4. **Обработка ошибок** с понятными сообщениями

## 📈 **Результат**

Оба сценария работают **совместимо** и **не конфликтуют** в базе данных:
- Первое касание создает пользователя и первую запись
- Новые замеры добавляют записи к существующему пользователю
- Все данные сохраняются в одной структуре
- Прогресс рассчитывается на основе всех записей пользователя 