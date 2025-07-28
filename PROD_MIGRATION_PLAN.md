# 🚀 План миграции на PROD версию

> **Статус:** Планирование  
> **Дата создания:** 28.07.2025  
> **Цель:** Подготовка к продакшен версии

## 📋 Обзор

Данный документ описывает план миграции KBJU Bot с DEV версии (aiogram 2.x + SQLite) на PROD версию (python-telegram-bot 20.x + PostgreSQL + Docker).

## 🎯 Цели миграции

### Основные цели
- ✅ **Масштабируемость** - поддержка большого количества пользователей
- ✅ **Надежность** - стабильная работа 24/7
- ✅ **Мониторинг** - детальная аналитика и алерты
- ✅ **Безопасность** - защита данных и токенов
- ✅ **Производительность** - быстрый отклик бота

### Технические цели
- 🔄 **Фреймворк:** aiogram 2.x → python-telegram-bot 20.x
- 🗄️ **База данных:** SQLite → PostgreSQL
- 🐳 **Деплой:** Локальный сервер → Docker + Cloud
- 📊 **Мониторинг:** Логи → Prometheus + Grafana
- 🔒 **Безопасность:** Базовые настройки → Полная защита

## 🏗️ Архитектурные изменения

### Текущая архитектура (DEV)
```
┌─────────────────┐    ┌──────────────┐    ┌─────────────┐
│   Telegram API  │    │   aiogram    │    │   SQLite    │
│                 │◄──►│    2.x       │◄──►│   Database  │
└─────────────────┘    └──────────────┘    └─────────────┘
                              │
                              ▼
                       ┌──────────────┐
                       │ Local Server │
                       └──────────────┘
```

### Целевая архитектура (PROD)
```
┌─────────────────┐    ┌──────────────────┐    ┌──────────────┐
│   Telegram API  │    │ python-telegram  │    │ PostgreSQL   │
│                 │◄──►│      bot 20.x    │◄──►│   Database   │
└─────────────────┘    └──────────────────┘    └──────────────┘
                              │
                              ▼
                       ┌──────────────┐    ┌──────────────┐
                       │   Docker     │    │   Cloud      │
                       │  Container   │◄──►│   Platform   │
                       └──────────────┘    └──────────────┘
                              │
                              ▼
                       ┌──────────────┐    ┌──────────────┐
                       │ Prometheus   │    │   Grafana    │
                       │ Monitoring   │◄──►│   Dashboard  │
                       └──────────────┘    └──────────────┘
```

## 📅 План миграции

### Этап 1: Подготовка (1-2 недели)
- [ ] **Анализ текущего кода**
  - [ ] Документирование всех функций
  - [ ] Выявление критических зависимостей
  - [ ] Анализ производительности

- [ ] **Создание PROD репозитория**
  - [ ] Создание нового репозитория `kbju-bot-prod`
  - [ ] Настройка веток (main, staging, develop)
  - [ ] Настройка CI/CD пайплайна

- [ ] **Подготовка инфраструктуры**
  - [ ] Выбор облачной платформы (AWS/GCP/Azure)
  - [ ] Настройка PostgreSQL сервера
  - [ ] Настройка Docker окружения

### Этап 2: Миграция кода (2-3 недели)
- [ ] **Миграция фреймворка**
  - [ ] Установка python-telegram-bot 20.x
  - [ ] Переписывание обработчиков
  - [ ] Адаптация состояний FSM
  - [ ] Обновление утилит

- [ ] **Миграция базы данных**
  - [ ] Создание схемы PostgreSQL
  - [ ] Написание миграций
  - [ ] Создание индексов
  - [ ] Настройка бэкапов

- [ ] **Docker контейнеризация**
  - [ ] Создание Dockerfile
  - [ ] Настройка docker-compose
  - [ ] Оптимизация образа
  - [ ] Настройка переменных окружения

### Этап 3: Тестирование (1-2 недели)
- [ ] **Модульные тесты**
  - [ ] Тесты обработчиков
  - [ ] Тесты утилит
  - [ ] Тесты CRUD операций
  - [ ] Тесты валидации

