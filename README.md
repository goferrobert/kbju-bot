# 🤖 KBJU Bot - Telegram Bot для отслеживания прогресса

> **Версия:** DEV (Development)  
> **Статус:** Активная разработка  
> **Архитектура:** aiogram 2.x

## 📋 Описание

Telegram бот для отслеживания прогресса в фитнесе и питании. Помогает пользователям вести дневник измерений, рассчитывать КБЖУ, отслеживать прогресс и мотивировать к достижению целей.

## 🏗️ Архитектура

### Текущая версия (DEV)
- **Фреймворк:** aiogram 2.x
- **База данных:** SQLite (kbju_bot.db)
- **Язык:** Python 3.10+
- **Статус:** Активная разработка

### Планируемая версия (PROD)
- **Фреймворк:** python-telegram-bot 20.x
- **База данных:** PostgreSQL
- **Деплой:** Docker + Cloud
- **Статус:** В разработке

## 🚀 Быстрый старт

### Требования
- Python 3.10+
- Git
- Telegram Bot Token

### Установка

1. **Клонируйте репозиторий:**
```bash
git clone https://github.com/goferrobert/kbju-bot.git
cd kbju-bot
```

2. **Создайте виртуальное окружение:**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

3. **Установите зависимости:**
```bash
pip install -r requirements.txt
```

4. **Настройте переменные окружения:**
```bash
# Создайте файл .env
BOT_TOKEN=ваш_токен_бота
```

5. **Запустите бота:**
```bash
python main.py
```

## 📁 Структура проекта

```
Telegram/
├── 📁 handlers/          # Обработчики бота
│   ├── start_handlers.py      # Стартовые команды
│   ├── user_info_handlers.py  # Регистрация пользователей
│   ├── menu_handlers.py       # Главное меню
│   ├── measurements_handlers.py # Новые замеры
│   ├── food_handlers.py       # Предпочтения в еде
│   └── goal_handlers.py       # Цели и КБЖУ
├── 📁 utils/            # Утилиты
│   ├── calculations.py        # Расчеты (КБЖУ, жир)
│   ├── validators.py         # Валидация данных
│   ├── buttons.py            # Кнопки интерфейса
│   ├── texts.py              # Тексты сообщений
│   └── progress.py           # Графики прогресса
├── 📁 crud/             # Операции с БД
│   ├── user_crud.py          # Пользователи
│   ├── record_crud.py        # Записи измерений
│   └── food_crud.py          # Предпочтения в еде
├── 📁 models/           # Модели данных
│   ├── database.py           # Настройки БД
│   └── tables.py             # Таблицы SQLAlchemy
├── 📁 states/           # Состояния FSM
│   └── fsm_states.py        # Определения состояний
├── 📁 scripts/          # Полезные скрипты
│   ├── create_test_data.py   # Создание тестовых данных
│   └── clear_test_data.py    # Очистка тестовых данных
├── 📁 data/             # Данные (графики)
├── 📄 main.py           # Главный файл бота
├── 📄 config.py         # Конфигурация
├── 📄 requirements.txt  # Зависимости
└── 📄 .env              # Переменные окружения
```

## 🎯 Основные функции

### ✅ Реализованные функции
- **Регистрация пользователей** - сбор анкетных данных
- **Новые замеры** - добавление измерений
- **Прогресс** - графики и анализ изменений
- **КБЖУ расчеты** - автоматический расчет калорий
- **Цели** - постановка и отслеживание целей
- **Предпочтения в еде** - настройка диеты

### 🔄 В разработке
- **Уведомления** - напоминания о замерах
- **Статистика** - детальная аналитика
- **Экспорт данных** - выгрузка отчетов
- **Интеграции** - связь с фитнес-трекерами

## 🗄️ База данных

### Таблицы
- **users** - информация о пользователях
- **user_records** - записи измерений
- **user_food_preferences** - предпочтения в еде

### Схема данных
```sql
-- Пользователи
users (
    telegram_id INTEGER PRIMARY KEY,
    username VARCHAR,
    first_name VARCHAR,
    last_name VARCHAR,
    sex VARCHAR,
    date_of_birth DATE,
    created_at DATETIME
)

-- Записи измерений
user_records (
    id INTEGER PRIMARY KEY,
    telegram_id INTEGER,
    date DATE,
    weight FLOAT,
    waist FLOAT,
    neck FLOAT,
    hip FLOAT,
    height INTEGER,
    goal VARCHAR,
    steps VARCHAR,
    sport_type VARCHAR,
    sport_freq VARCHAR,
    step_multiplier FLOAT,
    bodyfat FLOAT
)
```

## 🔧 Конфигурация

### Переменные окружения
```bash
# .env
BOT_TOKEN=ваш_токен_бота
```

### Настройки логирования
- **Файл:** `bot.log`
- **Уровень:** INFO
- **Формат:** Время - Модуль - Уровень - Сообщение

## 🛠️ Разработка

### Команды для разработки
```bash
# Запуск бота
python main.py

# Создание тестовых данных
python scripts/create_test_data.py

# Очистка тестовых данных
python scripts/clear_test_data.py

# Очистка БД
clear_db_simple.bat
```

### Ветки Git
- **main** - стабильная версия
- **dev** - активная разработка (текущая)

## 📊 Мониторинг

### Логи
- **Файл:** `bot.log`
- **Ротация:** Автоматическая
- **Уровни:** INFO, WARNING, ERROR

### Метрики
- Количество активных пользователей
- Частота использования функций
- Ошибки и исключения

## 🚀 Деплой

### DEV версия (текущая)
- **Платформа:** Локальный сервер
- **База данных:** SQLite
- **Запуск:** `python main.py`

### PROD версия (планируется)
- **Платформа:** Docker + Cloud
- **База данных:** PostgreSQL
- **Мониторинг:** Prometheus + Grafana
- **Логи:** ELK Stack

## 📝 Документация

- **[SETUP.md](SETUP.md)** - Подробная инструкция по установке
- **[SCENARIOS.md](SCENARIOS.md)** - Описание сценариев использования
- **[CLEANUP_REPORT.md](CLEANUP_REPORT.md)** - Отчет об очистке проекта

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции
3. Внесите изменения
4. Создайте Pull Request

## 📄 Лицензия

MIT License - см. файл [LICENSE](LICENSE)

## 📞 Поддержка

- **Issues:** [GitHub Issues](https://github.com/goferrobert/kbju-bot/issues)
- **Discussions:** [GitHub Discussions](https://github.com/goferrobert/kbju-bot/discussions)

---

**Версия:** DEV v1.0.0  
**Последнее обновление:** 28.07.2025  
**Статус:** Активная разработка 