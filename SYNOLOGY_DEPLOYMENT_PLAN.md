# 🏢 План развертывания PROD версии на Synology NAS DS925+

> **Дата создания:** 28.07.2025  
> **Цель:** Развертывание PROD версии на Synology NAS DS925+  
> **Статус:** Подготовка

## 📋 Обзор

Данный документ описывает план развертывания KBJU Bot PROD версии на Synology NAS DS925+. PROD версия будет использовать python-telegram-bot 20.x, PostgreSQL и Docker контейнеризацию.

## 🏗️ Архитектура развертывания

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

### Целевая архитектура (PROD на Synology)
```
┌─────────────────┐    ┌──────────────────┐    ┌──────────────┐
│   Telegram API  │    │ python-telegram  │    │ PostgreSQL   │
│                 │◄──►│      bot 20.x    │◄──►│   Database   │
└─────────────────┘    └──────────────────┘    └──────────────┘
                              │
                              ▼
                       ┌──────────────┐    ┌──────────────┐
                       │   Docker     │    │ Synology NAS │
                       │  Container   │◄──►│   DS925+     │
                       └──────────────┘    └──────────────┘
                              │
                              ▼
                       ┌──────────────┐    ┌──────────────┐
                       │ Prometheus   │    │   Grafana    │
                       │ Monitoring   │◄──►│   Dashboard  │
                       └──────────────┘    └──────────────┘
```

## 🔑 Токены и конфигурация

### Токены ботов
```bash
# DEV токен (локальный)
DEV_BOT_TOKEN=7718052021:AAF9UoJN-ZlHivpgq0Gk_ZRw949ujCGnPPk

# PROD токен (Synology NAS)
PROD_BOT_TOKEN=7743151696:AAGbt8nOrUxD3ZZt3UkAzCX28J_u8Gl_VWQ
```

### Переменные окружения PROD
```bash
# PROD переменные для Synology
BOT_TOKEN=7743151696:AAGbt8nOrUxD3ZZt3UkAzCX28J_u8Gl_VWQ
DATABASE_URL=postgresql://kbju_user:secure_password@localhost:5432/kbju_bot
LOG_LEVEL=INFO
DEBUG_MODE=false
PROMETHEUS_ENABLED=true
GRAFANA_PASSWORD=secure_password
SYNOLOGY_MODE=true
```

## 🖥️ Требования к Synology NAS DS925+

### Аппаратные характеристики
- **Процессор:** AMD Ryzen R1600 (2 ядра, 2.6 ГГц)
- **Память:** 4 ГБ DDR4 (расширяемо до 32 ГБ)
- **Хранилище:** 4 отсека для дисков (до 64 ТБ)
- **Сеть:** 2 порта Gigabit Ethernet
- **USB:** 2 порта USB 3.2 Gen 1

### Программные требования
- **DSM:** 7.2 или выше
- **Docker:** Установлен через Package Center
- **PostgreSQL:** Контейнер или пакет
- **Git:** Для развертывания кода

## 📦 Подготовка Synology NAS

### 1. Установка необходимых пакетов
```bash
# Через Package Center установить:
- Docker
- Git Server (опционально)
- PostgreSQL (опционально, можно использовать контейнер)
```

### 2. Настройка Docker
```bash
# Включить Docker в DSM
# Настроить права доступа
# Создать пользователя для приложения
```

### 3. Настройка сети
```bash
# Открыть порты:
- 5432 (PostgreSQL)
- 9090 (Prometheus)
- 3000 (Grafana)
- 8080 (Приложение, опционально)
```

## 🐳 Docker контейнеризация для Synology

### Dockerfile для PROD
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копирование зависимостей
COPY requirements_prod.txt .
RUN pip install --no-cache-dir -r requirements_prod.txt

# Копирование кода
COPY . .

# Создание пользователя для безопасности
RUN useradd -m -u 1000 botuser && chown -R botuser:botuser /app
USER botuser

# Проверка здоровья
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python health_check.py

# Запуск приложения
CMD ["python", "main_prod.py"]
```

### docker-compose.yml для Synology
```yaml
version: '3.8'