- [ ] **Интеграционные тесты**
  - [ ] Тесты API Telegram
  - [ ] Тесты базы данных
  - [ ] Тесты мониторинга
  - [ ] Нагрузочные тесты

- [ ] **Пользовательские тесты**
  - [ ] Тестирование всех сценариев
  - [ ] Проверка совместимости данных
  - [ ] Тестирование производительности

### Этап 4: Деплой (1 неделя)
- [ ] **Настройка CI/CD**
  - [ ] GitHub Actions пайплайн
  - [ ] Автоматическое тестирование
  - [ ] Автоматический деплой
  - [ ] Откат изменений

- [ ] **Мониторинг и логирование**
  - [ ] Настройка Prometheus
  - [ ] Настройка Grafana дашбордов
  - [ ] Настройка алертов
  - [ ] Централизованное логирование

- [ ] **Безопасность**
  - [ ] Настройка SSL/TLS
  - [ ] Настройка файрвола
  - [ ] Шифрование данных
  - [ ] Аудит безопасности

### Этап 5: Запуск (1 неделя)
- [ ] **Пилотный запуск**
  - [ ] Деплой на staging окружении
  - [ ] Тестирование с ограниченной аудиторией
  - [ ] Сбор обратной связи
  - [ ] Исправление проблем

- [ ] **Полный запуск**
  - [ ] Деплой на production
  - [ ] Мониторинг производительности
  - [ ] Настройка алертов
  - [ ] Документирование процедур

## 🔧 Технические детали

### Миграция фреймворка

#### aiogram 2.x → python-telegram-bot 20.x
```python
# Старый код (aiogram 2.x)
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer("Привет!")

# Новый код (python-telegram-bot 20.x)
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram import Update

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет!")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start_command))
```

### Миграция базы данных

#### SQLite → PostgreSQL
```sql
-- Создание таблиц в PostgreSQL
CREATE TABLE users (
    telegram_id BIGINT PRIMARY KEY,
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    sex VARCHAR(10),
    date_of_birth DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_records (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT REFERENCES users(telegram_id),
    date DATE NOT NULL,
    weight DECIMAL(5,2),
    waist DECIMAL(5,2),
    neck DECIMAL(5,2),
    hip DECIMAL(5,2),
    height INTEGER,
    goal VARCHAR(50),
    steps VARCHAR(50),
    sport_type VARCHAR(50),
    sport_freq VARCHAR(50),
    step_multiplier DECIMAL(3,2),
    bodyfat DECIMAL(4,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для производительности
CREATE INDEX idx_user_records_telegram_id ON user_records(telegram_id);
CREATE INDEX idx_user_records_date ON user_records(date);
CREATE INDEX idx_user_records_telegram_date ON user_records(telegram_id, date);
```

### Docker контейнеризация

#### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копирование зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY . .

# Создание пользователя для безопасности
RUN useradd -m -u 1000 botuser && chown -R botuser:botuser /app
USER botuser

# Запуск приложения
CMD ["python", "main.py"]
```

#### docker-compose.yml
```yaml
version: '3.8'

services:
  bot:
    build: .
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
      - DATABASE_URL=${DATABASE_URL}
      - LOG_LEVEL=${LOG_LEVEL}
    depends_on:
      - postgres
    restart: unless-stopped

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=kbju_bot
      - POSTGRES_USER=botuser
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    restart: unless-stopped

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
    restart: unless-stopped

volumes:
  postgres_data:
  grafana_data:
```

## 📊 Мониторинг и метрики

### Prometheus метрики
```python
from prometheus_client import Counter, Histogram, Gauge