services:
  kbju-bot:
    build: .
    container_name: kbju-bot-prod
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
      - DATABASE_URL=${DATABASE_URL}
      - LOG_LEVEL=${LOG_LEVEL}
      - SYNOLOGY_MODE=true
    depends_on:
      - postgres
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    networks:
      - kbju-network

  postgres:
    image: postgres:15
    container_name: kbju-postgres
    environment:
      - POSTGRES_DB=kbju_bot
      - POSTGRES_USER=kbju_user
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d
    restart: unless-stopped
    networks:
      - kbju-network

  prometheus:
    image: prom/prometheus
    container_name: kbju-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    restart: unless-stopped
    networks:
      - kbju-network

  grafana:
    image: grafana/grafana
    container_name: kbju-grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana:/etc/grafana/provisioning
    restart: unless-stopped
    networks:
      - kbju-network

  nginx:
    image: nginx:alpine
    container_name: kbju-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - kbju-bot
    restart: unless-stopped
    networks:
      - kbju-network

volumes:
  postgres_data:
  prometheus_data:
  grafana_data:

networks:
  kbju-network:
    driver: bridge
```

## 📁 Структура PROD проекта

```
kbju-bot-prod/
├── 📁 app/                 # Основное приложение
│   ├── main_prod.py        # Главный файл PROD версии
│   ├── handlers/           # Обработчики
│   ├── utils/             # Утилиты
│   ├── crud/              # CRUD операции
│   ├── models/            # Модели данных
│   └── states/            # Состояния FSM
├── 📁 monitoring/         # Мониторинг
│   ├── prometheus.yml     # Конфигурация Prometheus
│   ├── grafana/           # Дашборды Grafana
│   └── health_check.py    # Проверка здоровья
├── 📁 nginx/              # Веб-сервер
│   ├── nginx.conf         # Конфигурация Nginx
│   └── ssl/               # SSL сертификаты
├── 📁 init-scripts/       # Скрипты инициализации БД
├── 📁 logs/               # Логи приложения
├── 📁 data/               # Данные (графики)
├── 📄 docker-compose.yml  # Docker Compose
├── 📄 Dockerfile          # Docker образ
├── 📄 requirements_prod.txt # Зависимости PROD
├── 📄 .env.prod           # Переменные окружения PROD
└── 📄 deploy.sh           # Скрипт развертывания
```

## 🔧 Конфигурация для Synology

### Nginx конфигурация
```nginx
events {
    worker_connections 1024;
}

http {
    upstream kbju_bot {
        server kbju-bot:8000;
    }

    server {
        listen 80;
        server_name your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl;
        server_name your-domain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        location / {
            proxy_pass http://kbju_bot;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /grafana {
            proxy_pass http://grafana:3000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /prometheus {
            proxy_pass http://prometheus:9090;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

### Prometheus конфигурация
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'kbju-bot'
    static_configs:
      - targets: ['kbju-bot:8000']

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
```

## 🚀 Процедура развертывания

### 1. Подготовка Synology NAS
```bash
# Установить Docker через Package Center
# Настроить права доступа
# Создать папку для проекта
mkdir /volume1/docker/kbju-bot-prod
cd /volume1/docker/kbju-bot-prod
```

### 2. Клонирование PROD репозитория
```bash
# Клонировать PROD репозиторий
git clone https://github.com/goferrobert/kbju-bot-prod.git .
```

### 3. Настройка переменных окружения
```bash
# Создать файл .env.prod
cp .env.example .env.prod
# Отредактировать переменные
nano .env.prod
```

### 4. Запуск контейнеров
```bash
# Собрать и запустить контейнеры
docker-compose up -d --build

# Проверить статус
docker-compose ps

# Просмотр логов
docker-compose logs -f kbju-bot
```

### 5. Инициализация базы данных
```bash
# Создать таблицы
docker-compose exec postgres psql -U kbju_user -d kbju_bot -f /docker-entrypoint-initdb.d/init.sql

# Проверить подключение
docker-compose exec kbju-bot python -c "from app.models.database import engine; print('DB connected')"
```

## 📊 Мониторинг и логирование

### Логирование
```python
# PROD логирование
import logging
from logging.handlers import RotatingFileHandler

# Настройка логирования для Synology
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('/app/logs/bot.log', maxBytes=10*1024*1024, backupCount=5),
        logging.StreamHandler()
    ]
)
```

### Метрики Prometheus
```python
from prometheus_client import Counter, Histogram, Gauge

# Метрики для мониторинга
messages_total = Counter('bot_messages_total', 'Total messages processed')
commands_total = Counter('bot_commands_total', 'Total commands processed', ['command'])
response_time = Histogram('bot_response_time_seconds', 'Response time in seconds')
active_users = Gauge('bot_active_users', 'Number of active users')
db_connections = Gauge('db_connections', 'Database connections')
```

## 🔒 Безопасность для Synology

### SSL сертификаты
```bash
# Получить SSL сертификат (Let's Encrypt)
certbot certonly --standalone -d your-domain.com

# Скопировать сертификаты
cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ./nginx/ssl/cert.pem
cp /etc/letsencrypt/live/your-domain.com/privkey.pem ./nginx/ssl/key.pem
```

### Брандмауэр
```bash
# Настроить брандмауэр Synology
# Открыть только необходимые порты:
# - 80 (HTTP)
# - 443 (HTTPS)
# - 22 (SSH, опционально)
```

### Резервное копирование
```bash
# Автоматическое резервное копирование
# Настроить через Hyper Backup
# Резервировать:
# - База данных PostgreSQL
# - Логи приложения
# - Конфигурационные файлы
```

## 📈 Производительность для Synology

### Оптимизация ресурсов
```yaml
# Ограничения ресурсов в docker-compose.yml
services:
  kbju-bot:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### Мониторинг ресурсов
```bash
# Проверка использования ресурсов
docker stats

# Мониторинг дискового пространства
df -h /volume1/docker/kbju-bot-prod

# Мониторинг памяти
free -h
```

## 🔄 Процедуры обновления

### Автоматическое обновление
```bash
#!/bin/bash
# deploy.sh - Скрипт автоматического развертывания

echo "Starting deployment..."

# Остановить контейнеры
docker-compose down

# Получить последние изменения
git pull origin main

# Пересобрать образы
docker-compose build --no-cache

# Запустить контейнеры
docker-compose up -d

# Проверить статус
docker-compose ps

echo "Deployment completed!"
```

### Откат изменений
```bash
# Откат к предыдущей версии
git checkout HEAD~1
docker-compose down
docker-compose up -d --build
```

## 📞 Поддержка и мониторинг

### Алерты
```python
# Настройка алертов в Grafana
# - Высокое использование CPU/памяти
# - Ошибки в логах
# - Недоступность сервисов
# - Проблемы с базой данных
```

### Логирование ошибок
```python
# Отправка ошибок в систему мониторинга
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[LoggingIntegration(level=logging.INFO, event_level=logging.ERROR)]
)
```

## 📅 План реализации

### Этап 1: Подготовка (1 неделя)
- [ ] Настройка Synology NAS
- [ ] Установка Docker и зависимостей
- [ ] Создание PROD репозитория
- [ ] Подготовка конфигурационных файлов

### Этап 2: Развертывание (1 неделя)
- [ ] Развертывание контейнеров
- [ ] Настройка базы данных
- [ ] Настройка мониторинга
- [ ] Тестирование функциональности

### Этап 3: Оптимизация (1 неделя)
- [ ] Настройка производительности
- [ ] Настройка безопасности
- [ ] Настройка резервного копирования
- [ ] Документирование процедур

### Этап 4: Запуск (1 неделя)
- [ ] Финальное тестирование
- [ ] Настройка алертов
- [ ] Обучение команды
- [ ] Запуск в продакшен

## 🎯 Целевые метрики

### Производительность
- **Время отклика:** < 1 секунды
- **Доступность:** 99.9%
- **Пользователи:** 10,000+
- **Запросы в минуту:** 1000+

### Ресурсы Synology
- **CPU:** До 80% нагрузки
- **Память:** До 3 ГБ из 4 ГБ
- **Дисковое пространство:** До 80% от доступного
- **Сеть:** До 100 Мбит/с

---

**Статус:** Подготовка к развертыванию  
**Следующий этап:** Настройка Synology NAS  
**Версия:** PROD v1.0.0 (планируется) 