# Метрики для мониторинга
messages_total = Counter('bot_messages_total', 'Total messages processed')
commands_total = Counter('bot_commands_total', 'Total commands processed', ['command'])
response_time = Histogram('bot_response_time_seconds', 'Response time in seconds')
active_users = Gauge('bot_active_users', 'Number of active users')
```

### Grafana дашборды
- **Обзор системы:** Общие метрики бота
- **Пользователи:** Активность пользователей
- **Производительность:** Время отклика и ошибки
- **База данных:** Производительность PostgreSQL

## 🔒 Безопасность

### Переменные окружения
```bash
# PROD переменные
BOT_TOKEN=prod_token_here
DATABASE_URL=postgresql://user:pass@host:port/db
LOG_LEVEL=INFO
DEBUG_MODE=false
PROMETHEUS_ENABLED=true
GRAFANA_PASSWORD=secure_password
```

### Рекомендации по безопасности
- [ ] Использование секретов в CI/CD
- [ ] Шифрование данных в базе
- [ ] Настройка файрвола
- [ ] Регулярные обновления зависимостей
- [ ] Аудит безопасности

## 📈 Производительность

### Целевые метрики
- **Время отклика:** < 1 секунды
- **Доступность:** 99.9%
- **Пользователи:** Поддержка 10,000+ пользователей
- **Запросы:** 1000+ запросов в минуту

### Оптимизации
- [ ] Кэширование данных
- [ ] Оптимизация запросов к БД
- [ ] Асинхронная обработка
- [ ] CDN для статических файлов

## 🧪 Тестирование

### Автоматические тесты
```python
import pytest
from telegram.ext import Application

@pytest.fixture
async def app():
    app = Application.builder().token("test_token").build()
    yield app
    await app.shutdown()

async def test_start_command(app):
    # Тест команды /start
    pass

async def test_user_registration(app):
    # Тест регистрации пользователя
    pass
```

### Нагрузочные тесты
- [ ] Тестирование с 1000+ пользователей
- [ ] Тестирование базы данных
- [ ] Тестирование API Telegram
- [ ] Мониторинг ресурсов

## 📝 Документация

### Обязательная документация
- [ ] **API документация** - описание всех эндпоинтов
- [ ] **Архитектурная документация** - схема системы
- [ ] **Операционная документация** - процедуры деплоя
- [ ] **Пользовательская документация** - инструкции для пользователей

### Документация для разработчиков
- [ ] **Руководство по разработке** - как добавлять новые функции
- [ ] **Руководство по тестированию** - как писать тесты
- [ ] **Руководство по деплою** - процедуры развертывания

## 🚨 Риски и митигация

### Высокие риски
1. **Потеря данных при миграции**
   - **Митигация:** Полное резервное копирование, тестирование на копии

2. **Простой сервиса**
   - **Митигация:** Поэтапная миграция, откат изменений

3. **Проблемы производительности**
   - **Митигация:** Нагрузочное тестирование, мониторинг

### Средние риски
1. **Совместимость API**
   - **Митигация:** Тщательное тестирование всех функций

2. **Проблемы безопасности**
   - **Митигация:** Аудит безопасности, шифрование данных

## 📅 Временные рамки

### Общий план
- **Подготовка:** 2 недели
- **Миграция кода:** 3 недели
- **Тестирование:** 2 недели
- **Деплой:** 1 неделя
- **Запуск:** 1 неделя

**Итого:** 9 недель

### Критические вехи
- [ ] **Неделя 2:** Завершение анализа кода
- [ ] **Неделя 5:** Завершение миграции фреймворка
- [ ] **Неделя 7:** Завершение тестирования
- [ ] **Неделя 8:** Деплой на staging
- [ ] **Неделя 9:** Запуск в production

## 📞 Команда и ответственности

### Роли в проекте
- **Технический лид:** Архитектура и планирование
- **Backend разработчик:** Миграция кода
- **DevOps инженер:** Инфраструктура и деплой
- **QA инженер:** Тестирование
- **Product Manager:** Координация и приоритизация

### Коммуникация
- **Еженедельные встречи:** Обзор прогресса
- **Ежедневные standup:** Статус задач
- **Срочные вопросы:** Slack/Telegram

---

**Статус:** Планирование  
**Следующее обновление:** Начало реализации  
**Версия:** v1.0.0 